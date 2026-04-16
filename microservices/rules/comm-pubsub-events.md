---
title: Publish domain events; subscribers are decoupled
impact: CRITICAL
tags: [communication, events]
---

# comm-pubsub-events

Emit facts about what happened in your domain (`OrderPaid`, `UserSignedUp`), not commands that tell other services what to do (`SendEmail`). Commands couple you to the subscriber; events let unknown future subscribers plug in without the publisher changing.

## Bad — PHP

```php
// Publisher knows about every downstream concern
$queue->push(new SendConfirmationEmailJob($order));
$queue->push(new UpdateAnalyticsJob($order));
$queue->push(new AllocateInventoryJob($order));
$queue->push(new NotifyWarehouseJob($order));
// Adding a loyalty service means changing this caller.
```

## Bad — TypeScript

```ts
await queue.add('send-confirmation-email', order);
await queue.add('update-analytics', order);
await queue.add('allocate-inventory', order);
```

## Good — PHP

```php
// Publisher emits a single fact
$this->events->publish(new OrderPaid(
    eventId: Ulid::generate(),
    occurredAt: new \DateTimeImmutable(),
    data: ['order_id' => $order->id, 'total_cents' => $order->totalCents],
));
```

## Good — TypeScript

```ts
await producer.send({
  topic: 'orders.events',
  messages: [{
    key: order.id,  // partition key for ordering per aggregate
    value: JSON.stringify({
      event_id: ulid(),
      event_type: 'OrderPaid',
      event_version: 1,
      aggregate_id: order.id,
      occurred_at: new Date().toISOString(),
      data: { order_id: order.id, total_cents: order.totalCents },
    }),
  }],
});
```

Email, analytics, inventory, warehouse, and a future loyalty service each subscribe independently. The publisher never changes when a new subscriber appears.
