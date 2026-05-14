# Go Test Assertions

testify assertions, require vs assert, error checking, and assertion best practices.

## require vs assert

Both packages have the same assertion functions. The difference is what happens on failure:

| Package | On failure | Use for |
|---|---|---|
| `require` | Stops the test immediately (`t.FailNow`) | Preconditions — if this fails, the rest makes no sense |
| `assert` | Records failure, continues test (`t.Fail`) | Independent checks — want to see all failures at once |

```go
import (
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestCreateUser(t *testing.T) {
    user, err := CreateUser(ctx, input)

    require.NoError(t, err)           // stop if error — no point checking user fields
    require.NotNil(t, user)           // stop if nil — can't dereference

    assert.Equal(t, "Alice", user.Name)      // check, but continue
    assert.NotEmpty(t, user.ID)              // check, but continue
    assert.Equal(t, input.Email, user.Email) // check, but continue
}
```

## Common Assertions

### Equality

```go
assert.Equal(t, expected, actual)          // deep equality (uses reflect.DeepEqual internally)
assert.NotEqual(t, expected, actual)
assert.Same(t, expected, actual)           // same pointer
assert.EqualValues(t, expected, actual)    // converts types before comparing
assert.InDelta(t, 100.0, actual, 0.01)    // float comparison with tolerance
assert.InEpsilon(t, 100.0, actual, 0.01)  // relative tolerance
```

### Nil and Empty

```go
assert.Nil(t, value)
assert.NotNil(t, value)
assert.Empty(t, value)      // nil, "", 0, [], {}, false
assert.NotEmpty(t, value)
assert.Zero(t, value)       // zero value for type
assert.NotZero(t, value)
```

### Booleans

```go
assert.True(t, condition, "optional message: %s", detail)
assert.False(t, condition)
```

### Errors

```go
require.Error(t, err)                          // err must be non-nil
require.NoError(t, err)                        // err must be nil
assert.ErrorIs(t, err, ErrNotFound)            // errors.Is(err, target)
assert.ErrorAs(t, err, &myErr)                 // errors.As(err, &target)
assert.EqualError(t, err, "expected message")  // err.Error() == string
assert.ErrorContains(t, err, "partial")        // substring match
```

### Collections

```go
assert.Len(t, collection, 3)
assert.Contains(t, slice, element)      // slice contains element
assert.Contains(t, str, "substring")    // string contains substring
assert.Contains(t, mapVar, key)         // map has key
assert.NotContains(t, slice, element)
assert.ElementsMatch(t, expected, actual) // same elements, any order
assert.Subset(t, list, subset)
assert.IsIncreasing(t, []int{1, 2, 3})
assert.IsDecreasing(t, []int{3, 2, 1})
```

### Types

```go
assert.IsType(t, User{}, actual)
assert.Implements(t, (*io.Reader)(nil), actual)
```

### Panic

```go
assert.Panics(t, func() { MustDo() })
assert.PanicsWithValue(t, "expected message", func() { MustDo() })
assert.NotPanics(t, func() { SafeDo() })
```

### String

```go
assert.Equal(t, expected, actual)
assert.Contains(t, actual, "substring")
assert.Regexp(t, `^\d{4}-\d{2}-\d{2}$`, actual)  // regex match
assert.NotRegexp(t, pattern, actual)
```

## Error Assertion Patterns

```go
// Check for specific sentinel error
require.ErrorIs(t, err, sql.ErrNoRows)

// Check error type and inspect fields
var valErr *ValidationError
require.ErrorAs(t, err, &valErr)
assert.Equal(t, "email", valErr.Field)

// Check wrapped error chain
require.ErrorIs(t, err, ErrUserNotFound)  // works even if err wraps ErrUserNotFound

// Check no error — prefer this over assert.Nil(t, err)
require.NoError(t, err)
```

## Custom Failure Messages

All assertions accept optional format string and args as final parameters:

```go
assert.Equal(t, expected, actual,
    "user %s should have role %s, got %s", userID, expected, actual)

require.NoError(t, err, "failed to create user with input %+v", input)
```

## testify/suite — Test Suites

For groups of tests that share setup/teardown:

```go
import "github.com/stretchr/testify/suite"

type UserServiceSuite struct {
    suite.Suite
    svc  *UserService
    db   *sql.DB
}

// SetupSuite runs once before all tests in the suite
func (s *UserServiceSuite) SetupSuite() {
    s.db = connectTestDB(s.T())
}

// SetupTest runs before each test
func (s *UserServiceSuite) SetupTest() {
    s.svc = NewUserService(s.db, slog.Default())
    // Start transaction for isolation
}

// TearDownTest runs after each test
func (s *UserServiceSuite) TearDownTest() {
    // Rollback transaction
}

func (s *UserServiceSuite) TestCreateUser_WithValidInput() {
    user, err := s.svc.Create(s.T().Context(), validInput)
    s.Require().NoError(err)
    s.Assert().Equal("Alice", user.Name)
}

func (s *UserServiceSuite) TestCreateUser_DuplicateEmail() {
    _, err := s.svc.Create(s.T().Context(), validInput)
    s.Require().NoError(err)

    _, err = s.svc.Create(s.T().Context(), validInput)
    s.Require().Error(err)
    s.Assert().ErrorIs(err, ErrDuplicateEmail)
}

// Run the suite
func TestUserServiceSuite(t *testing.T) {
    suite.Run(t, new(UserServiceSuite))
}
```

## What NOT to Use

```go
// Bad — reflect.DeepEqual gives poor diff output on failure
if !reflect.DeepEqual(expected, actual) { t.Fail() }

// Good — assert.Equal shows a readable diff
assert.Equal(t, expected, actual)

// Bad — assert.Equal for errors loses the stack/context
assert.Equal(t, ErrNotFound, err)

// Good — ErrorIs traverses the error chain
assert.ErrorIs(t, err, ErrNotFound)
```

## assert.ObjectsAreEqual vs assert.Equal

`assert.Equal` uses `ObjectsAreEqual` which handles `[]byte`, numeric type conversions, and time comparison. Prefer `assert.Equal` over manual `==` in tests.

## Quick Reference

```go
// require — fail fast (use for preconditions)
require.NoError(t, err)
require.NotNil(t, result)
require.Len(t, items, 3)
require.ErrorIs(t, err, ErrTarget)

// assert — continue on failure (use for independent checks)
assert.Equal(t, expected, actual)
assert.Contains(t, slice, item)
assert.Empty(t, list)
assert.True(t, condition, "msg: %v", val)
assert.Eventually(t, condition, timeout, tick)
```
