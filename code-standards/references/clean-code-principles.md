---
name: clean-code-principles
description: KISS, YAGNI, DRY, TDA principles with TypeScript examples, checklists, and when (not) to apply.
type: reference
---

# Clean Code Principles (Simplicity & Pragmatism)

Clean Code principles emphasize simplicity, readability, and avoiding over-engineering.

## KISS - Keep It Simple, Stupid

**Rule**: Simplicity is the ultimate sophistication

**Application:**

```typescript
// ✅ Good - Simple and clear
export class PasswordValidator {
  validate(password: string): boolean {
    return (
      password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)
    );
  }
}

// ❌ Bad - Over-engineered
export class PasswordValidator {
  private rules: ValidationRule[] = [];
  private ruleEngine: RuleEngine;
  private strategyFactory: StrategyFactory;
  private policyManager: PolicyManager;

  validate(password: string): ValidationResult {
    return this.ruleEngine
      .withStrategy(this.strategyFactory.create("password"))
      .withPolicy(this.policyManager.getDefault())
      .applyRules(this.rules)
      .execute(password);
  }
}
```

**When KISS applies:**

- Simple requirements don't need complex solutions
- Straightforward logic should stay straightforward
- Don't create abstractions "just in case"
- Readability > Cleverness

**Checklist:**

- [ ] Solution is as simple as possible (but no simpler)
- [ ] No unnecessary abstractions or patterns
- [ ] Code is easy to understand at first glance
- [ ] No premature optimization

## YAGNI - You Aren't Gonna Need It

**Rule**: Build only what you need right now

**Application:**

```typescript
// ✅ Good - Build only what's needed NOW
export class UserService {
  async createUser(dto: CreateUserDto): Promise<User> {
    return this.repository.save(new User(dto));
  }
}

// ❌ Bad - Building for imaginary future needs
export class UserService {
  // We don't need these yet!
  async createUser(dto: CreateUserDto): Promise<User> {}
  async createUserBatch(dtos: CreateUserDto[]): Promise<User[]> {}
  async createUserWithRetry(
    dto: CreateUserDto,
    maxRetries: number
  ): Promise<User> {}
  async createUserAsync(dto: CreateUserDto): Promise<JobId> {}
  async createUserWithCallback(
    dto: CreateUserDto,
    callback: Function
  ): Promise<void> {}
  async createUserWithHooks(dto: CreateUserDto, hooks: Hooks): Promise<User> {}
}
```

**When YAGNI applies:**

- Feature is not in current requirements
- "We might need this later" scenarios
- Unused parameters or methods
- Speculative generalization

**Checklist:**

- [ ] Feature is required by current user story
- [ ] No "we might need this later" code
- [ ] No unused parameters or methods
- [ ] Will refactor when new requirements actually arrive

## DRY - Don't Repeat Yourself

**Rule**: Apply abstraction after seeing duplication 3 times (Rule of Three)

**Application:**

```typescript
// ✅ Good - Meaningful abstraction after Rule of Three
export class DateFormatter {
  formatToISO(date: Date): string {
    return date.toISOString();
  }

  formatToDisplay(date: Date): string {
    return date.toLocaleDateString("en-US");
  }

  formatToRelative(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    return `${days} days ago`;
  }
}

// Used in 3+ places
const isoDate = dateFormatter.formatToISO(user.createdAt);

// ❌ Bad - Premature abstraction
// Don't abstract after seeing duplication just ONCE
// Wait for the Rule of Three (3 occurrences)

// ❌ Bad - Wrong abstraction
export class StringHelper {
  doSomething(str: string, num: number, bool: boolean): string {
    // Forcing unrelated code into one function
  }
}
```

**When DRY applies:**

- Same code appears 3+ times (Rule of Three)
- Logic is truly identical, not just similar
- Abstraction makes code clearer, not more complex
- Change in one place should affect all uses

**When NOT to apply DRY:**

- Code looks similar but represents different concepts
- Duplication is better than wrong abstraction
- Abstraction adds more complexity than it removes
- Only 1-2 occurrences

**Checklist:**

- [ ] Duplication appears 3+ times
- [ ] Logic is truly identical
- [ ] Abstraction is clearer than duplication
- [ ] Not forcing unrelated concepts together

## TDA - Tell, Don't Ask

**Rule**: Tell objects what to do, don't ask for data and make decisions

**Application:**

```typescript
// ✅ Good - Tell the object what to do
export class User {
  private _isActive: boolean = true;
  private _failedLoginAttempts: number = 0;

  deactivate(): void {
    if (!this._isActive) {
      throw new Error("User already inactive");
    }
    this._isActive = false;
    this.logDeactivation();
  }

  recordFailedLogin(): void {
    this._failedLoginAttempts++;
    if (this._failedLoginAttempts >= 5) {
      this.lock();
    }
  }

  private lock(): void {
    this._isActive = false;
    this.logLockout();
  }

  private logDeactivation(): void {
    console.log(`User ${this.id} deactivated`);
  }

  private logLockout(): void {
    console.log(`User ${this.id} locked due to failed login attempts`);
  }
}

// Usage - Tell it what to do
user.deactivate();
user.recordFailedLogin();

// ❌ Bad - Ask for data and make decisions
export class User {
  get isActive(): boolean {
    return this._isActive;
  }

  set isActive(value: boolean) {
    this._isActive = value;
  }

  get failedLoginAttempts(): number {
    return this._failedLoginAttempts;
  }

  set failedLoginAttempts(value: number) {
    this._failedLoginAttempts = value;
  }
}

// Usage - Asking and deciding externally
if (user.isActive) {
  user.isActive = false;
  console.log(`User ${user.id} deactivated`);
}

if (user.failedLoginAttempts >= 5) {
  user.isActive = false;
  console.log(`User ${user.id} locked`);
}
```

**When TDA applies:**

- Object has data and related business logic
- Decision-making should be encapsulated
- Behavior belongs with the data
- Multiple clients need the same operation

**Benefits:**

- Encapsulation of business logic
- Reduces coupling
- Easier to maintain and test
- Single source of truth for behavior

**Checklist:**

- [ ] Business logic lives with the data
- [ ] Methods are commands, not just getters
- [ ] Clients tell, don't ask
- [ ] Encapsulation is preserved
