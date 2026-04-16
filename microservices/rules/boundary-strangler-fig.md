---
title: Extract from monolith incrementally with a strangler fig
impact: CRITICAL
tags: [boundaries, migration]
---

# boundary-strangler-fig

Never "big-bang" rewrite a monolith. Put a router in front, migrate one capability at a time, keep the old path running until the new one is proven. Named after the strangler fig tree which gradually envelops its host.

## Bad — PHP

```php
// Weekend project: copy half the monolith into a new repo,
// flip DNS on Monday, debug in prod.
```

## Bad — TypeScript

```ts
// v2/ — full rewrite, 0% test coverage, plan to cut over next quarter
```

Both fail: no rollback path, no incremental validation, no way to A/B old vs new.

## Good — PHP

```php
// gateway/routes.php — strangler routing
$router->match('/api/orders/*', function ($req) {
    if ($req->header('X-Use-New-Service') || mt_rand(1, 100) <= 5) {
        return proxy($req, 'http://orders-service-new');  // 5% canary
    }
    return proxy($req, 'http://monolith');
});
```

## Good — TypeScript

```ts
// gateway.ts
app.use('/api/orders', (req, res) => {
  const useNew = req.header('X-Use-New-Service') === '1'
              || Math.random() < 0.05;
  const target = useNew ? ORDERS_NEW_URL : MONOLITH_URL;
  proxy.web(req, res, { target });
});
```

Gradually raise the canary % as confidence grows. Once 100% traffic routes to the new service and the monolith's orders code is unreachable, delete it.
