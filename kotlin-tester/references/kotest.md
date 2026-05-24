# Kotest Testing Framework for Kotlin/KMP

Expert guidance for writing tests with Kotest — a flexible, multi-style testing framework for Kotlin and Kotlin Multiplatform projects.

## 1. Setup Dependencies

```kotlin
dependencies {
    testImplementation("io.kotest:kotest-runner-junit5:5.9.1")
    testImplementation("io.kotest:kotest-assertions-core:5.9.1")
    testImplementation("io.kotest:kotest-property:5.9.1")
    testImplementation("io.mockk:mockk:1.13.12")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
}
```

| Library | Purpose |
|---------|---------|
| kotest-runner-junit5 | Test engine, spec styles, lifecycle |
| kotest-assertions-core | Matchers (shouldBe, shouldThrow, etc.) |
| kotest-property | Property-based testing |
| MockK | Kotlin-native mocking |
| coroutines-test | runTest, TestDispatcher for coroutine tests |

**build.gradle.kts** — ensure JUnit Platform is used:

```kotlin
tasks.withType<Test>().configureEach {
    useJUnitPlatform()
}
```

## 2. Spec Styles

Kotest provides multiple spec styles. Pick one per project and stay consistent.

### StringSpec

Simplest style — test names as raw strings.

```kotlin
import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe

class StringUtilsTest : StringSpec({
    "should concatenate two strings" {
        "hello" + " world" shouldBe "hello world"
    }

    "should return true for empty string" {
        "".isEmpty() shouldBe true
    }

    "should reverse a string" {
        "abc".reversed() shouldBe "cba"
    }
})
```

### FunSpec

JUnit-like style with `test("name") { }` blocks.

```kotlin
import io.kotest.core.spec.style.FunSpec
import io.kotest.matchers.shouldBe

class CalculatorTest : FunSpec({
    test("should add two numbers") {
        2 + 3 shouldBe 5
    }

    test("should subtract two numbers") {
        10 - 4 shouldBe 6
    }

    context("multiplication") {
        test("should multiply positive numbers") {
            3 * 4 shouldBe 12
        }

        test("should return zero when multiplying by zero") {
            5 * 0 shouldBe 0
        }
    }
})
```

### BehaviorSpec

BDD-style with Given/When/Then structure.

```kotlin
import io.kotest.core.spec.style.BehaviorSpec
import io.kotest.matchers.shouldBe

class LoginUseCaseTest : BehaviorSpec({
    given("a login use case") {
        val repository = mockk<UserRepository>()
        val useCase = LoginUseCase(repository)

        `when`("valid credentials are provided") {
            coEvery { repository.login("user@test.com", "pass123") } returns
                Result.success(User("1", "user@test.com"))

            then("should return success with user") {
                val result = useCase("user@test.com", "pass123")
                result.isSuccess shouldBe true
                result.getOrNull()?.email shouldBe "user@test.com"
            }
        }

        `when`("invalid credentials are provided") {
            coEvery { repository.login(any(), any()) } returns
                Result.failure(AuthException("Invalid credentials"))

            then("should return failure") {
                val result = useCase("user@test.com", "wrong")
                result.isFailure shouldBe true
            }
        }
    }
})
```

### DescribeSpec

RSpec-style with describe/context/it blocks.

```kotlin
import io.kotest.core.spec.style.DescribeSpec
import io.kotest.matchers.shouldBe

class EmailValidatorTest : DescribeSpec({
    describe("EmailValidator") {
        val validator = EmailValidator()

        context("valid email addresses") {
            it("should accept standard email") {
                validator.isValid("user@example.com") shouldBe true
            }

            it("should accept email with subdomain") {
                validator.isValid("user@mail.example.com") shouldBe true
            }
        }

        context("invalid email addresses") {
            it("should reject missing @") {
                validator.isValid("userexample.com") shouldBe false
            }

            it("should reject empty string") {
                validator.isValid("") shouldBe false
            }
        }
    }
})
```

