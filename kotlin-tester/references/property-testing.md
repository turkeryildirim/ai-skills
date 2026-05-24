# Property-Based Testing with Kotest

Expert guidance for property-based testing and data-driven testing using the Kotest framework in Kotlin.

## 1. What Is Property-Based Testing?

Property-based testing verifies **properties** (invariants, rules) that hold true across a wide range of randomly generated inputs, rather than testing specific input/output pairs.

| Aspect | Example-Based Testing | Property-Based Testing |
|--------|----------------------|----------------------|
| Inputs | Hand-picked values | Randomly generated |
| Coverage | Limited to chosen cases | Broad, finds edge cases |
| Test count | 1 test = 1 scenario | 1 test = 1000+ scenarios |
| Failure reporting | Exact input shown | Minimal failing case (shrunk) |
| Best for | Specific edge cases | Pure functions, algorithms |

**Core idea:** Instead of `assert(f(x) == y)`, write `for all x: property(x) holds`.

## 2. Setup

```kotlin
dependencies {
    testImplementation("io.kotest:kotest-property:5.9.1")
    testImplementation("io.kotest:kotest-runner-junit5:5.9.1")
}
```

For JUnit 4 integration:

```kotlin
dependencies {
    testImplementation("io.kotest:kotest-property-jvm:5.9.1")
}
```

## 3. Basic Property Testing

### forAll

```kotlin
import io.kotest.property.forAll
import io.kotest.property.Arb
import io.kotest.property.arbitrary.int
import io.kotest.property.arbitrary.string

@Test
fun `string concatenation always increases length`() {
    forAll(Arb.string(), Arb.string()) { a, b ->
        (a + b).length >= a.length
    }
}

@Test
fun `addition is commutative`() {
    forAll(Arb.int(), Arb.int()) { a, b ->
        a + b == b + a
    }
}
```

### checkAll

```kotlin
import io.kotest.property.checkAll

@Test
fun `list reversal preserves size`() {
    checkAll<List<Int>> { list ->
        list.reversed().size == list.size
    }
}
```

| Function | Iterations | Shrinking | Use When |
|----------|-----------|-----------|----------|
| `forAll` | Default 1000 | Yes | Standard property tests |
| `checkAll` | Default 1000 | Yes | Same as forAll, inline type inference |
| `forAll(n)` | Custom count | Yes | Need more/fewer iterations |

## 4. Built-in Generators (Arb)

```kotlin
import io.kotest.property.arbitrary.*

Arb.int()                    // Random Int (includes negative, zero, positive)
Arb.int(0..100)              // Int in range
Arb.long()                   // Random Long
Arb.float()                  // Random Float
Arb.double()                 // Random Double
Arb.string()                 // Random String (various lengths, chars)
Arb.string(0..10)            // String with length 0 to 10
Arb.stringPattern("[a-z]+")  // String matching regex pattern
Arb.boolean()                // Random Boolean
Arb.byte()                   // Random Byte
Arb.short()                  // Random Short
Arb.bigDecimal()             // Random BigDecimal
Arb.uuid()                   // Random UUID
Arb.instant()                // Random Instant
Arb.localDate()              // Random LocalDate
Arb.localDateTime()          // Random LocalDateTime
Arb.list(Arb.int())          // Random List<Int>
Arb.list(Arb.string(), 0..5) // List with 0 to 5 elements
Arb.set(Arb.int())           // Random Set<Int>
Arb.map(Arb.string(), Arb.int())  // Random Map<String, Int>
Arb.pair(Arb.int(), Arb.string()) // Random Pair
Arb.enum<Direction>()        // Random enum value
Arb.element(1, 2, 3, 4, 5)  // Random element from list
Arb.positiveInt()            // Positive integers only
Arb.negativeInt()            // Negative integers only
Arb.nonZeroInt()             // Non-zero integers
Arb.bind(Arb.string(), Arb.int()) { name, age -> Person(name, age) }  // Custom
```

