---
title: require vs assert — Choose Based on Whether the Test Can Continue
impact: HIGH
impactDescription: Using assert when require is needed causes confusing nil pointer panics in the test body after the first failure
tags: testing, testify, require, assert, assertions
---

## require vs assert — Stop on First Failure vs Continue

**Impact: HIGH — Using assert when require is needed causes confusing nil pointer panics after the initial failure**

Both `require` and `assert` have the same function signatures. The difference is what happens when an assertion fails:

- `require` calls `t.FailNow()` — stops the test immediately
- `assert` calls `t.Fail()` — records failure, continues the test

## Bad Example

```go
func TestCreateUser(t *testing.T) {
    user, err := CreateUser(ctx, input)

    assert.NoError(t, err)      // records failure but continues
    assert.NotNil(t, user)      // also continues

    // If err != nil, user is nil — this panics with "nil pointer dereference"
    // even though the real failure was the error above
    assert.Equal(t, "Alice", user.Name) // PANIC
}
```

## Good Example

```go
func TestCreateUser(t *testing.T) {
    user, err := CreateUser(ctx, input)

    // require — if err != nil, stop here; no point checking user fields
    require.NoError(t, err)
    require.NotNil(t, user)

    // assert — independent checks, see all failures at once
    assert.Equal(t, "Alice", user.Name)
    assert.NotEmpty(t, user.ID)
    assert.Equal(t, input.Email, user.Email)
}
```

## Decision Rule

Use `require` when:
- The return value would be nil/zero if the assertion fails (dereference risk)
- The rest of the test makes no sense if this fails
- The assertion is a **precondition** for the test

Use `assert` when:
- The assertions are independent of each other
- You want to see all failures in one test run
- The assertion is about observable behavior, not setup

## The Pattern

```go
// Preconditions: require (fail-fast)
result, err := DoSomething(ctx, input)
require.NoError(t, err)         // stop if error
require.NotNil(t, result)       // stop if nil

// Behavior checks: assert (collect all failures)
assert.Equal(t, expectedID, result.ID)
assert.Equal(t, expectedName, result.Name)
assert.True(t, result.Active)
```

## Suite Usage

In testify suites, use `s.Require()` and `s.Assert()`:

```go
func (s *UserSuite) TestCreateUser() {
    user, err := s.svc.Create(s.T().Context(), validInput)
    s.Require().NoError(err)
    s.Require().NotNil(user)
    s.Assert().Equal("Alice", user.Name)
}
```

Reference: [Testify Assertions](https://github.com/stretchr/testify#assert-package) | [Assertions reference](../references/assertions.md)
See also: `golang-tester/references/assertions.md`
