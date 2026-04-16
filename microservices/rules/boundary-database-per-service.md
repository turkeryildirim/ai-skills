---
title: Each service owns its own database schema
impact: CRITICAL
tags: [boundaries, data]
---

# boundary-database-per-service

No other service connects to your DB. Not for reads, not for reports, not "just this once". A shared schema couples deploys (you can't evolve a column without coordinating) and blurs ownership. Expose data through APIs or domain events.

## Bad — PHP

```php
// reports-service connecting directly to orders DB
$pdo = new PDO('pgsql:host=orders-db;dbname=orders', $user, $pass);
$rows = $pdo->query('SELECT * FROM orders WHERE status = \'paid\'')->fetchAll();
```

## Bad — TypeScript

```ts
// reports-service/src/index.ts
const orders = new Pool({ host: 'orders-db', database: 'orders' });
const { rows } = await orders.query("SELECT * FROM orders WHERE status = 'paid'");
```

Reports now breaks the moment Orders renames a column or shards the table.

## Good — PHP

```php
// reports-service calls orders API
$response = $http->get('http://orders-service/api/v1/orders', [
    'query' => ['status' => 'paid'],
]);
$orders = json_decode($response->getBody()->getContents(), true);
```

## Good — TypeScript

```ts
// reports-service consumes OrderPaid events and builds its own projection
consumer.on('OrderPaid', async (event) => {
  await reportsDb.insert('paid_orders_projection', {
    order_id: event.data.orderId,
    paid_at: event.occurredAt,
    total_cents: event.data.totalCents,
  });
});
```

Reports owns its projection table and survives any internal change in the Orders schema.
