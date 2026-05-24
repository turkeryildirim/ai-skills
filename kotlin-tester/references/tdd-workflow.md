# TDD Workflow Guide

Step-by-step guide to Test-Driven Development for Kotlin/Android projects.

## 1. RED / GREEN / REFACTOR Cycle

The TDD cycle consists of three repeating steps:

| Phase | Action | Duration |
|-------|--------|----------|
| **RED** | Write a failing test that defines the desired behavior | 1–2 minutes |
| **GREEN** | Write the minimal code to make the test pass | 1–2 minutes |
| **REFACTOR** | Clean up code while keeping all tests green | 1–3 minutes |

```
┌─────────┐     ┌─────────┐     ┌───────────┐
│  RED    │────▶│  GREEN  │────▶│ REFACTOR  │
│ (Fails) │     │ (Passes)│     │ (Clean)   │
└─────────┘     └─────────┘     └───────────┘
      ▲                                │
      └────────────────────────────────┘
```

**Rules:**
1. Never write production code except to make a failing test pass.
2. Write only enough of a test to demonstrate a failure.
3. Write only enough production code to pass the test.

## 2. Step-by-Step TDD Example: EmailValidator

### Step 1: Define Interface with TODO

```kotlin
interface EmailValidator {
    fun isValid(email: String): Boolean
}
```

### Step 2: Write Failing Test (RED)

```kotlin
class EmailValidatorTest {

    private val validator = EmailValidatorImpl()

    @Test
    fun `should return true for valid email`() {
        val result = validator.isValid("user@example.com")

        assertTrue(result)
    }
}
```

### Step 3: Run Tests — Verify FAIL

```
EmailValidatorImpl does not exist → COMPILATION ERROR (counts as RED)
```

The test fails because the implementation does not exist yet. This confirms the test exercises the right code path.

### Step 4: Implement Minimal Code (GREEN)

```kotlin
class EmailValidatorImpl : EmailValidator {
    override fun isValid(email: String): Boolean {
        return email.contains("@")
    }
}
```

### Step 5: Run Tests — Verify PASS

```
✅ should return true for valid email — PASSED
```

The simplest implementation that makes the test pass. Not production-ready, but correct for current tests.

### Step 6: Refactor

Current implementation passes but is incomplete. No structural changes needed yet.

### Step 7: Add Next Requirement — Reject Missing Domain

```kotlin
@Test
fun `should return false for email without domain`() {
    val result = validator.isValid("user@")

    assertFalse(result)
}
```

**Run:** This FAILS because `"user@".contains("@")` returns true.

**Fix:**

```kotlin
class EmailValidatorImpl : EmailValidator {
    override fun isValid(email: String): Boolean {
        if (!email.contains("@")) return false
        val parts = email.split("@")
        val domain = parts.getOrElse(1) { "" }
        return domain.contains(".")
    }
}
```

**Run:** All tests PASS.

### Continue the Cycle

```kotlin
@Test
fun `should return false for empty string`() {
    assertFalse(validator.isValid(""))
}

@Test
fun `should return false for email with spaces`() {
    assertFalse(validator.isValid("user @example.com"))
}

@Test
fun `should return true for uppercase email`() {
    assertTrue(validator.isValid("USER@EXAMPLE.COM"))
}

@Test
fun `should return false for email without local part`() {
    assertFalse(validator.isValid("@example.com"))
}
```

### Final Refactored Implementation

```kotlin
class EmailValidatorImpl : EmailValidator {
    private val emailPattern = Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")

    override fun isValid(email: String): Boolean {
        return emailPattern.matches(email)
    }
}
```

All tests still pass after refactoring to a regex-based solution.

## 3. TDD for UseCase

```kotlin
// RED: Write failing test first
class LoginUseCaseTest {

    private val repository = mockk<AuthRepository>()
    private val useCase = LoginUseCase(repository)

    @Test
    fun `should return success with user when credentials are valid`() = runTest {
        val user = User(id = "1", email = "test@example.com")
        coEvery { repository.login("test@example.com", "password") } returns Result.success(user)

        val result = useCase("test@example.com", "password")

        assertTrue(result.isSuccess)
        assertEquals(user, result.getOrNull())
    }
}

// GREEN: Create minimal UseCase
class LoginUseCase(
    private val repository: AuthRepository
) {
    suspend operator fun invoke(email: String, password: String): Result<User> {
        return repository.login(email, password)
    }
}
```

### Add Validation (Next Cycle)

```kotlin
// RED
@Test
fun `should return failure when email is blank`() = runTest {
    val result = useCase("", "password")

    assertTrue(result.isFailure)
    coVerify(exactly = 0) { repository.login(any(), any()) }
}

// GREEN: Add validation
class LoginUseCase(
    private val repository: AuthRepository
) {
    suspend operator fun invoke(email: String, password: String): Result<User> {
        if (email.isBlank()) return Result.failure(ValidationException("Email required"))
        return repository.login(email, password)
    }
}
```

