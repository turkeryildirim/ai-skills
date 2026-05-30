---
name: pragmatic-software-design
description: Language-independent pragmatic software design patterns including defensive coding, guard clauses, Result wrappers, flag parameters, and cognitive complexity reduction.
type: reference
---

# Pragmatic Software Design

Pragmatic software design prioritizes readability, safety, and cognitive ease. These principles are language-independent and apply universally across Object-Oriented, Functional, and Procedural programming.

---

## 1. Defensive Coding & Guard Clauses (Fail-Fast)

**Rule**: Validate inputs at the boundary immediately and return early to keep the execution path flat.

Defensive coding prevents executing expensive operations on invalid data. Rather than nesting large blocks of code inside `if` statements, assert preconditions immediately.

```typescript
// ✅ Good - Clean, flat, fail-fast with Guard Clauses
export class UserService {
  async registerUser(userDto: UserDto): Promise<User> {
    // 1. Guard Clauses (Validate input immediately)
    if (!userDto.email || !userDto.password) {
      throw new ValidationError("Missing required credentials");
    }
    if (userDto.password.length < 8) {
      throw new ValidationError("Password too short");
    }

    // 2. Clear, flat execution path
    const isEmailTaken = await this.repo.existsByEmail(userDto.email);
    if (isEmailTaken) {
      throw new ConflictError("Email already registered");
    }

    const hashedPassword = await this.hasher.hash(userDto.password);
    return this.repo.save(new User(userDto.email, hashedPassword));
  }
}

// ❌ Bad - Heavily nested, hard to trace inputs
export class UserService {
  async registerUser(userDto: UserDto): Promise<User> {
    if (userDto.email && userDto.password) {
      if (userDto.password.length >= 8) {
        const isEmailTaken = await this.repo.existsByEmail(userDto.email);
        if (!isEmailTaken) {
          const hashedPassword = await this.hasher.hash(userDto.password);
          return this.repo.save(new User(userDto.email, hashedPassword));
        } else {
          throw new ConflictError("Email already registered");
        }
      } else {
        throw new ValidationError("Password too short");
      }
    } else {
      throw new ValidationError("Missing required credentials");
    }
  }
}
```

---

## 2. No Exceptions for Control Flow

**Rule**: Use exceptions exclusively for exceptional, unrecoverable, or error conditions, never to direct normal business logic paths.

Using exceptions to route business execution is an anti-pattern. It creates hidden goto jumps, ruins performance, and severely increases cognitive overhead because the reader cannot trace execution statically.

```typescript
// ✅ Good - Use return data values to steer control flow
export class CheckoutService {
  async processOrder(orderId: string): Promise<CheckoutResult> {
    const stockStatus = await this.inventory.checkStock(orderId);
    
    // Return a structured data result to steer logic
    if (stockStatus === StockStatus.OUT_OF_STOCK) {
      return CheckoutResult.failed("Item is currently out of stock");
    }

    await this.payment.charge(orderId);
    return CheckoutResult.success();
  }
}

// ❌ Bad - Throwing business exceptions to steer control flow
export class CheckoutService {
  async processOrder(orderId: string): Promise<void> {
    try {
      await this.inventory.assertStockExists(orderId); // ❌ Throws OutOfStockException
      await this.payment.charge(orderId);
    } catch (e) {
      if (e instanceof OutOfStockException) {
        // ❌ Using exception catching to perform business redirect/flow control
        this.logger.log("Redirecting to out-of-stock screen");
        return;
      }
      throw e;
    }
  }
}
```

---

## 3. Flag Arguments Anti-Pattern

**Rule**: Do not pass boolean "flag" parameters to methods that couple them to multiple unrelated execution paths. Split the function or pass polymorphic strategies instead.

Flag arguments split a function into two (or more) completely distinct behaviors. This reduces readability at the call site and creates tight coupling inside the method body.

```typescript
// ✅ Good - Explicitly split functions or use parameters
export class InvoiceSender {
  async sendInvoice(invoice: Invoice, recipientEmail: string): Promise<void> {
    await this.emailClient.send(recipientEmail, invoice.pdfBytes);
  }

  async sendInvoiceAndArchive(invoice: Invoice, recipientEmail: string): Promise<void> {
    await this.sendInvoice(invoice, recipientEmail);
    await this.archiveSystem.archive(invoice);
  }
}

// Usage at call site:
invoiceSender.sendInvoice(invoice, "user@example.com"); // Clear
invoiceSender.sendInvoiceAndArchive(invoice, "user@example.com"); // Clear

// ❌ Bad - Flag argument forces reader to inspect source code
export class InvoiceSender {
  async sendInvoice(invoice: Invoice, recipientEmail: string, archive: boolean): Promise<void> {
    await this.emailClient.send(recipientEmail, invoice.pdfBytes);
    
    if (archive) { // ❌ Flag controls the inner code path
      await this.archiveSystem.archive(invoice);
    }
  }
}

// Usage at call site:
invoiceSender.sendInvoice(invoice, "user@example.com", false); // What does 'false' mean?
invoiceSender.sendInvoice(invoice, "user@example.com", true); // What does 'true' mean?
```

---

## 4. Explaining Variables (Cognitive Load Reduction)

**Rule**: Break down complex boolean expressions or mathematical equations into well-named local variables that explain their intent.

Complex logical expressions require intense mental compilation. Storing intermediate states in descriptive constants makes the code self-documenting.

```typescript
// ✅ Good - Explaining variables make intent clear
export class SubscriptionManager {
  canRenewSubscription(user: User, subscription: Subscription): boolean {
    const isPremiumUser = user.tier === Tier.PREMIUM;
    const isSubscriptionActive = subscription.status === Status.ACTIVE;
    const hasValidPaymentMethod = user.paymentMethods.length > 0;
    const isPastDueDate = subscription.nextBillingDate < new Date();

    return (isPremiumUser || isSubscriptionActive) && hasValidPaymentMethod && isPastDueDate;
  }
}

// ❌ Bad - Readers must parse a massive logic string
export class SubscriptionManager {
  canRenewSubscription(user: User, subscription: Subscription): boolean {
    return (
      (user.tier === "premium" || subscription.status === "active") &&
      user.paymentMethods.length > 0 &&
      subscription.nextBillingDate < new Date()
    ); // ❌ Cognitive overload
  }
}
```

---

## 5. Data-Oriented Programming (DOP) vs Object-Oriented (OOP)

**Rule**: Know when to encapsulate data and behavior together (OOP/TDA) versus keeping data structures completely immutable and using pure functions (DOP/Functional).

- **Use OOP (Tell, Don't Ask)** when you are managing rich, complex state machines or domain logic that requires strict encapsulation and data integrity rules.
- **Use DOP (Pure Functions & Data Models)** when you are writing stateless transformations, processing API payloads, mapping DTOs, or handling database queries where simple, immutable data records are safest.

```typescript
// ✅ DOP: Pure transformations on immutable records (Extremely safe for APIs and Pipelines)
export interface OrderItem {
  readonly price: number;
  readonly quantity: number;
}

export interface Order {
  readonly items: readonly OrderItem[];
  readonly discountCode?: string;
}

// Pure function: predictable, easy to unit test, no side-effects
export function calculateOrderTotal(order: Order): number {
  const subTotal = order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  if (order.discountCode === "SAVE10") {
    return subTotal * 0.9;
  }
  return subTotal;
}
```
