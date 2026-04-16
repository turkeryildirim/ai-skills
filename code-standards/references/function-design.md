---
name: function-design
description: Function design and code organization - small functions, meaningful names, single level of abstraction, early returns.
type: reference
---

# Function Design & Code Organization

## Keep Functions Small

**Target**: < 20 lines per function

```typescript
// ✅ Good - Small, focused functions
export class CreateUserUseCase {
  async execute(dto: CreateUserDto): Promise<User> {
    this.validateDto(dto);
    const user = await this.createUser(dto);
    await this.sendWelcomeEmail(user);
    return user;
  }

  private validateDto(dto: CreateUserDto): void {
    if (!this.isValidEmail(dto.email)) {
      throw new ValidationError("Invalid email");
    }
  }

  private async createUser(dto: CreateUserDto): Promise<User> {
    const hashedPassword = await this.hasher.hash(dto.password);
    return this.repository.save(new User(dto, hashedPassword));
  }

  private async sendWelcomeEmail(user: User): Promise<void> {
    await this.emailService.send(
      user.email,
      "Welcome",
      this.getWelcomeMessage(user.name)
    );
  }

  private getWelcomeMessage(name: string): string {
    return `Welcome to our platform, ${name}!`;
  }
}

// ❌ Bad - One giant function
export class CreateUserUseCase {
  async execute(dto: CreateUserDto): Promise<User> {
    // 100+ lines of validation, hashing, saving, emailing...
    // Hard to test, hard to read, hard to maintain
    return User;
  }
}
```

**Guidelines:**

- Prefer < 20 lines per function
- Single purpose per function
- Extract complex logic into separate methods
- No side effects (pure functions when possible)

## Meaningful Names Over Comments

```typescript
// ❌ Bad - Comments explaining WHAT
export class UserService {
  // Check if user is active and not deleted
  async isValid(u: User): Promise<boolean> {
    return u.a && !u.d;
  }
}

// ✅ Good - Self-documenting code
export class UserService {
  async isActiveAndNotDeleted(user: User): Promise<boolean> {
    return user.isActive && !user.isDeleted;
  }
}

// ✅ Comments explain WHY when needed
export class PaymentService {
  async processPayment(amount: number): Promise<void> {
    // Stripe requires amount in cents, not dollars
    const amountInCents = amount * 100;
    await this.stripe.charge(amountInCents);
  }
}
```

**Comment Guidelines:**

- Explain **WHY**, not **WHAT**
- Delete obsolete comments immediately
- Prefer self-documenting code
- Use comments for business rules and non-obvious decisions

**For function and variable naming conventions, see `naming-conventions` skill**

## Single Level of Abstraction

```typescript
// ✅ Good - Same level of abstraction
async function processOrder(orderId: string): Promise<void> {
  const order = await fetchOrder(orderId);
  validateOrder(order);
  await chargeCustomer(order);
  await sendConfirmation(order);
}

// ❌ Bad - Mixed levels of abstraction
async function processOrder(orderId: string): Promise<void> {
  const order = await db.query("SELECT * FROM orders WHERE id = ?", [orderId]);

  if (!order.items || order.items.length === 0) {
    throw new Error("Invalid order");
  }

  await chargeCustomer(order);

  const html = "<html><body>Order confirmed</body></html>";
  await emailService.send(order.customerEmail, html);
}
```

## Early Returns

```typescript
// ✅ Good - Early returns reduce nesting
function calculateDiscount(user: User, amount: number): number {
  if (!user.isActive) {
    return 0;
  }

  if (amount < 100) {
    return 0;
  }

  if (user.isPremium) {
    return amount * 0.2;
  }

  return amount * 0.1;
}

// ❌ Bad - Deep nesting
function calculateDiscount(user: User, amount: number): number {
  let discount = 0;

  if (user.isActive) {
    if (amount >= 100) {
      if (user.isPremium) {
        discount = amount * 0.2;
      } else {
        discount = amount * 0.1;
      }
    }
  }

  return discount;
}
```
