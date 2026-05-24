# Kotlin Multiplatform (KMP) Patterns

Expert guidance for sharing code across Android, iOS, Desktop, and Web using Kotlin Multiplatform.

## 1. Project Structure

A typical KMP project structure:

```
common/
├── src/
│   ├── commonMain/             (Shared logic: domain, data, network)
│   ├── androidMain/            (Android-specific implementations)
│   ├── iosMain/                (iOS-specific implementations)
│   ├── desktopMain/            (Desktop-specific implementations)
│   └── wasmJsMain/             (Web-specific implementations)
└── build.gradle.kts
```

## 2. expect / actual Pattern

Use `expect`/`actual` when you need to access platform-specific APIs.

### Example: Platform Name
```kotlin
// commonMain
expect fun getPlatformName(): String

// androidMain
actual fun getPlatformName(): String = "Android ${android.os.Build.VERSION.SDK_INT}"

// iosMain
actual fun getPlatformName(): String = "iOS ${UIDevice.currentDevice.systemVersion}"
```

### Example: Platform-specific Class
```kotlin
// commonMain
expect class PlatformLogger() {
    fun log(message: String)
}

// androidMain
actual class PlatformLogger actual constructor() {
    actual fun log(message: String) {
        android.util.Log.d("KMP", message)
    }
}
```

## 3. Interface-based Abstraction (Recommended)

Prefer interfaces and Dependency Injection over `expect`/`actual` for better testability and cleaner separation.

```kotlin
// commonMain
interface FileSystem {
    fun readText(path: String): String
}

class DataRepository(private val fileSystem: FileSystem) {
    fun loadConfig() = fileSystem.readText("config.json")
}

// androidMain
class AndroidFileSystem : FileSystem {
    override fun readText(path: String): String = // Android impl
}

// iosMain
class IosFileSystem : FileSystem {
    override fun readText(path: String): String = // iOS impl
}
```

## 4. KMP Networking with Ktor

Ktor is the standard networking library for KMP.

```kotlin
// commonMain
val client = HttpClient {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            explicitNulls = false
        })
    }
}

suspend fun fetchUsers(): List<User> = client.get("https://api.example.com/users").body()
```

### KMP HttpClient Engines

| Platform | Engine |
|----------|--------|
| Android | `OkHttp` |
| iOS | `Darwin` |
| Desktop | `CIO` / `Java` |
| JS/WASM | `Js` |

## 5. KMP Persistence with SQLDelight

SQLDelight generates type-safe Kotlin APIs from SQL.

```kotlin
// commonMain
val database = MyDatabase(driver)

// androidMain
val driver = AndroidSqliteDriver(MyDatabase.Schema, context, "test.db")

// iosMain
val driver = NativeSqliteDriver(MyDatabase.Schema, "test.db")
```

## 6. Compose Multiplatform

Compose Multiplatform allows sharing UI across Android, iOS, Desktop, and Web.

```kotlin
// commonMain
@Composable
fun App() {
    MaterialTheme {
        var text by remember { mutableStateOf("Hello, World!") }
        Button(onClick = { text = "Hello, KMP!" }) {
            Text(text)
        }
    }
}
```

## 7. KMP Dispatchers

`Dispatchers.IO` is NOT available in `commonMain` for all targets.

### Abstraction Pattern
```kotlin
// commonMain
expect val ioDispatcher: CoroutineDispatcher

// androidMain
actual val ioDispatcher = Dispatchers.IO

// iosMain
actual val ioDispatcher = Dispatchers.Default // iOS uses Default for IO
```

## 8. Best Practices

| Rule | Description |
|------|-------------|
| Keep `commonMain` pure | Avoid platform-specific imports in shared code |
| Prefer interfaces | Use interfaces for platform-specific capabilities |
| Use `kotlinx.serialization` | The standard for KMP serialization |
| Use `kotlinx.datetime` | The standard for KMP date/time handling |
| Use `Napier` or `Kermit` | Multiplatform logging libraries |
| Use `Koin` | Popular DI library for KMP |

## 9. Common Pitfalls

- **Memory Management on iOS:** Be aware of the new memory manager (no more frozen objects required), but still be careful with global state.
- **Platform-specific Dependencies:** Ensure your dependencies support all your target platforms.
- **Resources:** Use `compose-multiplatform-resources` for sharing strings, images, and fonts.

## Cross References

- Related rules: `kt-kmp-expect-actual`, `coro-kmp-dispatchers`
- Related references: [`coroutines.md`](coroutines.md), [`architecture.md`](architecture.md), [`compose-ui.md`](compose-ui.md)