| Generator | Produces | Edge Cases Included |
|-----------|----------|-------------------|
| `Arb.int()` | Int | 0, Int.MIN_VALUE, Int.MAX_VALUE |
| `Arb.string()` | String | Empty, single char, unicode, long |
| `Arb.list(Arb.int())` | List<Int> | Empty, single, large |
| `Arb.enum<T>()` | T (enum) | All enum values |
| `Arb.float()` | Float | 0.0, NaN, Infinity, -Infinity |

## 5. Custom Generators

### Using Arb.bind

```kotlin
data class User(val name: String, val age: Int, val email: String)

val userArb: Arb<User> = Arb.bind(
    Arb.string(3..20),
    Arb.int(0..120),
    Arb.stringPattern("[a-z]+@[a-z]+\\.[a-z]{2,}")
) { name, age, email ->
    User(name, age, email)
}

@Test
fun `user serialization roundtrip preserves all fields`() {
    forAll(userArb) { user ->
        val json = JsonSerializer.serialize(user)
        val deserialized = JsonSerializer.deserialize<User>(json)
        deserialized == user
    }
}
```

### Using Arb.map

```kotlin
val orderArb: Arb<Order> = Arb.int(1..10000).map { id ->
    Order(id = id, status = OrderStatus.PENDING)
}
```

### Using Arbitrary Builder

```kotlin
val emailArb: Arb<String> = arbitrary {
    val local = Arb.string(3..10).bind(it)
    val domain = Arb.string(3..10).bind(it)
    val tld = Arb.element("com", "net", "org", "dev").bind(it)
    "$local@$domain.$tld"
}

@Test
fun `email validator accepts all generated valid emails`() {
    forAll(emailArb) { email ->
        EmailValidator.isValid(email)
    }
}
```

## 6. Property Testing Examples

### String Reverse Is Involutory

```kotlin
@Test
fun `reversing a string twice returns the original`() {
    forAll(Arb.string()) { str ->
        str.reversed().reversed() == str
    }
}
```

### List Sort Is Idempotent

```kotlin
@Test
fun `sorting a sorted list produces the same result`() {
    forAll(Arb.list(Arb.int())) { list ->
        val sorted = list.sorted()
        sorted.sorted() == sorted
    }
}

@Test
fun `sorted list has same size as original`() {
    forAll(Arb.list(Arb.int())) { list ->
        list.sorted().size == list.size
    }
}

@Test
fun `sorted list contains same elements`() {
    forAll(Arb.list(Arb.int())) { list ->
        list.sorted().toSet() == list.toSet()
    }
}
```

### Serialization Roundtrip

```kotlin
data class Product(val id: String, val name: String, val price: Double)

val productArb: Arb<Product> = Arb.bind(
    Arb.string(1..10),
    Arb.string(3..50),
    Arb.double(0.0..10000.0)
) { id, name, price -> Product(id, name, price) }

@Test
fun `JSON serialization roundtrip preserves product`() {
    forAll(productArb) { product ->
        val json = Json.encodeToString(product)
        val decoded = Json.decodeFromString<Product>(json)
        decoded == product
    }
}
```

### Email Validation Properties

```kotlin
@Test
fun `valid email always contains exactly one @`() {
    forAll(Arb.string()) { str ->
        val atCount = str.count { it == '@' }
        if (atCount != 1) !EmailValidator.isValid(str)
        else true
    }
}

@Test
fun `empty string is never a valid email`() {
    forAll(Arb.string(0..0)) { str ->
        !EmailValidator.isValid(str)
    }
}
```

### Mathematical Properties

```kotlin
@Test
fun `multiplication distributes over addition`() {
    forAll(Arb.int(), Arb.int(), Arb.int()) { a, b, c ->
        a * (b + c) == a * b + a * c
    }
}

@Test
fun `absolute value is always non-negative`() {
    forAll(Arb.int()) { a ->
        abs(a) >= 0
    }
}

@Test
fun `max of two numbers is at least both`() {
    forAll(Arb.int(), Arb.int()) { a, b ->
        maxOf(a, b) >= a && maxOf(a, b) >= b
    }
}
```

