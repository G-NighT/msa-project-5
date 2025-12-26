package com.example.batchprocessing.api;

import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.MDC;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/jobs")
public class JobController {

  private final JobLauncher jobLauncher;
  private final Job importProductJob;

  public JobController(JobLauncher jobLauncher, Job importProductJob) {
    this.jobLauncher = jobLauncher;
    this.importProductJob = importProductJob;
  }

  @PostMapping("/import-products")
  public ResponseEntity<?> runImportProducts(HttpServletRequest request) throws Exception {
    // пишем URI в MDC, чтобы улетело в логи вместе с traceId/spanId
    MDC.put("uri", request.getRequestURI());
    try {
      JobParameters params = new JobParametersBuilder()
          // параметр обязателен, иначе Spring Batch сочтёт job уже выполнявшейся
          .addLong("requestTime", System.currentTimeMillis())
          .toJobParameters();

      JobExecution exec = jobLauncher.run(importProductJob, params);

      return ResponseEntity.ok(Map.of(
          "jobExecutionId", exec.getId(),
          "status", exec.getStatus().toString()));
    } finally {
      MDC.remove("uri");
    }
  }
}
