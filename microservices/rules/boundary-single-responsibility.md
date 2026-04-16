---
title: One business capability per service
impact: CRITICAL
tags: [boundaries, cohesion]
---

# boundary-single-responsibility

A service should do one thing: ship orders, process payments, send emails. When a service handles unrelated capabilities (orders + invoicing + notifications), every change touches shared code, teams collide on deploys, and the blast radius grows.

## Bad — PHP

```php
// app/Services/OrderService.php — 2000+ lines
class OrderService {
    public function placeOrder(...) {}
    public function chargeCard(...) {}          // payments
    public function sendConfirmationEmail() {}  // notifications
    public function generateInvoicePdf() {}     // invoicing
    public function updateInventory() {}        // inventory
    public function computeLoyaltyPoints() {}   // loyalty
}
```

## Bad — TypeScript

```ts
@Injectable()
export class OrderService {
  placeOrder() {}
  chargeCard() {}
  sendConfirmationEmail() {}
  generateInvoicePdf() {}
  updateInventory() {}
  computeLoyaltyPoints() {}
}
```

## Good — PHP

```php
// orders-service: orchestrates the workflow, owns no other capability
class PlaceOrder {
    public function __invoke(PlaceOrderCommand $cmd): OrderId {
        $order = $this->orders->create($cmd);
        $this->events->publish(new OrderCreated($order));
        return $order->id;
    }
}
```

## Good — TypeScript

```ts
// orders-service
@Injectable()
export class PlaceOrder {
  async execute(cmd: PlaceOrderCommand): Promise<OrderId> {
    const order = await this.orders.create(cmd);
    await this.events.publish(new OrderCreated(order));
    return order.id;
  }
}
```

Payments, inventory, notifications, loyalty each live in their own service and subscribe to `OrderCreated`.
