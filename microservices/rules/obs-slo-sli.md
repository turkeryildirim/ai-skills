---
title: Define SLIs, SLOs, and an error budget policy
impact: HIGH
tags: [observability, slo]
---

# obs-slo-sli

"Is the service healthy?" is unanswerable without a number. An SLO is that number. An error budget is the agreement between product and engineering about what happens when you miss it.

## Bad — PHP / TypeScript (both)

```yaml
# No SLO. Health = "nobody's paging me right now."
# Outage reviews devolve into arguments about whether this one counted.
```

## Good — SLO definition

```yaml
# orders-api.slo.yaml
service: orders-api
slis:
  availability:
    description: Fraction of 200-range responses among non-4xx requests
    query: |
      sum(rate(http_requests_total{service="orders-api",code!~"4.."}[5m]))
      / sum(rate(http_requests_total{service="orders-api",code!~"4..",code!~"5.."}[5m]))
  latency:
    description: Fraction of requests faster than 300ms
    query: |
      sum(rate(http_request_duration_seconds_bucket{service="orders-api",le="0.3"}[5m]))
      / sum(rate(http_request_duration_seconds_count{service="orders-api"}[5m]))

slos:
  - sli: availability
    target: 0.999
    window: 30d
  - sli: latency
    target: 0.95
    window: 30d

error_budget_policy:
  when_burned_50_percent: warn in #sre channel
  when_burned_100_percent: freeze non-critical feature work, reliability-only sprint
```

## Good — PHP (metric emission)

```php
// HTTP middleware records the SLI data
$startedAt = hrtime(true);
$response = $next($req);
$durationSec = (hrtime(true) - $startedAt) / 1e9;
$this->metrics->histogram('http_request_duration_seconds', $durationSec, [
    'service' => 'orders-api', 'route' => $route, 'method' => $req->method(),
]);
$this->metrics->counter('http_requests_total', 1, [
    'service' => 'orders-api', 'code' => (string) $response->status(),
]);
```

## Good — TypeScript

```ts
// prom-client histogram + counter
httpDuration.labels({ service, route, method }).observe(durationSec);
httpRequests.labels({ service, code: String(res.statusCode) }).inc();
```

SLIs user-centric (success rate, latency p95/p99, freshness), not infra-centric (CPU %). Burn-rate alerts (fast: 2% budget in 1h, slow: 10% in 6h) page only on trends that matter.
