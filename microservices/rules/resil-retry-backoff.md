---
title: Exponential backoff with jitter; bounded attempts; idempotent only
impact: CRITICAL
tags: [resilience, retry]
---

# resil-retry-backoff

Retries save transient failures but amplify outages. Rules: only retry idempotent operations, cap attempts, wait exponentially, and add jitter to avoid thundering herds. Never retry `400`, `401`, `403`, `404`, or `422` — they're not going to change.

## Bad — PHP

```php
// Tight loop hammers the dependency; no cap
while (true) {
    try { return $this->http->post('/charge', $payload); }
    catch (\Throwable) { sleep(1); }
}
```

## Bad — TypeScript

```ts
for (let i = 0; i < 100; i++) {
  try { return await fetch('/charge', { method: 'POST', body }); }
  catch { /* retry forever */ }
}
```

## Good — PHP

```php
public function chargeWithRetry(array $payload, string $idempotencyKey): array {
    $attempts = 0; $maxAttempts = 4; $baseMs = 200;
    while (true) {
        try {
            return $this->http->post('/charge', [
                'json' => $payload,
                'headers' => ['Idempotency-Key' => $idempotencyKey],
                'timeout' => 2.0,
            ])->json();
        } catch (ClientException $e) {
            throw $e;  // 4xx — won't succeed on retry
        } catch (\Throwable $e) {
            if (++$attempts >= $maxAttempts) throw $e;
            $delayMs = min(5000, $baseMs * (2 ** $attempts)) + random_int(0, 200);
            usleep($delayMs * 1000);
        }
    }
}
```

## Good — TypeScript (cockatiel)

```ts
import { retry, handleWhen, ExponentialBackoff } from 'cockatiel';

const policy = retry(
  handleWhen(err => !(err instanceof HttpClientError)),  // skip 4xx
  { maxAttempts: 4, backoff: new ExponentialBackoff({ initialDelay: 200, maxDelay: 5000 }) },
);

async chargeWithRetry(body: unknown, idempotencyKey: string) {
  return policy.execute(() => fetch('/charge', {
    method: 'POST',
    headers: { 'Idempotency-Key': idempotencyKey, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(2000),
  }).then(throwOnError));
}
```

Exponential: 200, 400, 800, 1600ms. Jitter (`+ random(0, 200)`) spreads clients so they don't sync up on the recovery moment.