| Spec Style | Structure | Best For |
|------------|-----------|----------|
| StringSpec | `"test name" { }` | Simple unit tests, quick scripts |
| FunSpec | `test("name") { }` + `context { }` | General purpose, JUnit migrants |
| BehaviorSpec | `given` / `when` / `then` | BDD-style, use case tests |
| DescribeSpec | `describe` / `context` / `it` | RSpec fans, hierarchical tests |

## 3. Matchers

### Core Matchers

```kotlin
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import io.kotest.matchers.strings.shouldStartWith
import io.kotest.matchers.strings.shouldEndWith
import io.kotest.matchers.strings.shouldContain
import io.kotest.matchers.string.shouldMatch

"name" shouldBe "name"
a shouldNotBe b
"hello world" shouldStartWith "hello"
"hello world" shouldEndWith "world"
"hello world" shouldContain "lo wo"
"2024-01-15" shouldMatch "\\d{4}-\\d{2}-\\d{2}".toRegex()
```

### Collection Matchers

```kotlin
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.collections.shouldBeSorted
import io.kotest.matchers.collections.shouldContainAll
import io.kotest.matchers.collections.shouldBeEmpty

listOf(1, 2, 3) shouldHaveSize 3
listOf(1, 2, 3) shouldBeSorted true
listOf(1, 2, 3, 4) shouldContainAll listOf(2, 3)
emptyList<Int>() shouldBeEmpty
```

### Null Matchers

```kotlin
import io.kotest.matchers.nulls.shouldNotBeNull
import io.kotest.matchers.nulls.shouldBeNull

val result: String? = fetchValue()
result shouldNotBeNull
result shouldBe "expected"

val missing: String? = fetchMissing()
missing shouldBeNull
```

### Type Matchers

```kotlin
import io.kotest.matchers.types.shouldBeInstanceOf

val animal: Animal = Dog("Rex")
animal shouldBeInstanceOf<Dog>
```

### Number Matchers

```kotlin
import io.kotest.matchers.numbers.shouldBeGreaterThan
import io.kotest.matchers.numbers.shouldBeInRange

42 shouldBeGreaterThan 10
5 shouldBeInRange 1..10
```

### Exception Matchers

```kotlin
import io.kotest.assertions.throwables.shouldThrow
import io.kotest.assertions.throwables.shouldNotThrow

shouldThrow<IllegalArgumentException> {
    validator.validate(-1)
}

shouldThrow<IOException> {
    service.fetchData()
}

shouldNotThrow<Exception> {
    calculator.add(1, 2)
}

val exception = shouldThrow<ValidationException> {
    service.process(invalidInput)
}
exception.message shouldBe "Input cannot be blank"
```

### Custom Matchers

```kotlin
import io.kotest.matchers.Matcher
import io.kotest.matchers.MatcherResult
import io.kotest.matchers.should

fun beValidEmail() = object : Matcher<String> {
    override fun test(value: String) = MatcherResult(
        passed = value.contains("@") && value.contains("."),
        failureMessageFn = { "\"$value\" is not a valid email address" },
        negatedFailureMessageFn = { "\"$value\" should not be a valid email address" }
    )
}

"user@example.com" should beValidEmail()
```

## 4. MockK Integration

MockK works with Kotest the same way as with JUnit. Clear mocks in `beforeTest` to avoid state leakage between tests.

```kotlin
import io.kotest.core.spec.style.FunSpec
import io.mockk.clearMocks
import io.mockk.coEvery
import io.mockk.mockk
import io.mockk.verify

class OrderServiceTest : FunSpec({
    val repository = mockk<OrderRepository>()
    val service = OrderService(repository)

    beforeTest {
        clearMocks(repository)
    }

    test("should create order and call repository") {
        coEvery { repository.save(any()) } returns Order(id = "1", total = 100.0)

        val order = service.createOrder(listOf(Item("A", 100.0)))

        verify(exactly = 1) { repository.save(any()) }
    }

    test("should return order by id") {
        val expected = Order(id = "42", total = 50.0)
        coEvery { repository.findById("42") } returns expected

        service.getOrder("42") shouldBe expected
    }
})
```

