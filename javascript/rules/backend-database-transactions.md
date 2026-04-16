---
title: Database Transaction Safety
impact: HIGH
impactDescription: Related multi-table operations without transactions leave data inconsistent on partial failure.
tags: database, transactions, postgresql, data-integrity
---

# Database Transaction Safety

Wrap related database operations in BEGIN / COMMIT / ROLLBACK blocks so that partial failures do not leave data in an inconsistent state.

## Bad Example

```typescript
// No transaction — if stock update fails, the order is already saved with wrong totals
export class OrderService {
  constructor(private db: Pool) {}

  async createOrder(userId: string, items: OrderItem[]) {
    const orderResult = await this.db.query(
      "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING id",
      [userId, calculateTotal(items)],
    );
    const orderId = orderResult.rows[0].id;

    for (const item of items) {
      await this.db.query(
        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
        [orderId, item.productId, item.quantity, item.price],
      );

      // If this throws, we have order + some items but wrong stock levels
      await this.db.query(
        "UPDATE products SET stock = stock - $1 WHERE id = $2",
        [item.quantity, item.productId],
      );
    }

    return orderId;
  }
}
```

## Good Example

```typescript
// Transaction with proper BEGIN / COMMIT / ROLLBACK / finally release
export class OrderService {
  constructor(private db: Pool) {}

  async createOrder(userId: string, items: OrderItem[]) {
    const client = await this.db.connect();

    try {
      await client.query("BEGIN");

      const orderResult = await client.query(
        "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING id",
        [userId, calculateTotal(items)],
      );
      const orderId = orderResult.rows[0].id;

      for (const item of items) {
        await client.query(
          "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
          [orderId, item.productId, item.quantity, item.price],
        );

        await client.query(
          "UPDATE products SET stock = stock - $1 WHERE id = $2",
          [item.quantity, item.productId],
        );
      }

      await client.query("COMMIT");
      return orderId;
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally {
      client.release(); // always return the client to the pool
    }
  }
}
```

## Why

- **Benefit**: ROLLBACK on error reverts every query in the block, so the database never holds a partially written order with missing items or incorrect stock.
- **Benefit**: `client.release()` in `finally` guarantees the connection returns to the pool even when an unexpected error occurs, preventing connection leaks.
- **Benefit**: The transaction boundary is explicit and visible, making it clear which operations must succeed or fail as a unit.
