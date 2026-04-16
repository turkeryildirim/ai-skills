---
name: solid-principles
description: Detailed SOLID principles (SRP, OCP, LSP, ISP, DIP) with TypeScript examples and checklists.
type: reference
---

# SOLID Principles (OOP Design)

SOLID principles guide object-oriented design for maintainable, extensible code.

## 1. Single Responsibility Principle (SRP)

**Rule**: One reason to change per class/module

**Application**:

```typescript
// ✅ Good - Single responsibility
export class UserPasswordHasher {
  hash(password: string): Promise<string> {
    return bcrypt.hash(password, 10);
  }

  verify(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }
}

export class UserValidator {
  validate(user: CreateUserDto): ValidationResult {
    // Only validation logic
  }
}

// ❌ Bad - Multiple responsibilities
export class UserService {
  hash(password: string) {
    /* ... */
  }
  validate(user: User) {
    /* ... */
  }
  sendEmail(user: User) {
    /* ... */
  }
  saveToDatabase(user: User) {
    /* ... */
  }
}
```

**Checklist**:

- [ ] Class has one clear purpose
- [ ] Can describe the class without using "and"
- [ ] Changes to different features don't affect this class

## 2. Open/Closed Principle (OCP)

**Rule**: Open for extension, closed for modification

**Application**:

```typescript
// ✅ Good - Extensible without modification
export interface NotificationChannel {
  send(message: string, recipient: string): Promise<void>;
}

export class EmailNotification implements NotificationChannel {
  async send(message: string, recipient: string): Promise<void> {
    // Email implementation
  }
}

export class SmsNotification implements NotificationChannel {
  async send(message: string, recipient: string): Promise<void> {
    // SMS implementation
  }
}

export class NotificationService {
  constructor(private channels: NotificationChannel[]) {}

  async notify(message: string, recipient: string): Promise<void> {
    await Promise.all(
      this.channels.map((channel) => channel.send(message, recipient))
    );
  }
}

// ❌ Bad - Requires modification for new features
export class NotificationService {
  async notify(
    message: string,
    recipient: string,
    type: "email" | "sms"
  ): Promise<void> {
    if (type === "email") {
      // Email logic
    } else if (type === "sms") {
      // SMS logic
    }
    // Adding push notification requires modifying this method
  }
}
```

**Checklist**:

- [ ] New features don't require modifying existing code
- [ ] Uses interfaces/abstractions for extension points
- [ ] Behavior changes through new implementations, not code edits

## 3. Liskov Substitution Principle (LSP)

**Rule**: Subtypes must be substitutable for base types

**Application**:

```typescript
// ✅ Good - Maintains contract
export abstract class PaymentProcessor {
  abstract process(amount: number): Promise<PaymentResult>;
}

export class StripePaymentProcessor extends PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // Always returns PaymentResult, never throws unexpected errors
    try {
      const result = await this.stripe.charge(amount);
      return { success: true, transactionId: result.id };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// ❌ Bad - Breaks parent contract
export class PaypalPaymentProcessor extends PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    if (amount > 10000) {
      throw new Error("Amount too high"); // Unexpected behavior!
    }
    // Different behavior than parent contract
  }
}
```

**Checklist**:

- [ ] Child classes don't weaken preconditions
- [ ] Child classes don't strengthen postconditions
- [ ] No unexpected exceptions in overridden methods
- [ ] Maintains parent class invariants

## 4. Interface Segregation Principle (ISP)

**Rule**: Small, focused interfaces over large ones

**Application**:

```typescript
// ✅ Good - Segregated interfaces
export interface Readable {
  read(id: string): Promise<User | null>;
}

export interface Writable {
  create(user: User): Promise<void>;
  update(user: User): Promise<void>;
}

export interface Deletable {
  delete(id: string): Promise<void>;
}

// Repositories implement only what they need
export class ReadOnlyUserRepository implements Readable {
  async read(id: string): Promise<User | null> {
    // Implementation
  }
}

export class FullUserRepository implements Readable, Writable, Deletable {
  // Implements all operations
}

// ❌ Bad - Fat interface
export interface UserRepository {
  read(id: string): Promise<User | null>;
  create(user: User): Promise<void>;
  update(user: User): Promise<void>;
  delete(id: string): Promise<void>;
  archive(id: string): Promise<void>;
  restore(id: string): Promise<void>;
  // Forces all implementations to have all methods
}
```

**Checklist**:

- [ ] Interfaces have focused responsibilities
- [ ] Clients depend only on methods they use
- [ ] No empty or not-implemented methods in concrete classes

## 5. Dependency Inversion Principle (DIP)

**Rule**: Depend on abstractions, not concretions

**Application**:

```typescript
// ✅ Good - Depends on abstraction
export interface UserRepository {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
}

export class CreateUserUseCase {
  constructor(private userRepository: UserRepository) {}

  async execute(data: CreateUserDto): Promise<User> {
    const user = new User(data);
    await this.userRepository.save(user);
    return user;
  }
}

// ❌ Bad - Depends on concrete implementation
export class CreateUserUseCase {
  constructor(private postgresUserRepository: PostgresUserRepository) {}

  async execute(data: CreateUserDto): Promise<User> {
    // Tightly coupled to PostgreSQL implementation
    const user = new User(data);
    await this.postgresUserRepository.insertIntoPostgres(user);
    return user;
  }
}
```

**Checklist**:

- [ ] High-level modules depend on interfaces
- [ ] Low-level modules implement interfaces
- [ ] Dependencies flow toward abstractions
- [ ] Easy to swap implementations for testing