## 5. Coroutine Testing

Use `runTest` from kotlinx-coroutines-test inside Kotest specs for suspend function testing.

```kotlin
import io.kotest.core.spec.style.FunSpec
import kotlinx.coroutines.test.runTest

class UserRepositoryTest : FunSpec({
    val api = mockk<UserApi>()
    val repository = UserRepositoryImpl(api)

    test("should fetch user from api") {
        runTest {
            coEvery { api.getUser("1") } returns User("1", "Alice")

            val result = repository.fetchUser("1")

            result shouldBe User("1", "Alice")
        }
    }

    test("should emit loading then data") {
        runTest {
            val flow = repository.observeUser("1")

            flow.test {
                awaitItem() shouldBe Resource.Loading
                awaitItem() shouldBe Resource.Success(User("1", "Alice"))
                awaitComplete()
            }
        }
    }
})
```

Coroutine test mode can be set at spec level:

```kotlin
class CoroutineSpec : FunSpec({
    coroutineTestScope = true

    test("runs in test coroutine scope") {
        runTest {
            delay(1000)
        }
    }
})
```

## 6. Test Lifecycle

Kotest provides lifecycle callbacks at both spec and individual test levels.

```kotlin
import io.kotest.core.spec.style.FunSpec
import io.kotest.core.spec.IsolationMode

class LifecycleExampleTest : FunSpec({
    isolationMode = IsolationMode.InstancePerTest

    beforeSpec {
        println("Runs once before all tests in this spec")
    }

    afterSpec {
        println("Runs once after all tests in this spec")
    }

    beforeTest {
        println("Runs before each test")
    }

    afterTest {
        println("Runs after each test")
    }

    beforeEach {
        println("Alias for beforeTest — runs before each leaf test")
    }

    afterEach {
        println("Alias for afterTest — runs after each leaf test")
    }

    test("first test") {
        1 shouldBe 1
    }

    test("second test") {
        2 shouldBe 2
    }
})
```

| Callback | Scope | Runs |
|----------|-------|------|
| `beforeSpec` / `afterSpec` | Entire spec class | Once |
| `beforeTest` / `afterTest` | Each test (including nested) | Per test |
| `beforeEach` / `afterEach` | Each leaf test only | Per leaf test |
| `beforeProject` / `afterProject` | Project-wide | Once per test run |

### Isolation Modes

```kotlin
class IsolatedTest : FunSpec({
    isolationMode = IsolationMode.InstancePerTest
})
```

| Mode | Behavior |
|------|----------|
| `SingleInstance` | Default — one spec instance for all tests |
| `InstancePerTest` | New spec instance per leaf test (fresh state) |
| `InstancePerLeaf` | New instance per leaf test in nested hierarchies |

## 7. Kotest Extensions

Extensions allow hooking into the test lifecycle externally.

```kotlin
import io.kotest.core.extensions.BeforeSpecListener
import io.kotest.core.extensions.AfterSpecListener
import io.kotest.core.spec.Spec

class DatabaseExtension : BeforeSpecListener, AfterSpecListener {
    override suspend fun beforeSpec(spec: Spec) {
        Database.connect("jdbc:h2:mem:test")
        Database.runMigrations()
    }

    override suspend fun afterSpec(spec: Spec) {
        Database.close()
    }
}

class RepositoryTest : FunSpec({
    register(DatabaseExtension())

    test("should query database") {
        Database.query("SELECT 1") shouldNotBeNull
    }
})
```

### Project-Level Extensions

Register in `ProjectConfig`:

```kotlin
import io.kotest.core.config.AbstractProjectConfig
import io.kotest.core.extensions.Extension

object ProjectConfig : AbstractProjectConfig() {
    override fun extensions(): List<Extension> = listOf(
        DatabaseExtension(),
        LoggingExtension()
    )

    override val parallelism = 2
}
```

