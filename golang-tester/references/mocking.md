# Go Mocking Strategies

Interface-based mocking — inline fakes, gomock, testify/mock. Mock at the interface boundary.

## Core Principle

**Mock interfaces, not concrete types.** Define the interface in the consuming package, implement it in tests. This decouples tests from implementation details.

```go
// UserService depends on an interface it owns
type UserStore interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
}

type UserService struct {
    store  UserStore
    mailer Mailer
    logger *slog.Logger
}
```

## Decision: Which Strategy?

| Scenario | Strategy |
|---|---|
| Simple stub — just return a value or error | Inline fake struct |
| Verify exact call count and argument order | gomock with `EXPECT()` |
| Flexible argument matchers + call count | testify/mock with `On()` |
| Complex stateful behavior | Embedded fake with state |
| External HTTP service | `httptest.NewServer` |
| External database | testcontainers or in-memory SQLite |

## Strategy 1 — Inline Fake (Simplest)

Best for: simple stubs that just need to return values or errors.

```go
// Define the fake in the test file
type fakeUserStore struct {
    users  map[string]*User
    findErr error
}

func (f *fakeUserStore) FindByID(_ context.Context, id string) (*User, error) {
    if f.findErr != nil {
        return nil, f.findErr
    }
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

func (f *fakeUserStore) Delete(_ context.Context, id string) error {
    delete(f.users, id)
    return nil
}

// Use in tests
func TestUserService_GetUser(t *testing.T) {
    t.Parallel()

    store := &fakeUserStore{
        users: map[string]*User{
            "1": {ID: "1", Name: "Alice", Email: "alice@example.com"},
        },
    }
    svc := NewUserService(store, &fakeMailer{}, slog.Default())

    user, err := svc.GetUser(t.Context(), "1")
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}

func TestUserService_GetUser_NotFound(t *testing.T) {
    t.Parallel()

    store := &fakeUserStore{findErr: ErrNotFound}
    svc := NewUserService(store, &fakeMailer{}, slog.Default())

    _, err := svc.GetUser(t.Context(), "999")
    require.ErrorIs(t, err, ErrNotFound)
}
```

## Strategy 2 — gomock (uber-go/mock)

Best for: verifying exact call counts, argument matching, and call ordering.

```bash
go install go.uber.org/mock/mockgen@latest
```

```go
//go:generate mockgen -source=store.go -destination=mocks/mock_store.go -package=mocks
```

```go
import (
    "testing"
    "go.uber.org/mock/gomock"
    "myapp/mocks"
)

func TestUserService_DeleteUser(t *testing.T) {
    t.Parallel()

    ctrl := gomock.NewController(t) // automatically calls ctrl.Finish() via t.Cleanup

    mockStore := mocks.NewMockUserStore(ctrl)

    // Set expectations
    mockStore.EXPECT().
        FindByID(gomock.Any(), "1").
        Return(&User{ID: "1", Name: "Alice"}, nil).
        Times(1)

    mockStore.EXPECT().
        Delete(gomock.Any(), "1").
        Return(nil).
        Times(1)

    svc := NewUserService(mockStore, &fakeMailer{}, slog.Default())

    err := svc.DeleteUser(t.Context(), "1")
    require.NoError(t, err)
    // gomock automatically verifies all expectations were met
}
```

### gomock Argument Matchers

```go
// Exact match
mockStore.EXPECT().FindByID(gomock.Any(), "user-123")

// Any value of the right type
mockStore.EXPECT().Create(gomock.Any(), gomock.Any())

// Custom matcher
mockStore.EXPECT().Create(
    gomock.Any(),
    gomock.AssignableToTypeOf(&User{}),
)

// Multiple matchers with And/Or/Not
mockStore.EXPECT().FindByID(
    gomock.Any(),
    gomock.Not(gomock.Eq("")),
)
```

### gomock Return Values and Errors

```go
// Return value
mockStore.EXPECT().FindByID(gomock.Any(), "1").
    Return(&User{ID: "1"}, nil)

// Return error
mockStore.EXPECT().FindByID(gomock.Any(), "missing").
    Return(nil, ErrNotFound)

// Dynamic return via DoAndReturn
mockStore.EXPECT().Create(gomock.Any(), gomock.Any()).
    DoAndReturn(func(_ context.Context, u *User) error {
        u.ID = "generated-id"
        return nil
    })
```

## Strategy 3 — testify/mock

Best for: flexible call verification with readable `On()` / `AssertExpectations()` syntax.

```go
import "github.com/stretchr/testify/mock"

type MockUserStore struct {
    mock.Mock
}

func (m *MockUserStore) FindByID(ctx context.Context, id string) (*User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserStore) Create(ctx context.Context, user *User) error {
    args := m.Called(ctx, user)
    return args.Error(0)
}

func (m *MockUserStore) Delete(ctx context.Context, id string) error {
    args := m.Called(ctx, id)
    return args.Error(0)
}

// Usage in tests
func TestUserService_WithTestifyMock(t *testing.T) {
    t.Parallel()

    storeMock := &MockUserStore{}

    storeMock.On("FindByID", mock.Anything, "1").
        Return(&User{ID: "1", Name: "Alice"}, nil)

    storeMock.On("Delete", mock.Anything, "1").
        Return(nil)

    svc := NewUserService(storeMock, &fakeMailer{}, slog.Default())

    err := svc.DeleteUser(t.Context(), "1")
    require.NoError(t, err)

    storeMock.AssertExpectations(t)   // verify all On() calls were made
    storeMock.AssertNumberOfCalls(t, "Delete", 1)
}
```

### testify/mock Matchers

```go
// Any value
storeMock.On("Create", mock.Anything, mock.Anything).Return(nil)

// Exact value
storeMock.On("FindByID", mock.Anything, "specific-id").Return(user, nil)

// Custom matcher
storeMock.On("Create", mock.Anything, mock.MatchedBy(func(u *User) bool {
    return u.Email != ""
})).Return(nil)
```

## Mocking HTTP Services

Use `httptest.NewServer` — no need for third-party mock libraries:

```go
func TestAPIClient_FetchUser(t *testing.T) {
    t.Parallel()

    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        assert.Equal(t, "/users/1", r.URL.Path)
        assert.Equal(t, "Bearer test-token", r.Header.Get("Authorization"))

        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(map[string]string{
            "id": "1", "name": "Alice",
        })
    }))
    defer server.Close()

    client := NewAPIClient(server.URL, "test-token")
    user, err := client.FetchUser(t.Context(), "1")
    require.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
}

// Simulate errors
func TestAPIClient_HandleServerError(t *testing.T) {
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusInternalServerError)
    }))
    defer server.Close()

    client := NewAPIClient(server.URL, "token")
    _, err := client.FetchUser(t.Context(), "1")
    require.Error(t, err)
}
```

## Generating Mocks Automatically

### gomock generation

```go
// In the source file
//go:generate mockgen -source=userstore.go -destination=../mocks/mock_userstore.go -package=mocks
```

```bash
go generate ./...
```

### mockery (alternative)

```bash
go install github.com/vektra/mockery/v2@latest
mockery --name=UserStore --output=./mocks --outpkg=mocks
```

## Anti-Patterns

```go
// Bad — mocking concrete type requires field access
type UserService struct {
    db *postgres.Conn // can't swap in tests
}

// Bad — global variable injection (fragile, not thread-safe)
var DefaultStore UserStore = &PostgresStore{}

// Bad — testing internal implementation details
// Tests break when implementation changes but behavior is the same

// Good — inject interface, mock the interface
type UserService struct {
    store UserStore // interface — can be any implementation
}
```
