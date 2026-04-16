---
title: Services react to events — no central coordinator
impact: CRITICAL
tags: [data, saga]
---

# data-saga-choreography

For 2–3 step flows, skip the orchestrator: each service subscribes to the previous step's success event and emits its own. Simpler for small flows; harder to reason about as the graph grows.

## Bad — PHP

```php
// Orders service calling every downstream directly
public function place(Order $o): void {
    $this->inventoryClient->reserve($o);
    $this->paymentsClient->charge($o);
    $this->shippingClient->schedule($o);
    // tight coupling; orders service knows every downstream
}
```

## Bad — TypeScript

```ts
await inventory.reserve(order);
await payments.charge(order);
await shipping.schedule(order);
```

## Good — PHP

```php
// orders-service — emits and forgets
$this->events->publish(new OrderPlaced($order));

// inventory-service
public function onOrderPlaced(OrderPlaced $e): void {
    $reserved = $this->inventory->reserve($e->orderId);
    $this->events->publish($reserved ? new InventoryReserved($e->orderId)
                                      : new InventoryOutOfStock($e->orderId));
}

// payments-service
public function onInventoryReserved(InventoryReserved $e): void {
    try {
        $this->charge($e->orderId);
        $this->events->publish(new OrderPaid($e->orderId));
    } catch (\Throwable) {
        $this->events->publish(new PaymentFailed($e->orderId));
    }
}

// inventory-service also subscribes to PaymentFailed and releases the reservation
```

## Good — TypeScript

```ts
// orders
await producer.publish('OrderPlaced', { order_id: order.id });

// inventory
consumer.on('OrderPlaced', async (e) => {
  const ok = await inventory.reserve(e.order_id);
  await producer.publish(ok ? 'InventoryReserved' : 'InventoryOutOfStock', { order_id: e.order_id });
});

// payments
consumer.on('InventoryReserved', async (e) => {
  try { await payments.charge(e.order_id);
        await producer.publish('OrderPaid', { order_id: e.order_id });
  } catch { await producer.publish('PaymentFailed', { order_id: e.order_id }); }
});
```

Each service only knows about its inputs and outputs. If the flow grows past ~3 steps, graduate to orchestration.
