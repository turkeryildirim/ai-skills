---
title: Prefer Small, Focused Interfaces
impact: HIGH
impactDescription: Small interfaces are easier to implement, mock, and compose
tags: interfaces, design, idiomatic
---

## Prefer Small, Focused Interfaces

**Impact: HIGH — Small interfaces are easier to implement, mock, and compose**

Go interfaces are satisfied implicitly. Prefer interfaces with 1–3 methods. Large interfaces are hard to implement, hard to mock in tests, and couple consumers to implementations they don't need.

## Bad Example

```go
// 12-method interface — almost nothing implements this naturally
type UserRepository interface {
    FindByID(id int) (*User, error)
    FindByEmail(email string) (*User, error)
    FindAll() ([]*User, error)
    Save(u *User) error
    Update(u *User) error
    Delete(id int) error
    Count() (int, error)
    Exists(id int) (bool, error)
    FindActive() ([]*User, error)
    FindByRole(role string) ([]*User, error)
    Paginate(page, size int) ([]*User, error)
    Search(query string) ([]*User, error)
}

// Handler only needs FindByID and Save — forced to depend on 10 unused methods
type UserHandler struct {
    repo UserRepository
}
```

## Good Example

```go
// Interfaces defined at the point of use — only what's needed

type UserFinder interface {
    FindByID(ctx context.Context, id int) (*User, error)
}

type UserSaver interface {
    Save(ctx context.Context, u *User) error
}

// Handler depends only on what it actually uses
type UserHandler struct {
    finder UserFinder
    saver  UserSaver
}

// The concrete repository satisfies both (and more) — no coupling
type PostgresUserRepository struct{ db *sql.DB }

func (r *PostgresUserRepository) FindByID(ctx context.Context, id int) (*User, error) { ... }
func (r *PostgresUserRepository) Save(ctx context.Context, u *User) error { ... }
```

## Why

- **Testability**: A 1-method interface is trivially mocked inline — no generated mocks needed
- **Composability**: Small interfaces combine naturally with embedding
- **Decoupling**: Consumers declare exactly the behaviour they need
- **Go Proverb**: "The bigger the interface, the weaker the abstraction."

Reference: [Effective Go — Interfaces](https://go.dev/doc/effective_go#interfaces) | [Go Proverbs](https://go-proverbs.github.io) | [Best Practices reference](../references/best-practices.md)
See also: `golang/references/best-practices.md`
