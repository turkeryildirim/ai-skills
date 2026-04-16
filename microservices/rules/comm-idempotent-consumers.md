---
title: Dedupe consumers by event_id — brokers deliver at-least-once
impact: CRITICAL
tags: [communication, idempotency]
---

# comm-idempotent-consumers

Every modern broker (Kafka, RabbitMQ, SQS) delivers **at-least-once**. Your consumer WILL see the same message twice during failovers, rebalances, or retries. If it isn't idempotent, you'll double-charge, double-email, or corrupt counters.

## Bad — PHP

```php
public function onOrderPaid(OrderPaid $event): void {
    $this->ledger->increment('revenue_cents', $event->totalCents);  // double on replay
    $this->mailer->send(new ReceiptEmail($event->orderId));         // sent twice
}
```

## Bad — TypeScript

```ts
consumer.on('OrderPaid', async (event) => {
  await ledger.increment('revenue_cents', event.totalCents);
  await mailer.sendReceipt(event.orderId);
});
```

## Good — PHP

```php
public function onOrderPaid(OrderPaid $event): void {
    // Insert into dedup table; unique constraint rejects replays
    try {
        DB::insert('INSERT INTO processed_events (consumer, event_id) VALUES (?, ?)',
                   ['ledger', $event->eventId]);
    } catch (UniqueConstraintViolationException) {
        return;  // already processed
    }
    $this->ledger->increment('revenue_cents', $event->totalCents);
    $this->mailer->send(new ReceiptEmail($event->orderId));
}
```

## Good — TypeScript

```ts
consumer.on('OrderPaid', async (event) => {
  const result = await db.query(
    `INSERT INTO processed_events (consumer, event_id) VALUES ($1, $2)
     ON CONFLICT DO NOTHING RETURNING event_id`,
    ['ledger', event.event_id]
  );
  if (result.rowCount === 0) return;  // dup
  await ledger.increment('revenue_cents', event.data.total_cents);
  await mailer.sendReceipt(event.data.order_id);
});
```

Dedup + side effects ideally live in **one** DB transaction so a crash between them forces safe replay.