## 4. TDD for ViewModel

```kotlin
// RED: Write failing test
class ProfileViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val getProfileUseCase = mockk<GetProfileUseCase>()
    private lateinit var viewModel: ProfileViewModel

    @Test
    fun `should emit Success state when profile loads`() = runTest {
        val profile = Profile(name = "Türker", email = "turker@example.com")
        coEvery { getProfileUseCase() } returns Result.success(profile)
        viewModel = ProfileViewModel(getProfileUseCase)

        viewModel.uiState.test {
            viewModel.loadProfile()
            skipItems(1) // Skip initial Idle
            assertEquals(ProfileUiState.Loading, awaitItem())

            advanceUntilIdle()
            assertEquals(ProfileUiState.Success(profile), awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }
}

// GREEN: Create ViewModel
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val getProfileUseCase: GetProfileUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Idle)
    val uiState: StateFlow<ProfileUiState> = _uiState

    fun loadProfile() {
        viewModelScope.launch {
            _uiState.value = ProfileUiState.Loading
            when (val result = getProfileUseCase()) {
                is Result.Success -> _uiState.value = ProfileUiState.Success(result.data)
                is Result.Failure -> _uiState.value = ProfileUiState.Error(result.exception.message)
            }
        }
    }
}
```

## 5. When to Apply TDD

| Scenario | Apply TDD? | Reason |
|----------|-----------|--------|
| New feature | Yes | Define behavior before implementation |
| Bug fix | Yes | Write test that reproduces the bug, then fix |
| Refactoring | Yes | Existing tests guard against regressions |
| UseCase / ViewModel logic | Yes | Pure logic is ideal for TDD |
| Repository with complex rules | Yes | Business rules need precise test coverage |
| API integration | Partial | Test parsing/mapping with TDD, integration manually |
| UI Compose | Partial | Test ViewModel with TDD, visual layout manually |

## 6. When NOT to Apply TDD

| Scenario | Skip TDD? | Reason |
|----------|----------|--------|
| Spikes / prototypes | Yes | Rapid exploration, code will be thrown away |
| Exploratory POCs | Yes | Unknown requirements, too early to define tests |
| One-off scripts | Yes | Not worth the investment |
| Third-party API discovery | Yes | Write tests after understanding the API |
| Boilerplate / generated code | Yes | No meaningful behavior to test |
| Simple data class creation | Yes | No logic to drive with tests |

## 7. TDD Anti-Patterns

### Skipping the RED Phase

```kotlin
// WRONG: Writing test after implementation
// This means the test was never verified to fail
// A passing test written after code proves nothing
```

Always run the test and see it fail before writing the implementation.

### Writing All Tests First

```kotlin
// WRONG: Writing 10 tests, then implementing everything
// This is "Test-First", not TDD
// You lose the tight feedback loop
```

Write one test, make it pass, refactor, then write the next test.

### Over-Testing Implementation Details

```kotlin
// WRONG: Testing how the code works, not what it does
@Test
fun `should call repository then cache then analytics`() {
    // This ties tests to implementation order
    // Refactoring will break tests even if behavior is correct
}

// CORRECT: Testing observable behavior
@Test
fun `should return cached data when offline`() {
    // This tests behavior, not implementation
}
```

### Writing Too Much in One Cycle

```kotlin
// WRONG: Giant test covering entire feature
@Test
fun `should handle entire login flow`() {
    // 50 lines testing everything
}

// CORRECT: Small, focused tests
@Test
fun `should return user for valid credentials`() { }

@Test
fun `should return error for invalid password`() { }

@Test
fun `should return error for blank email`() { }
```

### Not Refactoring

```kotlin
// WRONG: Passing tests but messy code
// "It works, I'll clean it later" → later never comes

// CORRECT: Refactor in every cycle
// After GREEN, immediately clean up before writing next test
```

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Skip RED | Test may not actually verify anything | Always see test fail first |
| All tests first | Loses tight feedback loop | One test at a time |
| Test implementation | Tests break on refactor | Test behavior, not how |
| Giant tests | Hard to diagnose failures | One assertion per concept |
| No refactoring | Code rot | Refactor every cycle |
| Skipping GREEN | Over-engineering | Write minimal code to pass |

## Cross References

- Related rules: `test-naming-convention`, `test-given-when-then`, `test-usecase-pattern`, `test-viewmodel-pattern`
- Related references: [`unit-testing.md`](unit-testing.md), [`mocking.md`](mocking.md), [`property-testing.md`](property-testing.md)
