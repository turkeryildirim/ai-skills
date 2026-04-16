---
title: /health/live and /health/ready answer different questions
impact: HIGH
tags: [operations, kubernetes]
---

# ops-health-probes

**Liveness** = "am I alive?" Failing → pod restarts. **Readiness** = "can I serve traffic?" Failing → pod removed from the Service load balancer. Mixing them causes restart storms (DB blip restarts every replica) or traffic going to a warming-up pod.

## Bad — PHP

```php
Route::get('/health', function () {
    DB::select('SELECT 1');                // DB check in liveness → restart storms
    Redis::ping();
    Http::get('http://payments/health');   // chained health checks cascade failures
    return 'OK';
});
```

## Bad — TypeScript

```ts
@Get('health')
async health() {
  await this.db.query('SELECT 1');
  await this.redis.ping();
  await fetch('http://payments/health');
  return 'OK';
}
```

## Good — PHP

```php
// Liveness: am I the process still alive? No external deps.
Route::get('/health/live', fn() => response()->json(['status' => 'ok']));

// Readiness: can I serve traffic now? Check *my* deps only, not transitively.
Route::get('/health/ready', function () {
    $checks = [
        'db'    => fn() => DB::select('SELECT 1') !== null,
        'redis' => fn() => Redis::ping() === 'PONG',
    ];
    $failed = [];
    foreach ($checks as $name => $check) {
        try { if (!$check()) $failed[] = $name; }
        catch (\Throwable) { $failed[] = $name; }
    }
    $ready = empty($failed) && !app('shutdown-flag')->isShuttingDown();
    return response()->json(['ready' => $ready, 'failed' => $failed], $ready ? 200 : 503);
});
```

## Good — TypeScript

```ts
@Get('health/live')
live() { return { status: 'ok' }; }

@Get('health/ready')
async ready() {
  const failed: string[] = [];
  try { await this.db.query('SELECT 1'); } catch { failed.push('db'); }
  try { await this.redis.ping(); }        catch { failed.push('redis'); }
  const ready = failed.length === 0 && !this.shutdown.inProgress;
  if (!ready) throw new ServiceUnavailableException({ ready, failed });
  return { ready, failed };
}
```

Readiness flips to 503 during graceful shutdown so the service mesh stops sending traffic before the process exits.
