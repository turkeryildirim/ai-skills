---
title: Graceful Shutdown Handling
impact: MEDIUM
impactDescription: Abrupt process exit drops in-flight requests and leaks database connections.
tags: shutdown, reliability, express
---

# Graceful Shutdown Handling

Listen for SIGTERM and SIGINT signals, stop accepting new connections, drain in-flight requests, and close database pools before exiting.

## Bad Example

```typescript
// No shutdown handling — Ctrl+C or Kubernetes SIGTERM kills the process instantly
import express from "express";
import { Pool } from "pg";

const app = express();
const pool = new Pool({ /* config */ });

app.get("/users", async (req, res) => {
  const { rows } = await pool.query("SELECT * FROM users");
  res.json(rows);
});

app.listen(3000, () => {
  console.log("Server started");
});
// In-flight requests are aborted, database connections are leaked
```

## Good Example

```typescript
// utils/graceful-shutdown.ts
import { closeDatabase } from "../config/database";
import { logger } from "../middleware/logger.middleware";
import type { Server } from "http";

let isShuttingDown = false;

export const setupGracefulShutdown = (server: Server) => {
  const shutdown = async (signal: string) => {
    if (isShuttingDown) return;
    isShuttingDown = true;

    logger.info(`Received ${signal}. Shutting down gracefully...`);

    // Stop accepting new connections
    server.close(() => {
      logger.info("HTTP server closed");
    });

    // Close database connections
    try {
      await closeDatabase();
      logger.info("Database connections closed");
    } catch (err) {
      logger.error({ error: err }, "Error closing database");
    }

    process.exit(0);
  };

  process.on("SIGTERM", () => shutdown("SIGTERM"));
  process.on("SIGINT", () => shutdown("SIGINT"));
};

// config/database.ts
export const closeDatabase = async () => {
  await pool.end();
};

// app.ts
const server = app.listen(3000, () => {
  logger.info("Server started on port 3000");
});

setupGracefulShutdown(server);
```

## Why

- **Benefit**: `server.close()` stops the socket from accepting new connections while allowing in-flight requests to complete, preventing 502 errors seen by clients.
- **Benefit**: `pool.end()` drains active database connections cleanly, avoiding connection leaks that would accumulate on the database server.
- **Benefit**: The `isShuttingDown` guard prevents double-shutdown if the signal fires twice, which is common in containerized environments.
