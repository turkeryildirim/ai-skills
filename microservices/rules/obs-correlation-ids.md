---
title: Propagate X-Correlation-Id through every hop
impact: HIGH
tags: [observability]
---

# obs-correlation-ids

A single ID ties logs, traces, and metrics for one user request together across every service, queue, and DB call it touches. Without it, you're grepping timestamps.

## Bad — PHP

```php
public function handle(Request $req) {
    Log::info('order created', ['order_id' => $id]);
    $this->http->post('http://payments/charge', ['json' => $payload]);
    // payments service has no idea this came from request X
}
```

## Bad — TypeScript

```ts
logger.info({ orderId }, 'order created');
await fetch('http://payments/charge', { method: 'POST', body });
```

## Good — PHP

```php
// middleware/CorrelationId.php
public function handle(Request $req, Closure $next) {
    $id = $req->header('X-Correlation-Id') ?: (string) Ulid::generate();
    Context::add('correlation_id', $id);
    Log::withContext(['correlation_id' => $id]);
    $response = $next($req);
    return $response->header('X-Correlation-Id', $id);
}

// outbound HTTP client attaches it
$this->http->post('http://payments/charge', [
    'headers' => ['X-Correlation-Id' => Context::get('correlation_id')],
    'json'    => $payload,
]);
```

## Good — TypeScript

```ts
// NestJS middleware
use(req: Request, res: Response, next: NextFunction) {
  const id = req.header('X-Correlation-Id') ?? ulid();
  asyncLocalStorage.run({ correlationId: id }, () => {
    res.setHeader('X-Correlation-Id', id);
    next();
  });
}

// All outbound calls read from AsyncLocalStorage
await fetch('http://payments/charge', {
  method: 'POST',
  headers: { 'X-Correlation-Id': store().correlationId, 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
});
```

Also copy the ID onto published events (as `correlation_id` field) so async consumers keep the chain.
