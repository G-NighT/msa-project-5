import os
import datetime
import psycopg2

PGHOST = os.getenv("PGHOST", "postgres")
PGPORT = int(os.getenv("PGPORT", "5432"))
PGDATABASE = os.getenv("PGDATABASE", "analytics")
PGUSER = os.getenv("PGUSER", "analytics")
PGPASSWORD = os.getenv("PGPASSWORD", "analytics")

TABLE_NAME = os.getenv("TABLE_NAME", "shipments")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/exports")
FILE_PREFIX = os.getenv("FILE_PREFIX", "shipments")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ds = datetime.datetime.utcnow().strftime("%Y%m%d")
    out_path = os.path.join(OUTPUT_DIR, f"{FILE_PREFIX}_{ds}.csv")

    conn = psycopg2.connect(
        host=PGHOST, port=PGPORT, dbname=PGDATABASE, user=PGUSER, password=PGPASSWORD
    )
    conn.autocommit = True

    with conn.cursor() as cur, open(out_path, "w", encoding="utf-8") as f:
        copy_sql = f"COPY {TABLE_NAME} TO STDOUT WITH (FORMAT CSV, HEADER TRUE)"
        cur.copy_expert(copy_sql, f)

    conn.close()

    size = os.path.getsize(out_path)
    print(f"Exported table '{TABLE_NAME}' to: {out_path} ({size} bytes)")
    # печать первых строк, чтобы на скрине было что-то видно
    with open(out_path, "r", encoding="utf-8") as f:
        print("---- CSV HEAD ----")
        for i in range(5):
            line = f.readline()
            if not line:
                break
            print(line.rstrip())
        print("------------------")

if __name__ == "__main__":
    main()
