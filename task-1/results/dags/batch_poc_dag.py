from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
from airflow import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


DATA_DIR = "/opt/airflow/data"
OUT_DIR = f"{DATA_DIR}/out"
os.makedirs(OUT_DIR, exist_ok=True)


default_args = {
    "owner": "marketing",
    "retries": 2,
    "retry_delay": timedelta(seconds=10),
    "retry_exponential_backoff": True,
    # email “из коробки” при ошибке/ретрае
    "email": ["marketing@example.com"],
    "email_on_failure": True,
    "email_on_retry": True,
}


def read_orders_from_postgres(**context):
    hook = PostgresHook(postgres_conn_id="postgres_default")
    # В LocalExecutor можно просто использовать pandas через fetchall + DataFrame
    rows = hook.get_records("SELECT order_id, user_id, amount, created_at FROM orders ORDER BY order_id")
    df = pd.DataFrame(rows, columns=["order_id", "user_id", "amount", "created_at"])
    context["ti"].xcom_push(key="orders_df", value=df.to_json(orient="records"))
    return f"Loaded {len(df)} orders from Postgres"


def read_delivery_csv(**context):
    path = f"{DATA_DIR}/delivery_statuses.csv"
    df = pd.read_csv(path)
    context["ti"].xcom_push(key="delivery_df", value=df.to_json(orient="records"))
    return f"Loaded {len(df)} delivery rows from CSV"


def unstable_step_fail_once():
    """
    Демонстрация retry:
    Падает один раз (создаёт marker-файл) и проходит на следующей попытке.
    """
    marker = f"{DATA_DIR}/.failed_once_marker"
    if not os.path.exists(marker):
        with open(marker, "w", encoding="utf-8") as f:
            f.write("fail once to demonstrate retry\n")
        raise RuntimeError("Intentional one-time failure to demonstrate retries")
    return "Unstable step succeeded after retry"


def analyze_and_join(**context):
    ti = context["ti"]
    orders = pd.read_json(ti.xcom_pull(key="orders_df", task_ids="read_orders"))
    delivery = pd.read_json(ti.xcom_pull(key="delivery_df", task_ids="read_delivery_csv"))

    merged = orders.merge(delivery, on="order_id", how="left")
    failed_cnt = int((merged["delivery_status"] == "FAILED").sum())

    report_path = f"{OUT_DIR}/report_{context['ds_nodash']}.csv"
    merged.to_csv(report_path, index=False)

    ti.xcom_push(key="failed_cnt", value=failed_cnt)
    ti.xcom_push(key="report_path", value=report_path)

    return {"failed_cnt": failed_cnt, "report_path": report_path}


def branch_by_failed_cnt(**context):
    failed_cnt = int(context["ti"].xcom_pull(key="failed_cnt", task_ids="analyze_and_join"))
    # Условие для ветвления (пример): если есть хотя бы 1 FAILED, идём по "alert" ветке
    return "alert_branch" if failed_cnt > 0 else "ok_branch"


with DAG(
    dag_id="batch_poc",
    description="POC batch pipeline: Postgres + CSV -> analyze -> branch -> email notifications",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule=None,  # вручную, чтобы создать скриншоты
    catchup=False,
    tags=["poc", "batch", "marketing"],
) as dag:

    start = EmptyOperator(task_id="start")

    read_orders = PythonOperator(
        task_id="read_orders",
        python_callable=read_orders_from_postgres,
    )

    read_delivery_csv = PythonOperator(
        task_id="read_delivery_csv",
        python_callable=read_delivery_csv,
    )

    unstable = PythonOperator(
        task_id="unstable_step_with_retry",
        python_callable=unstable_step_fail_once,
    )

    analyze = PythonOperator(
        task_id="analyze_and_join",
        python_callable=analyze_and_join,
    )

    branch = BranchPythonOperator(
        task_id="branch_by_failed_cnt",
        python_callable=branch_by_failed_cnt,
    )

    ok_branch = EmptyOperator(task_id="ok_branch")
    alert_branch = EmptyOperator(task_id="alert_branch")

    # Email на успех (в конце, если всё успешно)
    email_success = EmailOperator(
        task_id="email_success",
        to=["marketing@example.com"],
        subject="Airflow batch_poc: SUCCESS",
        html_content="""
        <p>DAG <b>batch_poc</b> успешно завершился.</p>
        <p>Report: {{ ti.xcom_pull(task_ids='analyze_and_join', key='report_path') }}</p>
        """,
        trigger_rule="none_failed_min_one_success",
    )

    # Email на ошибку (если упал любой таск)
    email_failure = EmailOperator(
        task_id="email_failure",
        to=["marketing@example.com"],
        subject="Airflow batch_poc: FAILED",
        html_content="""
        <p>DAG <b>batch_poc</b> завершился с ошибкой.</p>
        <p>Проверь логи в Airflow UI.</p>
        """,
        trigger_rule="one_failed",
    )

    end = EmptyOperator(task_id="end", trigger_rule="all_done")

    start >> [read_orders, read_delivery_csv] >> unstable >> analyze >> branch
    branch >> [ok_branch, alert_branch]

    ok_branch >> email_success
    alert_branch >> email_success

    ok_branch >> email_failure
    alert_branch >> email_failure

    email_success >> end
    email_failure >> end
