---
title: Structured Logging with Pino
impact: MEDIUM
impactDescription: Console.log with no structure or timing makes production issues impossible to search or correlate.
tags: logging, pino, observability, express
---

# Structured Logging with Pino

Use Pino to emit JSON-structured logs with request ID, duration, status code, and contextual fields instead of plain console.log statements.

## Bad Example

```typescript
// Unstructured console.log — no timestamp, no correlation, no log levels
app.get("/users/:id", async (req, res) => {
  console.log("Getting user " + req.params.id);
  const user = await userService.getUserById(req.params.id);
  console.log("Found user: " + JSON.stringify(user));
  res.json(user);
});

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.log("ERROR: " + err.message);
  console.log(err.stack);
  res.status(500).json({ error: "Internal error" });
});

// Output is plain text — impossible to filter, search, or aggregate:
// Getting user abc123
// Found user: {"name":"Alice"}
// ERROR: connection refused
```

## Good Example

```typescript
// middleware/logger.middleware.ts — structured request logging
import pino from "pino";
import { v4 as uuid } from "uuid";

export const logger = pino({
  level: process.env.LOG_LEVEL || "info",
});

export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const requestId = req.headers["x-request-id"]?.toString() || uuid();

  req.requestId = requestId;
  res.setHeader("X-Request-Id", requestId);

  res.on("finish", () => {
    const duration = Date.now() - start;
    logger.info({
      requestId,
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration,
      userAgent: req.headers["user-agent"],
      ip: req.ip,
    });
  });

  next();
};

// Error handler uses structured logging too
export const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error({
    requestId: req.requestId,
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
  });

  res.status(500).json({ status: "error", message: "Internal server error" });
};

// Output is machine-parseable JSON:
// {"level":30,"requestId":"abc-123","method":"GET","url":"/users/42","status":200,"duration":12}
// {"level":50,"requestId":"abc-123","error":"connection refused","stack":"...","url":"/users/42"}
```

## Why

- **Benefit**: JSON output integrates directly with log aggregators (ELK, Datadog, CloudWatch) for filtering by requestId, status, or duration without custom parsing.
- **Benefit**: Request ID correlation lets you trace a single user request from entry to error across multiple log lines and even microservices.
- **Benefit**: Duration tracking on every request exposes slow endpoints automatically, enabling data-driven performance optimization.
