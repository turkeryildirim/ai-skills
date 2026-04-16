---
name: anti-patterns-and-examples
description: Common anti-patterns (god classes, premature optimization, clever code, magic numbers) and complete example applying all principles.
type: reference
---

# Common Anti-Patterns

## God Classes

```typescript
// ❌ Classes doing too much (violates SRP)
export class UserService {
  validateUser() {}
  hashPassword() {}
  sendEmail() {}
  saveToDatabase() {}
  generateReport() {}
  processPayment() {}
}
```

## Premature Optimization

```typescript
// ❌ Don't optimize before measuring
const cache = new Map<string, User>();
const lruCache = new LRUCache<string, User>(1000);
const bloomFilter = new BloomFilter();

// ✅ Start simple, optimize when needed
const users = await repository.findAll();
```

## Clever Code

```typescript
// ❌ Clever but unreadable
const result = arr.reduce((a, b) => a + (b.active ? 1 : 0), 0);

// ✅ Clear and boring
const activeCount = users.filter((user) => user.isActive).length;
```

## Magic Numbers

```typescript
// ❌ Magic numbers
if (user.age > 18 && order.amount < 1000) {
  // ...
}

// ✅ Named constants
const MINIMUM_AGE = 18;
const MAXIMUM_ORDER_AMOUNT = 1000;

if (user.age > MINIMUM_AGE && order.amount < MAXIMUM_ORDER_AMOUNT) {
  // ...
}
```

# Complete Example: Applying All Principles

```typescript
// SRP + DIP: Each class has one responsibility, depends on abstractions
export interface Logger {
  log(message: string): void;
}

export interface UserRepository {
  save(user: User): Promise<void>;
  findByEmail(email: string): Promise<User | null>;
}

export interface PasswordHasher {
  hash(password: string): Promise<string>;
}

export interface EmailSender {
  send(to: string, subject: string, body: string): Promise<void>;
}

// OCP: Open for extension (new implementations)
export class ConsoleLogger implements Logger {
  log(message: string): void {
    console.log(message);
  }
}

// ISP: Focused interfaces
// Each interface has a single, focused responsibility

// KISS: Simple, clear implementation
export class CreateUserUseCase {
  constructor(
    private userRepository: UserRepository,
    private passwordHasher: PasswordHasher,
    private logger: Logger,
    private emailSender: EmailSender
  ) {}

  // KISS + Small Functions: < 20 lines, single responsibility
  async execute(data: CreateUserDto): Promise<User> {
    this.logger.log("Creating new user");

    // YAGNI: Only what's needed now
    await this.validateEmail(data.email);
    const user = await this.createUser(data);
    await this.sendWelcomeEmail(user);

    this.logger.log("User created successfully");
    return user;
  }

  // DRY: Extracted after Rule of Three
  private async validateEmail(email: string): Promise<void> {
    const existing = await this.userRepository.findByEmail(email);
    if (existing) {
      throw new Error(`User with email ${email} already exists`);
    }
  }

  private async createUser(data: CreateUserDto): Promise<User> {
    const hashedPassword = await this.passwordHasher.hash(data.password);
    const user = new User({ ...data, password: hashedPassword });
    await this.userRepository.save(user);
    return user;
  }

  private async sendWelcomeEmail(user: User): Promise<void> {
    await this.emailSender.send(
      user.email,
      "Welcome",
      this.getWelcomeMessage(user.name)
    );
  }

  // Self-documenting: Clear name, no comments needed
  private getWelcomeMessage(name: string): string {
    return `Welcome to our platform, ${name}!`;
  }
}

// LSP: Implementations are substitutable
export class BcryptPasswordHasher implements PasswordHasher {
  async hash(password: string): Promise<string> {
    return bcrypt.hash(password, 10);
  }
}

export class ArgonPasswordHasher implements PasswordHasher {
  async hash(password: string): Promise<string> {
    return argon2.hash(password);
  }
}
```
