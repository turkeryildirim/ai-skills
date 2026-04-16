---
title: REST for public/polyglot, gRPC for internal hot paths
impact: CRITICAL
tags: [communication, sync]
---

# comm-sync-rest-grpc

Pick sync protocol by audience. REST+JSON is the lingua franca — any client speaks it, browsers include. gRPC+protobuf is faster and type-safe but needs codegen and isn't browser-native. Use REST at the edge; reserve gRPC for east-west where latency and contract strictness matter.

## Bad — PHP

```php
// Public API serving browsers — built on gRPC
// Clients can't call it without grpc-web proxy, PHP-side
// reinvents JSON shapes for the browser app anyway.
$server = new \Grpc\Server();
$server->addService(new PublicOrdersService());
```

## Bad — TypeScript

```ts
// Internal service-to-service call made via REST with no schema
const res = await fetch('http://pricing/api/compute', {
  method: 'POST',
  body: JSON.stringify({ sku: 'ABC', qty: 3 }),  // shape drifts silently
});
const { price } = await res.json();
```

## Good — PHP

```php
// Public REST API (OpenAPI-generated controllers)
#[Route('/api/v1/orders/{id}', methods: ['GET'])]
public function show(string $id): JsonResponse {
    return $this->json($this->orders->find($id));
}

// Internal gRPC call to pricing service
$reply = $this->pricingClient->Compute(
    (new ComputeRequest())->setSku('ABC')->setQty(3),
    ['timeout' => 500_000]  // 500ms deadline
);
```

## Good — TypeScript

```ts
// Public REST (NestJS)
@Get('orders/:id')
findOne(@Param('id') id: string) {
  return this.orders.find(id);
}

// Internal gRPC call
const reply = await this.pricingClient.compute(
  { sku: 'ABC', qty: 3 },
  { deadline: Date.now() + 500 }
);
```

Generated stubs guarantee both ends agree on shape; 500ms deadline is mandatory.
