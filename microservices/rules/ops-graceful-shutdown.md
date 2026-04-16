---
title: Drain in-flight work before SIGTERM grace expires
impact: HIGH
tags: [operations, shutdown]
---

# ops-graceful-shutdown

On deploy, Kubernetes sends SIGTERM then waits `terminationGracePeriodSeconds` (default 30s) before SIGKILL. If you don't drain, in-flight requests get dropped and queue messages get replayed unnecessarily.

## Bad — PHP / TypeScript

```ts
// No shutdown handler — process dies mid-request on deploy
```

## Good — PHP (Laravel Octane / Symfony)

```php
// bootstrap/app.php or kernel
pcntl_signal(SIGTERM, function () {
    app('shutdown-flag')->begin();                 // /health/ready now 503s
    sleep(5);                                      // let LB notice
    app(ConnectionInterface::class)->disconnect(); // close DB
    app(QueueManager::class)->stopPolling();       // drain workers
    exit(0);
});

// Queue worker
while (!app('shutdown-flag')->isShuttingDown()) {
    $job = $this->queue->pop(timeout: 1);
    if ($job) $this->process($job);
}
$this->flushInFlight();
```

## Good — TypeScript (NestJS / Express)

```ts
const app = await NestFactory.create(AppModule);
app.enableShutdownHooks();
const server = await app.listen(3000);

let shuttingDown = false;
export const isShuttingDown = () => shuttingDown;

async function shutdown(signal: string) {
  logger.info({ signal }, 'shutdown started');
  shuttingDown = true;                          // /health/ready returns 503
  await new Promise(r => setTimeout(r, 5000));  // give LB time to notice
  server.close();                               // stop accepting new conns
  await kafka.consumer.disconnect();            // stop polling
  await app.close();                            // flush DI shutdown hooks
  logger.info('shutdown complete');
  process.exit(0);
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT',  () => shutdown('SIGINT'));
```

Pair this with Kubernetes `preStop` hook + appropriate `terminationGracePeriodSeconds` so the whole sequence fits in the grace window with margin.
