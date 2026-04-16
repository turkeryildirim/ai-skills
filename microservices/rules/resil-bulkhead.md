---
title: Isolate resources per dependency with bulkheads
impact: CRITICAL
tags: [resilience, isolation]
---

# resil-bulkhead

Named after ship hull compartments: if one fills with water, the others stay dry. Give each downstream dependency its own connection pool / semaphore / worker pool so one bad neighbour can't drain a shared pool and starve the healthy paths.

## Bad — PHP

```php
// Shared Guzzle client with one connection pool for every service
$shared = new Client(['timeout' => 1.0]);
// When recommender is slow, orders and payments also queue behind its connections.
```

## Bad — TypeScript

```ts
// Shared http keep-alive agent across all destinations
const agent = new http.Agent({ maxSockets: 50 });
```

## Good — PHP

```php
// One client per downstream, with its own pool size
$this->paymentsHttp    = new Client(['base_uri' => PAYMENTS_URL,    'timeout' => 1.0, /* pool 20 */]);
$this->inventoryHttp   = new Client(['base_uri' => INVENTORY_URL,   'timeout' => 1.0, /* pool 20 */]);
$this->recommenderHttp = new Client(['base_uri' => RECOMMENDER_URL, 'timeout' => 0.3, /* pool  5 */]);

// Semaphore guarding concurrent recommender calls
if (!$this->semaphore->acquire('recommender', timeout: 100)) {
    return $this->defaultRecommendations();  // shed load instead of queueing
}
try { return $this->recommenderHttp->get('/recs'); }
finally { $this->semaphore->release('recommender'); }
```

## Good — TypeScript

```ts
// One agent per host, capped per its criticality
const paymentsAgent    = new http.Agent({ maxSockets: 20 });
const inventoryAgent   = new http.Agent({ maxSockets: 20 });
const recommenderAgent = new http.Agent({ maxSockets: 5 });

// cockatiel bulkhead
const recBulkhead = bulkhead(5, 0);  // max 5 concurrent, 0 queued
async recommend(userId: string) {
  return recBulkhead.execute(() =>
    fetch(RECOMMENDER_URL + '/recs', { agent: recommenderAgent, signal: AbortSignal.timeout(300) })
  ).catch(() => this.defaults());
}
```

When recommender melts, it burns its own pool of 5 — payments and inventory keep their 20 each.
