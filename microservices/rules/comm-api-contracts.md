---
title: OpenAPI / proto / AsyncAPI are the source of truth
impact: CRITICAL
tags: [communication, contracts]
---

# comm-api-contracts

Define the contract **first**, generate server stubs and typed clients from it. Hand-written DTOs on both sides drift within a sprint. Contract-first means breaking changes fail CI, not prod.

## Bad — PHP

```php
// Controller invents JSON shape; frontend team reads code to guess it
public function show(int $id) {
    $o = Order::find($id);
    return response()->json([
        'id' => $o->id,
        'status' => $o->status,
        'total' => $o->total_cents / 100,  // string? float? who knows
    ]);
}
```

## Bad — TypeScript

```ts
// Hand-written client, hand-written server type, duplicated and drifting
interface Order { id: string; status: string; total: number; }
const r = await fetch(`/api/orders/${id}`);
const order: Order = await r.json();  // no validation
```

## Good — PHP

```yaml
# contracts/openapi.yaml (source of truth, in its own repo)
paths:
  /orders/{id}:
    get:
      parameters:
        - { in: path, name: id, required: true, schema: { type: string } }
      responses:
        '200': { content: { application/json: { schema: { $ref: '#/components/schemas/Order' } } } }
components:
  schemas:
    Order:
      type: object
      required: [id, status, total_cents]
      properties:
        id:          { type: string }
        status:      { type: string, enum: [pending, paid, shipped] }
        total_cents: { type: integer, minimum: 0 }
```

```php
// Server stub generated; controller just returns the DTO
public function show(string $id): OrderResponse {
    $o = $this->orders->find($id);
    return new OrderResponse(id: $o->id, status: $o->status, totalCents: $o->totalCents);
}
```

## Good — TypeScript

```ts
// Typed client generated from the same openapi.yaml
import { OrdersClient } from '@org/orders-client';  // codegen output
const order = await orders.getById(id);  // fully typed, validated
```

Breaking the schema breaks CI in both services simultaneously; no runtime surprises.
