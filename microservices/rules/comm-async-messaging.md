---
title: Queue long-running and cross-service work via a broker
impact: CRITICAL
tags: [communication, async]
---

# comm-async-messaging

If the caller doesn't need an answer in the current request, don't make it wait. Publish to a broker and return. This decouples deploys, smooths spikes, and lets you retry without the user staring at a spinner.

## Bad — PHP

```php
// Controller blocks the HTTP request for 12s sending emails
public function placeOrder(Request $r) {
    $order = $this->orders->create($r->all());
    $this->mailer->send(new ConfirmationEmail($order));          // 3s
    $this->mailer->send(new AdminAlert($order));                 // 2s
    $this->analytics->track('order_placed', $order);             // 1.5s
    $this->warehouse->notify($order);                            // 5s
    return response()->json($order);
}
```

## Bad — TypeScript

```ts
@Post('orders')
async place(@Body() dto: PlaceOrderDto) {
  const order = await this.orders.create(dto);
  await this.mailer.sendConfirmation(order);   // blocks response
  await this.mailer.sendAdminAlert(order);
  await this.analytics.track(order);
  await this.warehouse.notify(order);
  return order;
}
```

## Good — PHP (Laravel queues / Symfony Messenger)

```php
public function placeOrder(Request $r) {
    $order = $this->orders->create($r->all());
    // single DB tx writes order + outbox row; relay publishes
    $this->events->publish(new OrderCreated($order));
    return response()->json($order);  // ~80ms
}
```

## Good — TypeScript (kafkajs / bullmq)

```ts
@Post('orders')
async place(@Body() dto: PlaceOrderDto) {
  const order = await this.orders.create(dto);
  await this.events.publish('OrderCreated', {
    event_id: ulid(),
    data: { order_id: order.id, customer_id: order.customerId },
  });
  return order;
}
```

Confirmation email, admin alert, analytics, and warehouse are independent subscribers — each retries on its own, none block the response.