## 8. Data-Driven Testing

Use `withData` to parameterize tests over sets of inputs.

```kotlin
import io.kotest.core.spec.style.StringSpec
import io.kotest.datatest.withData
import io.kotest.matchers.shouldBe

class MathTest : StringSpec({
    withData(
        nameFn = { (a, b, expected) -> "$a + $b = $expected" },
        Triple(1, 2, 3),
        Triple(0, 0, 0),
        Triple(-1, 1, 0),
        Triple(100, 200, 300)
    ) { (a, b, expected) ->
        (a + b) shouldBe expected
    }
})
```

### Named Data Classes

```kotlin
data class IsEvenTest(val input: Int, val expected: Boolean)

class EvenNumberTest : FunSpec({
    context("isEven") {
        withData(
            IsEvenTest(2, true),
            IsEvenTest(3, false),
            IsEvenTest(0, true),
            IsEvenTest(-4, true)
        ) { (input, expected) ->
            input.isEven() shouldBe expected
        }
    }
})
```

### Table-Driven Tests

```kotlin
import io.kotest.core.spec.style.StringSpec
import io.kotest.datatest.withData

class StringOpsTest : StringSpec({
    withData(
        nameFn = { "${it.input} -> ${it.output}" },
        io.kotest.data.row("hello", "HELLO"),
        io.kotest.data.row("world", "WORLD"),
        io.kotest.data.row("", "")
    ) { (input, output) ->
        input.uppercase() shouldBe output
    }
})
```

## 9. Best Practices

| Practice | Reason |
|----------|--------|
| Use a single spec style per project | Consistency — team familiarity, uniform test structure |
| Use `InstancePerTest` isolation when tests mutate state | Prevents cross-test contamination |
| Use `data class` for test inputs instead of mocks | Data classes are cheap to construct — no mocking overhead |
| Call `clearMocks()` in `beforeTest` | Prevents stub leakage between tests in same spec instance |
| Use `runTest` for all suspend functions | Deterministic coroutine execution, no real delays |
| Keep tests independent — no ordering assumptions | Parallel execution safety, debugging clarity |
| Use `shouldThrow` over try/catch assertions | Cleaner intent, better failure messages |
| Name tests descriptively in the spec DSL | Kotest test names are identifiers — make them count |

## 10. Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Mixing JUnit and Kotest assertions | Confusing imports, inconsistent error messages | Use only Kotest matchers (`shouldBe`, `shouldThrow`) |
| `Thread.sleep` in tests | Flaky, slow, timing-dependent | Use `runTest` with virtual time or `advanceUntilIdle` |
| Testing private functions | Couples tests to implementation details | Test through public API only |
| Overusing `relaxed = true` mocks | Hides missing stubs, allows unexpected calls silently | Use strict mocks, stub only what is needed |
| Creating new mock objects inside test bodies | Boilerated setup, no reuse | Initialize mocks at spec level, clear in `beforeTest` |
| Using `assertThrows` (JUnit) in Kotest specs | Wrong framework assertion | Use `shouldThrow` from Kotest |
| Ignoring coroutine context in suspend tests | Unresolved coroutine scope errors | Always wrap suspend calls in `runTest { }` |

## 11. Cross References

| Topic | Reference |
|-------|-----------|
| MockK detailed usage | [mocking.md](mocking.md) |
| JUnit 4 unit testing patterns | [unit-testing.md](unit-testing.md) |
| Flow and StateFlow testing | [flow-testing.md](flow-testing.md) |
| Coroutine testing deep dive | See `runTest` patterns in [unit-testing.md](unit-testing.md) |
| Property-based testing | [property-testing.md](property-testing.md) |
| Test coverage configuration | [coverage.md](coverage.md) |
| TDD workflow | [tdd-workflow.md](tdd-workflow.md) |
