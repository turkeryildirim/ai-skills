---
title: Dependency Injection over Hardcoded Imports
impact: HIGH
impactDescription: Hardcoded dependencies make classes untestable and tightly coupled to concrete implementations.
tags: di, testing, coupling, express
---

# Dependency Injection over Hardcoded Imports

Use constructor injection and a lightweight DI container instead of creating dependencies inside classes or relying on module-level singletons.

## Bad Example

```typescript
// Hardcoded dependency — impossible to swap or mock
import { pool } from "../config/database";
import { EmailService } from "../services/email.service";

export class UserService {
  private emailService = new EmailService(); // tight coupling

  async createUser(data: CreateUserDTO) {
    const result = await pool.query(       // hidden global dependency
      "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
      [data.name, data.email],
    );
    await this.emailService.sendWelcome(data.email);
    return result.rows[0];
  }
}
```

## Good Example

```typescript
// Constructor injection — dependencies are explicit and swappable
export class UserService {
  constructor(
    private userRepo: UserRepository,
    private emailService: EmailService,
  ) {}

  async createUser(data: CreateUserDTO) {
    const user = await this.userRepo.create(data);
    await this.emailService.sendWelcome(user.email);
    return user;
  }
}

// Lightweight DI container wires everything together
class Container {
  private instances = new Map<string, any>();

  register<T>(key: string, factory: () => T): void {
    this.instances.set(key, factory);
  }

  resolve<T>(key: string): T {
    const factory = this.instances.get(key);
    if (!factory) throw new Error(`No factory registered for ${key}`);
    return factory();
  }

  singleton<T>(key: string, factory: () => T): void {
    let instance: T;
    this.instances.set(key, () => {
      if (!instance) instance = factory();
      return instance;
    });
  }
}

// Composition root — single place where wiring happens
container.singleton("userRepo", () => new UserRepository(container.resolve("db")));
container.singleton("userService", () => new UserService(
  container.resolve("userRepo"),
  container.resolve("emailService"),
));
```

## Why

- **Benefit**: Constructor parameters make every dependency explicit, so readers immediately know what a class needs.
- **Benefit**: Tests can pass mocks or fakes without monkey-patching module imports or relying on module-level state.
- **Benefit**: The container centralises wiring in one composition root, preventing scattered `new` calls that are hard to track and replace.
