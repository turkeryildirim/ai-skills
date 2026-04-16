---
title: Per-key, per-endpoint rate limits; 429 with Retry-After
impact: HIGH
tags: [gateway, rate-limiting]
---

# gw-rate-limiting

Protect expensive endpoints, enforce tier limits, and shield against abuse. Limits should be expressive: per API key **and** per endpoint **and** per tenant — not one global bucket. Always return `429 Too Many Requests` with `Retry-After`, never silently drop.

## Bad — PHP

```php
// Single global counter — one noisy tenant starves all others
if (Cache::increment('global_req_count') > 10000) {
    return response('Too many', 503);  // wrong status; no retry info
}
```

## Bad — TypeScript

```ts
if (requestsThisSecond > 1000) return res.status(500).send('slow down');
```

## Good — Gateway config (Kong example)

```yaml
plugins:
  - name: rate-limiting-advanced
    config:
      limit: [600, 60000]           # 600/min, 60000/day
      window_size: [60, 86400]
      identifier: consumer          # per API key
      strategy: redis
  - name: rate-limiting-advanced
    route: expensive-search-route
    config:
      limit: [30]                   # tighter on a hot endpoint
      window_size: [60]
      identifier: consumer
```

## Good — PHP (application-side, per-user)

```php
$key = "rl:user:{$user->id}:orders";
$count = Redis::incr($key);
if ($count === 1) Redis::expire($key, 60);
if ($count > 120) {
    return response()->json(
        ['error' => ['code' => 'RATE_LIMITED', 'message' => 'Too many requests']],
        429,
        ['Retry-After' => '60',
         'X-RateLimit-Limit' => '120',
         'X-RateLimit-Remaining' => '0',
         'X-RateLimit-Reset' => (string) (time() + Redis::ttl($key))]
    );
}
```

## Good — TypeScript (express-rate-limit / custom)

```ts
const limiter = rateLimit({
  windowMs: 60_000,
  limit: 120,
  standardHeaders: 'draft-7',       // RateLimit-* + Retry-After
  keyGenerator: (req) => req.user?.id ?? req.ip,
  handler: (req, res) => {
    res.status(429).json({
      error: { code: 'RATE_LIMITED', message: 'Too many requests' },
    });
  },
});
app.use('/api/orders', limiter);
```

Always expose `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After` so good clients can back off; bad clients at least stop guessing.
