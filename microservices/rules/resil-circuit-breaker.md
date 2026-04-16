---
title: Stop calling a failing dependency; fail fast; half-open to probe
impact: CRITICAL
tags: [resilience]
---

# resil-circuit-breaker

When a dependency is down, the polite thing is to stop hammering it. A circuit breaker tracks failures in a sliding window; after a threshold it **opens** and fails fast for a cooldown, then allows one probe. Saves your workers and gives the downstream room to recover.

## Bad — PHP

```php
// Every request hits the dead dependency; workers pile up on 30s timeouts
public function getPrice(string $sku): int {
    return $this->http->get("http://pricing/api/price/$sku")->json()['cents'];
}
```

## Bad — TypeScript

```ts
async getPrice(sku: string): Promise<number> {
  const r = await fetch(`http://pricing/api/price/${sku}`);
  return (await r.json()).cents;
}
```

## Good — PHP (ackintosh/ganesha)

```php
$ganesha = Builder::withRateStrategy()
    ->failureRateThreshold(50)
    ->intervalToHalfOpen(10)
    ->minimumRequests(10)
    ->timeWindow(30)
    ->adapter(new Redis($redis))
    ->build();

public function getPrice(string $sku): int {
    if (!$this->ganesha->isAvailable('pricing')) {
        return $this->fallbackCents($sku);  // last known good
    }
    try {
        $cents = $this->http->get("http://pricing/api/price/$sku", ['timeout' => 0.5])->json()['cents'];
        $this->ganesha->success('pricing');
        return $cents;
    } catch (\Throwable $e) {
        $this->ganesha->failure('pricing');
        return $this->fallbackCents($sku);
    }
}
```

## Good — TypeScript (opossum)

```ts
const breaker = new CircuitBreaker(
  (sku: string) => fetch(`http://pricing/api/price/${sku}`, { signal: AbortSignal.timeout(500) })
                     .then(r => r.json()).then(j => j.cents as number),
  { errorThresholdPercentage: 50, resetTimeout: 10_000, volumeThreshold: 10 },
);
breaker.fallback((sku) => this.lastKnownCents(sku));

async getPrice(sku: string) { return breaker.fire(sku); }
```

Once OPEN, calls short-circuit in microseconds and serve the fallback. After 10s, one probe determines whether to close the circuit.
