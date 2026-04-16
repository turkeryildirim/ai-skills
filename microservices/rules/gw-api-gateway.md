---
title: Gateway routes, auths, rate-limits — no business logic
impact: HIGH
tags: [gateway]
---

# gw-api-gateway

The gateway is the front door: TLS, auth, rate-limit, route. It should not know what an Order is, what prices are legal, or how to calculate loyalty points. When business logic leaks into the gateway, every domain change needs a gateway deploy and the gateway becomes the bottleneck.

## Bad — Gateway plugin (pseudocode)

```lua
-- Kong plugin running business logic in the request path
local order = request.body
if order.total_cents > 100000 and order.customer.country == 'XX' then
  local score = call_fraud_service(order)
  if score > 80 then return 403 end
end
order.total_cents = apply_discount(order)  -- repricing
request:set_body(order)
```

## Good — Gateway config (Kong / Envoy / Traefik)

```yaml
# Only routing + auth + rate-limit
services:
  - name: orders-service
    url: http://orders-service.default.svc.cluster.local
    routes:
      - paths: ['/api/v1/orders']
    plugins:
      - name: jwt
      - name: rate-limiting
        config: { minute: 600, policy: redis }
      - name: cors
        config: { origins: ['https://app.example.com'] }
      - name: request-transformer
        config: { remove: { headers: ['X-Internal-*'] } }
```

## Good — Business logic lives in the service

```php
// orders-service handles fraud check and pricing
public function place(PlaceOrder $cmd): Order {
    $score = $this->fraud->score($cmd);
    if ($score > 80) throw new SuspectedFraudException();
    $priced = $this->pricing->apply($cmd);
    return $this->orders->create($priced);
}
```

Rule of thumb: if adding a feature to the domain requires editing gateway config, the wrong thing is in the gateway.
