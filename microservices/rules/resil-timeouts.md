---
title: Every outbound call has a timeout shorter than upstream's
impact: CRITICAL
tags: [resilience, timeouts]
---

# resil-timeouts

The default timeout of every HTTP client library is far too long (often infinite). One slow dependency then saturates all your workers waiting on it. Set explicit, tight timeouts, tighter than the caller's budget so there's headroom to retry.

## Bad — PHP

```php
// Default timeout — Guzzle is ~infinite
$response = $this->http->get('http://pricing/api/price/ABC');
```

## Bad — TypeScript

```ts
// Node fetch has no default timeout
const r = await fetch('http://pricing/api/price/ABC');
```

## Good — PHP

```php
// Client budget: 5s. Gateway: 4.5s. This service: 3s. This call: 500ms.
$response = $this->http->get('http://pricing/api/price/ABC', [
    'timeout' => 0.5,
    'connect_timeout' => 0.2,
]);
```

## Good — TypeScript

```ts
const r = await fetch('http://pricing/api/price/ABC', {
  signal: AbortSignal.timeout(500),
});
```

Always set **both** connect timeout and overall timeout. A fast-failing unreachable host (connect timeout) is very different from a slow-responding host (read timeout).
