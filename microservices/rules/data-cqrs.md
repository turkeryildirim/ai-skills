---
title: Separate write model from read projections
impact: CRITICAL
tags: [data, cqrs]
---

# data-cqrs

Use one model for writes (normalised, transactional) and separate read models optimised per query (denormalised, possibly in a different store). Great when read and write shapes diverge or read scale ≫ write scale. Overkill for simple CRUD.

## Bad — PHP

```php
// Same ORM entity serves /api/orders/123 AND full-text search AND dashboards
$orders = Order::with(['items.product', 'customer', 'shipments', 'invoices'])
    ->where('status', 'paid')
    ->orderByRaw('similarity(notes, ?) DESC', [$q])
    ->paginate(20);
// Heavy joins + full-text on the transactional DB = slow under load
```

## Bad — TypeScript

```ts
const orders = await Order.findAll({
  include: [Items, Customer, Shipments, Invoices],
  where: { status: 'paid' },
});
// Plus a cron that scans the same DB to rebuild dashboards
```

## Good — PHP

```php
// Write side: command handler writes normalised rows + emits events
final class PayOrderHandler {
    public function __invoke(PayOrder $cmd): void {
        $order = $this->orders->find($cmd->orderId);
        $order->markPaid($cmd->paymentId);
        $this->orders->save($order);
        $this->events->publish(new OrderPaid($order->id, $order->totalCents));
    }
}

// Read side: projector updates denormalised search index on the event
final class OrderSearchProjector {
    public function onOrderPaid(OrderPaid $e): void {
        $this->elastic->index('orders', $e->orderId, [
            'status' => 'paid', 'total_cents' => $e->totalCents,
            'customer_name' => $e->customerName, /* …flattened view */
        ]);
    }
}
```

## Good — TypeScript

```ts
// Write side
async pay(cmd: PayOrderCmd) {
  const order = await orders.findById(cmd.orderId);
  order.markPaid(cmd.paymentId);
  await orders.save(order);
  await events.publish(new OrderPaid(order.id, order.totalCents));
}

// Read side: independent Elasticsearch projection
consumer.on('OrderPaid', async (e) => {
  await elastic.index({
    index: 'orders',
    id: e.order_id,
    document: { status: 'paid', total_cents: e.total_cents, /* … */ },
  });
});
```

Writes hit Postgres, reads hit Elasticsearch. Each scales independently. Reads are eventually consistent — expose `updated_at` so clients can detect staleness.
