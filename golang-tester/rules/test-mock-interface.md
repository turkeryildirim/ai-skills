---
title: Mock at the Interface Boundary — Never Mock Concrete Types
impact: CRITICAL
impactDescription: Mocking concrete types tightly couples tests to implementation; tests break when internals change even if behavior is unchanged
tags: testing, mocking, interfaces, testability
---

## Mock at the Interface Boundary

**Impact: CRITICAL — Mocking concrete types couples tests to implementation details**

Define an interface in the consuming package. Implement it in tests as a fake/mock. This means:
1. The interface captures exactly what the consumer needs
2. Tests swap in a fake implementation
3. The real implementation is free to change without breaking tests

## Bad Example

```go
// userservice.go — depends on concrete postgres type
type UserService struct {
    db *postgres.DB  // concrete — cannot be swapped in tests
}

func NewUserService() *UserService {
    db, _ := postgres.Connect(os.Getenv("DATABASE_URL")) // hidden, hardcoded
    return &UserService{db: db}
}

// user_service_test.go — no way to inject a fake
func TestUserService_GetUser(t *testing.T) {
    // Must connect to a real database to test anything
    svc := NewUserService()
    // ...
}
```

## Good Example

```go
// userservice.go — depends on a small interface it owns
type UserStore interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

type UserService struct {
    store UserStore
}

func NewUserService(store UserStore) *UserService {
    return &UserService{store: store}
}

// user_service_test.go — inject a fake, no database needed
type fakeUserStore struct {
    users map[string]*User
}

func (f *fakeUserStore) FindByID(_ context.Context, id string) (*User, error) {
    u, ok := f.users[id]
    if !ok {
        return nil, ErrNotFound
    }
    return u, nil
}

func (f *fakeUserStore) Create(_ context.Context, user *User) error {
    if f.users == nil {
        f.users = make(map[string]*User)
    }
    f.users[user.ID] = user
    return nil
}

func TestUserService_GetUser(t *testing.T) {
    t.Parallel()

    store := &fakeUserStore{
        users: map[string]*User{"1": {ID: "1", Name: "Alice"}},
    }
    svc := NewUserService(store)

    user, err := svc.GetUser(t.Context(), "1")
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}
```

## Interface Design Rules

```go
// Good — small, focused interface; only what UserService needs
type UserStore interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

// Bad — interface mirrors the entire repository, most methods unused by this consumer
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
    List(ctx context.Context, filter UserFilter) ([]*User, error)
    Count(ctx context.Context, filter UserFilter) (int, error)
    // ...20 more methods
}
```

Keep interfaces as small as possible. One to three methods is ideal. If a consumer only calls two methods, define a two-method interface even if the implementation has twenty.

## Compile-Time Interface Check

Verify that your real implementation satisfies the interface at compile time:

```go
// postgres/userstore.go
var _ user.UserStore = (*UserStore)(nil)  // compile error if interface not satisfied
```

## Why

- **Isolation** — unit tests don't need a real database, network, or file system
- **Speed** — fake implementations are orders of magnitude faster than real ones
- **Stability** — tests test behavior, not implementation; refactoring doesn't break tests
- **Clarity** — the interface documents exactly what the consumer needs from its dependencies

Reference: [Effective Go — Interfaces](https://go.dev/doc/effective_go#interfaces) | [Mocking reference](../references/mocking.md)
See also: `golang-tester/references/mocking.md`
