---
title: Node.js Layer Structure Analysis
impact: CRITICAL
impactDescription: "Business logic in route handlers makes code untestable and creates duplication"
tags: node, layering, controller, service, repository, architecture
---

## Node.js Layer Structure Analysis

**Impact: CRITICAL (Business logic in route handlers makes code untestable and creates duplication)**

The most common architectural failure in Node.js backends is collapsing all logic into route handlers. When database queries, business rules, external API calls, and HTTP response shaping all live in the same function, the code cannot be unit tested, reused in CLI commands or queue workers, or modified without risk of breaking other behavior.

## Incorrect

```typescript
// ❌ Everything in the route handler — spaghetti architecture

app.post('/orders', async (req, res) => {
    // ❌ No input validation before use
    const { userId, items } = req.body;

    // ❌ Database query directly in route
    const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
    if (!user.rows[0]) {
        return res.status(404).json({ error: 'User not found' });
    }

    // ❌ Business logic in route handler
    let total = 0;
    for (const item of items) {
        const product = await db.query(  // ❌ N+1 query in a loop
            'SELECT * FROM products WHERE id = $1', [item.id]
        );
        total += product.rows[0].price * item.quantity;
        await db.query(
            'UPDATE products SET stock = stock - $1 WHERE id = $2',
            [item.quantity, item.id]
        );
    }

    // ❌ Email sending in route handler
    await sendgrid.send({ to: user.rows[0].email, subject: 'Order placed', ... });

    const order = await db.query(
        'INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING *',
        [userId, total]
    );

    res.json(order.rows[0]);
});
```

## Correct

```typescript
// ✅ Clear layer separation: Router → Controller → Service → Repository

// Layer 1: Router — only routing and middleware
// src/routes/orderRoutes.ts
const router = Router();
router.post('/', authenticate, validateBody(CreateOrderSchema), OrderController.create);
export default router;

// Layer 2: Controller — HTTP in/out only, no business logic
// src/controllers/OrderController.ts
export class OrderController {
    static async create(req: Request, res: Response, next: NextFunction) {
        try {
            const order = await OrderService.createOrder(req.body, req.user!.id);
            res.status(201).json(order);
        } catch (error) {
            next(error); // ✅ Delegate to global error handler
        }
    }
}

// Layer 3: Service — business logic, orchestration, no HTTP
// src/services/OrderService.ts
export class OrderService {
    static async createOrder(dto: CreateOrderDto, userId: string): Promise<Order> {
        const user = await UserRepository.findByIdOrThrow(userId);
        const items = await ProductRepository.findManyWithStock(dto.items);

        const total = OrderService.calculateTotal(items, dto.items);
        const order = await OrderRepository.create({ userId, total, items });

        await InventoryService.deductStock(dto.items);
        await EmailService.sendOrderConfirmation(user.email, order);

        return order;
    }

    private static calculateTotal(products: Product[], cartItems: CartItem[]): number {
        return cartItems.reduce((sum, cartItem) => {
            const product = products.find(p => p.id === cartItem.id)!;
            return sum + product.price * cartItem.quantity;
        }, 0);
    }
}

// Layer 4: Repository — data access only
// src/repositories/OrderRepository.ts
export class OrderRepository {
    static async create(data: CreateOrderData): Promise<Order> {
        return prisma.order.create({ data });
    }
}
```

## Layer Compliance Assessment

```
CRITICAL violations:
├── Database queries directly in route handlers (no service/repository layer)
├── External API calls (email, payment, SMS) in route handlers
└── Business logic calculations in route handlers (>10 lines of domain logic)

HIGH violations:
├── Service classes that also accept/return HTTP Request/Response objects
├── Controllers that contain business logic (should only call services)
├── Repositories that contain business rules (should only do data access)
└── Missing service layer entirely (Controller → DB)

MEDIUM violations:
├── Services that directly import other services in circular fashion
├── Repository logic in service files
└── Inconsistent layer naming (some files are services, some are managers, some are helpers)
```

## Directory Structure Signals

```
✅ Well-layered project:
src/
├── routes/          → URL definitions + middleware wiring only
├── controllers/     → HTTP in/out, delegates to services
├── services/        → Business logic, orchestration
├── repositories/    → Data access only
├── middlewares/     → Auth, validation, logging
└── models/          → Entity definitions / Prisma schema

❌ Warning signals:
src/
├── routes/          → Contains 300-line functions with SQL queries
├── helpers/         → A dumping ground for everything that didn't fit elsewhere
└── utils/           → Another dumping ground
// No services/, no repositories/ → all logic collapsed into routes
```

## Why

- **Testability**: `OrderService.createOrder()` can be unit tested without HTTP — impossible when logic is in the route handler
- **Reusability**: The same business logic can be called from a cron job, CLI command, or queue worker — not just HTTP
- **Single Responsibility**: Each layer has one job; changes to HTTP format don't touch business logic