## 7. Data-Driven Testing with withData

Kotest provides `withData` for table-driven tests with named cases:

```kotlin
import io.kotest.datatest.withData

@Test
fun `should classify triangle correctly`() {
    withData(
        nameFn = { (a, b, c, expected) -> "Triangle($a, $b, $c) → $expected" },
        Triple(3, 3, 3, "Equilateral"),
        Triple(3, 4, 5, "Scalene"),
        Triple(3, 3, 4, "Isosceles"),
        Triple(5, 5, 3, "Isosceles"),
    ) { (a, b, c, expected) ->
        assertEquals(expected, TriangleClassifier.classify(a, b, c))
    }
}

@Test
fun `should validate password rules`() {
    withData(
        nameFn = { (input, expected) -> "\"$input\" → $expected" },
        Pair("", false),
        Pair("abc", false),
        Pair("abcdefgh", false),
        Pair("Abcdefgh", false),
        Pair("Abcdefg1", true),
        Pair("P@ssw0rd", true),
        Pair("12345678", false),
    ) { (password, expected) ->
        assertEquals(expected, PasswordValidator.isValid(password))
    }
}
```

### withData for Enums

```kotlin
@Test
fun `all order statuses have a display name`() {
    withData(OrderStatus.values().toList()) { status ->
        assertTrue(status.displayName.isNotBlank())
    }
}
```

| Method | Use When |
|--------|---------|
| `withData(vararg values)` | Small, known set of test cases |
| `withData(list)` | Dynamic or computed test data |
| `forAll(Arb)` | Random inputs, property-based |
| `checkAll` | Same as forAll with type inference |

## 8. Configuring Property Tests

```kotlin
@Test
fun `property test with custom iteration count`() {
    forAll(Arb.string(), iterations = 5000) { str ->
        str.length >= 0
    }
}

@Test
fun `property test with shrinking disabled`() {
    forAll(Arb.int(), Arb.int()) { a, b ->
        a + b == b + a
    }.config(shrinkingMode = ShrinkingMode.Off)
}

@Test
fun `property test with custom seed for reproducibility`() {
    forAll(Arb.int()) { a ->
        a * 0 == 0
    }.config(seed = 12345L)
}
```

| Config Option | Default | Purpose |
|---------------|---------|---------|
| `iterations` | 1000 | Number of random inputs to test |
| `shrinkingMode` | `ShrinkingMode.Full` | How to minimize failing cases |
| `seed` | Random | Reproduce specific failures |
| `minSuccess` | 1 | Minimum passing iterations |
| `maxFailure` | 10 | Maximum failures before aborting |

## 9. When to Use Property Testing

| Use For | Example |
|---------|---------|
| Pure functions | `reverse`, `sort`, `encode`, `decode` |
| Parsers | JSON parser, CSV parser, URL parser |
| Serializers | JSON, protobuf, XML roundtrips |
| Math operations | Arithmetic, geometry, statistics |
| Data transformations | Map, filter, reduce compositions |
| Validation rules | Email, phone, password rules |
| Collection operations | Merge, intersect, diff |
| Encoding / decoding | Base64, URL encoding, compression |

## 10. When NOT to Use Property Testing

| Skip For | Reason |
|----------|--------|
| Side-effect-heavy code | Database, network, file I/O — hard to generate valid inputs |
| I/O operations | Results depend on external state |
| UI rendering | Visual output is not easily compared |
| Tests with specific setup | Known edge cases are better as example tests |
| Flaky external dependencies | Non-deterministic results invalidate properties |

**Guideline:** If the function is **pure** (same input always produces same output, no side effects), property testing is ideal. If it depends on external state, use example-based tests.

## Cross References

- Related rules: `test-behavior-names`, `test-given-when-then`, `test-kotest-assertions`
- Related references: [`unit-testing.md`](unit-testing.md), [`tdd-workflow.md`](tdd-workflow.md), [`mocking.md`](mocking.md)
