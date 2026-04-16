---
title: Use Dependency Injection for Testable Mocking
impact: HIGH
impactDescription: Over-mocking with vi.mock couples tests to module internals; DI keeps tests focused on behavior.
tags: testing, dependency-injection, vitest, jest, best-practices
---

# Use Dependency Injection for Testable Mocking

Prefer constructor-injected interfaces over module-level mocking. Use `vi.mocked()` for type-safe mock creation.

## Bad Example

```typescript
// Mocking an internal module that the service imports
vi.mock("../repositories/user.repository", () => ({
  UserRepository: vi.fn(() => ({
    findById: vi.fn(),
    create: vi.fn(),
  })),
}));

// Tests are tightly coupled to the module path
it("gets a user", async () => {
  const service = new UserService();
  // Must reach into the mocked module internals
  const { UserRepository } = await import("../repositories/user.repository");
  const mockInstance = new UserRepository();
  vi.mocked(mockInstance.findById).mockResolvedValue({ id: "1" });
});
```

## Good Example

```typescript
// Define an interface for the dependency
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  create(user: User): Promise<User>;
}

// Accept the dependency through the constructor
export class UserService {
  constructor(private userRepository: IUserRepository) {}

  async getUser(id: string): Promise<User> {
    const user = await this.userRepository.findById(id);
    if (!user) {
      throw new Error("User not found");
    }
    return user;
  }
}

// In the test, inject a plain mock object
describe("UserService", () => {
  let service: UserService;
  let mockRepository: IUserRepository;

  beforeEach(() => {
    mockRepository = {
      findById: vi.fn(),
      create: vi.fn(),
    };
    service = new UserService(mockRepository);
  });

  it("should return user if found", async () => {
    const mockUser = { id: "1", name: "John", email: "john@example.com" };
    vi.mocked(mockRepository.findById).mockResolvedValue(mockUser);

    const user = await service.getUser("1");

    expect(user).toEqual(mockUser);
    expect(mockRepository.findById).toHaveBeenCalledWith("1");
  });

  it("should throw error if user not found", async () => {
    vi.mocked(mockRepository.findById).mockResolvedValue(null);

    await expect(service.getUser("999")).rejects.toThrow("User not found");
  });
});
```

## Why

- **Benefit**: Constructor injection lets you pass a simple object as the mock -- no `vi.mock` module patching needed.
- **Benefit**: `vi.mocked()` preserves full type safety, so the compiler catches mismatched mock signatures.
- **Benefit**: Tests depend on the public interface, not the internal import graph, so refactors do not break tests.
