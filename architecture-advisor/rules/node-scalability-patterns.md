---
title: Node.js Scalability and Async Pattern Analysis
impact: HIGH
impactDescription: "Blocking the event loop and missing queue patterns cause latency spikes and data loss under load"
tags: node, scalability, event-loop, queues, worker-threads, async
---

## Node.js Scalability and Async Pattern Analysis

**Impact: HIGH (Blocking the event loop and missing queue patterns cause latency spikes and data loss under load)**

Node.js's single-threaded event loop is its strength and its primary failure mode. A single synchronous operation — a large JSON parse, a CPU-intensive loop, a `fs.readFileSync` — blocks all concurrent requests. Long-running tasks done synchronously in request handlers, and missing job queue patterns, are the two most common scalability failures.

## Incorrect

```typescript
// ❌ Blocking the event loop in a request handler

app.post('/reports/generate', async (req, res) => {
    // ❌ CPU-intensive operation on the event loop
    const data = await db.query('SELECT * FROM orders'); // Could be 100k rows
    
    const report = data.rows.map(row => {
        // ❌ Synchronous heavy computation — blocks ALL other requests
        return expensiveCalculation(row);
    });

    // ❌ Synchronous file write in request handler
    const csv = convertToCSV(report);
    fs.writeFileSync('./reports/output.csv', csv); // ❌ Blocks event loop

    res.json({ path: './reports/output.csv' });
});

// ❌ Synchronous file operations anywhere in the request path
const config = JSON.parse(fs.readFileSync('./config.json', 'utf-8')); // ❌ blocks
```

```typescript
// ❌ Long-running task inline — no queue, no retry, no failure handling

app.post('/emails/send-campaign', async (req, res) => {
    const users = await db.query('SELECT * FROM users'); // Could be 50k users
    
    // ❌ 50,000 emails sent synchronously in the request — times out
    for (const user of users.rows) {
        await emailService.send(user.email, template); // 50,000 awaits
    }

    res.json({ sent: users.rows.length });
    // If this fails at email 30,000: no retry, partial send, no visibility
});
```

## Correct

```typescript
// ✅ Offload CPU work to Worker Threads

import { Worker, isMainThread, parentPort, workerData } from 'worker_threads';

// Route handler: fast response, heavy work in Worker Thread
app.post('/reports/generate', async (req, res) => {
    const jobId = await ReportJob.enqueue(req.body);
    res.status(202).json({ jobId, status: 'processing' }); // ✅ Immediate response
});

// Worker thread handles CPU-intensive work
// workers/reportWorker.ts
if (!isMainThread) {
    const { data } = workerData;
    const result = expensiveCalculation(data); // ✅ Doesn't block event loop
    parentPort?.postMessage(result);
}
```

```typescript
// ✅ Queue-based long-running tasks with BullMQ

import { Queue, Worker } from 'bullmq';

const emailQueue = new Queue('email-campaigns', { connection: redis });

// Route: enqueue immediately, respond fast
app.post('/emails/send-campaign', async (req, res) => {
    await emailQueue.add('send-campaign', {
        campaignId: req.body.campaignId,
        scheduledAt: req.body.scheduledAt,
    }, {
        attempts: 3,                    // ✅ Retry on failure
        backoff: { type: 'exponential', delay: 1000 },
    });

    res.status(202).json({ message: 'Campaign queued' });
});

// Worker processes asynchronously, in batches
const worker = new Worker('email-campaigns', async (job) => {
    const users = await UserRepository.findForCampaign(job.data.campaignId);
    
    // ✅ Process in chunks — not all 50k at once
    for (const chunk of chunks(users, 100)) {
        await Promise.all(chunk.map(u => emailService.send(u.email, template)));
        await job.updateProgress(Math.floor(processed / total * 100));
    }
}, { connection: redis, concurrency: 5 });
```

## Scalability Assessment Checklist

```
Event Loop Protection:
[ ] No fs.readFileSync / fs.writeFileSync in request paths
[ ] No JSON.parse of large payloads on the main thread (use streams)
[ ] No CPU-intensive loops (encryption, image processing, report generation) in request handlers
[ ] Worker Threads or separate process for CPU-bound work

Queue Patterns:
[ ] Long-running tasks (>2s expected) use a job queue (BullMQ, pg-boss)
[ ] Queue jobs have: retry attempts, backoff strategy, dead-letter queue
[ ] Queue visibility: job progress trackable, failed jobs inspectable

Database Access:
[ ] Paginated queries — no SELECT * without LIMIT on large tables
[ ] Streaming for large dataset exports (not loading all rows into memory)
[ ] Connection pool configured with max connections

Deployment:
[ ] Graceful shutdown handler (SIGTERM): drain connections, finish queue jobs
[ ] Health check endpoint (/health) for load balancer probes
[ ] Cluster mode or PM2 configured to use multiple CPU cores
```

## Why

- **Event loop**: Node.js processes one thing at a time synchronously — a 100ms CPU operation delays all concurrent requests by 100ms
- **Queue reliability**: Inline long-running tasks fail silently on server restart; queues persist jobs and enable retry
- **Memory**: Loading 100k database rows into memory at once causes OOM crashes; streaming processes row-by-row
