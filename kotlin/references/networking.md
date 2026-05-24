# Networking in Kotlin

Modern networking patterns for Android using Retrofit with Kotlin coroutines and Ktor for Kotlin Multiplatform. Covers production-grade configuration, error handling, retry logic, token refresh, and Hilt integration.

## Core Rule

**All API methods must be `suspend` functions.** Never use callback-based `Call<T>` or `Observable<T>` in new code.

## 1. Retrofit Interface Definitions

```kotlin
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserResponse

    @GET("users")
    suspend fun getUsers(@Query("page") page: Int): PagedResponse<UserResponse>

    @POST("users")
    suspend fun createUser(@Body request: CreateUserRequest): UserResponse

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body request: UpdateUserRequest): UserResponse

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String)

    @Multipart
    suspend fun uploadAvatar(@Part file: MultipartBody.Part): UserResponse
}
```

- Every method returns `suspend`. No `Call<T>`, no `Observable<T>`, no callbacks.
- Use `@Body` for POST/PUT, `@Path` for path parameters, `@Query` for query parameters.
- Use `@Multipart` with `MultipartBody.Part` for file uploads.

## 2. OkHttpClient Configuration

```kotlin
fun provideOkHttpClient(
    authInterceptor: AuthInterceptor,
    loggingInterceptor: HttpLoggingInterceptor,
): OkHttpClient {
    return OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .build()
}
```

| Setting | Recommended Value | Purpose |
|---|---|---|
| `connectTimeout` | 30s | TCP connection timeout |
| `readTimeout` | 30s | Socket read timeout |
| `writeTimeout` | 30s | Socket write timeout |
| Interceptor order | Auth → Logging → Retry | Interceptors run in order for requests, reverse for responses |
| `connectionPool` | 5 idle, 5 min keep-alive | Default is usually sufficient |

## 3. Protocol-Based API Client

```kotlin
interface UserRepository {
    fun getUsers(): Flow<List<User>>
    suspend fun getUser(id: String): Result<User>
    suspend fun createUser(request: CreateUserRequest): Result<User>
}

class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
) : UserRepository {

    override fun getUsers(): Flow<List<User>> = flow {
        val response = api.getUsers(1)
        emit(response.items.map { it.toDomain() })
    }

    override suspend fun getUser(id: String): Result<User> = runCatching {
        api.getUser(id).toDomain()
    }

    override suspend fun createUser(request: CreateUserRequest): Result<User> = runCatching {
        api.createUser(request.toDto()).toDomain()
    }
}
```

### Hilt NetworkModule

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                    else HttpLoggingInterceptor.Level.NONE
        }
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        loggingInterceptor: HttpLoggingInterceptor,
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi {
        return retrofit.create(UserApi::class.java)
    }
}
```

## 4. Error Handling

```kotlin
sealed class NetworkError : Exception() {
    data object NoConnection : NetworkError()
    data object Timeout : NetworkError()
    data class ClientError(val code: Int, val body: String?) : NetworkError()
    data class ServerError(val code: Int, val body: String?) : NetworkError()
    data class DecodingError(val cause: Throwable) : NetworkError()
    data class Unknown(val cause: Throwable) : NetworkError()
}

fun Throwable.toNetworkError(): NetworkError = when (this) {
    is java.net.UnknownHostException -> NetworkError.NoConnection
    is java.net.SocketTimeoutException -> NetworkError.Timeout
    is JsonParseException -> NetworkError.DecodingError(this)
    is retrofit2.HttpException -> {
        val code = code()
        val body = response()?.errorBody()?.string()
        if (code in 400..499) NetworkError.ClientError(code, body)
        else NetworkError.ServerError(code, body)
    }
    is CancellationException -> throw this
    else -> NetworkError.Unknown(this)
}
```

**CRITICAL:** Retrofit throws `HttpException` for non-2xx responses but does NOT throw for network-level failures in some configurations. Always wrap API calls with error handling.

| Error Type | Code Range | Retry? | Example |
|---|---|---|---|
| `ClientError` | 400-499 | No | 401 Unauthorized, 404 Not Found |
| `ServerError` | 500-599 | Yes | 500 Internal, 503 Unavailable |
| `NoConnection` | N/A | Yes | Airplane mode |
| `Timeout` | N/A | Yes | Slow network |
| `DecodingError` | N/A | No | Schema mismatch |

## 5. Retry Logic

```kotlin
suspend fun <T> retryWithBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000L,
    block: suspend () -> T,
): T {
    var attempt = 0
    while (true) {
        try {
            return block()
        } catch (e: Exception) {
            attempt++
            if (e is CancellationException) throw e
            if (attempt >= maxRetries) throw e
            if (e.isClientError()) throw e
            val delay = initialDelayMs * (2.0.pow(attempt - 1)).toLong()
            delay(delay)
        }
    }
}

fun Throwable.isClientError(): Boolean {
    val httpException = this as? retrofit2.HttpException ?: return false
    return httpException.code() in 400..499
}
```

- Check `CancellationException` first and rethrow immediately — never swallow coroutine cancellation.
- Skip retry on 4xx client errors (the request itself is wrong).
- Use exponential backoff: 1s → 2s → 4s.

## 6. JSON Decoding Configuration

```kotlin
val gson = GsonBuilder()
    .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
    .setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
    .setLenient()
    .create()

val retrofit = Retrofit.Builder()
    .addConverterFactory(GsonConverterFactory.create(gson))
    .build()
```

### Server Response Fields Must Be Nullable

```kotlin
data class UserResponse(
    val id: String?,
    val name: String?,
    val email: String?,
    val avatarUrl: String?,
    val createdAt: String?,
)
```

All fields in response DTOs must be nullable. The server may omit or null fields at any time. Map to non-nullable domain models with defaults in the mapper:

```kotlin
fun UserResponse.toDomain(): User = User(
    id = id.orEmpty(),
    name = name.orEmpty(),
    email = email.orEmpty(),
    avatarUrl = avatarUrl ?: "",
    createdAt = createdAt ?: "",
)
```

| Layer | Nullability | Rationale |
|---|---|---|
| Response DTO | All nullable | Server may omit fields |
| Domain Model | Non-nullable with defaults | Business logic assumes valid data |
| UI State | Non-nullable with defaults | Compose expects stable types |

## 7. Token Refresh (401 Handling)

Use a `Mutex` to prevent concurrent token refresh calls:

```kotlin
class AuthInterceptor @Inject constructor(
    private val tokenProvider: TokenProvider,
) : Interceptor {

    private val refreshMutex = Mutex()

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenProvider.accessToken()
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer $token")
            .build()
        val response = chain.proceed(request)

        if (response.code == 401) {
            response.close()
            return synchronizedRefresh(chain, request)
        }
        return response
    }

    private suspend fun synchronizedRefresh(
        chain: Interceptor.Chain,
        originalRequest: Request,
    ): Response = refreshMutex.withLock {
        val newToken = tokenProvider.refreshAccessToken()
        val refreshedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $newToken")
            .build()
        chain.proceed(refreshedRequest)
    }
}
```

- Use `Mutex` (not `synchronized`) because this runs inside a coroutine interceptor.
- Only retry once on 401 — do not loop.
- Close the original response before retrying to prevent connection leaks.

## 8. Ktor HttpClient for KMP

```kotlin
val httpClient = HttpClient {
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = false
            isLenient = true
            ignoreUnknownKeys = true
            namingStrategy = JsonNamingStrategy.SnakeCase
        })
    }

    install(Logging) {
        logger = Logger.DEFAULT
        level = LogLevel.INFO
    }

    defaultRequest {
        url("https://api.example.com/")
        header("Accept", "application/json")
    }
}
```

| Ktor Feature | Purpose |
|---|---|
| `ContentNegotiation` | JSON serialization/deserialization |
| `Logging` | HTTP request/response logging |
| `defaultRequest` | Base URL and common headers |
| `HttpResponseValidator` | Status code validation |

```kotlin
suspend fun fetchUser(id: String): User {
    return httpClient.get("users/$id").body<User>()
}
```

## 9. Anti-Patterns

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| `Call<T>` return type | Blocks thread, no coroutine support | Use `suspend` functions |
| Ignore HTTP status codes | Retrofit may not throw for all errors | Always check response codes |
| `Gson()` with no config | No snake_case, no date handling | Configure `GsonBuilder` with naming policy |
| Non-nullable response fields | Server may omit fields → crash | Make all DTO fields nullable |
| `synchronized` for token refresh | Blocks thread, not coroutine-safe | Use `Mutex` |
| Hardcoded URLs | Cannot change between environments | Use `BuildConfig` fields |
| No timeout configuration | Default timeouts may be too short | Configure `OkHttpClient` timeouts |
| Logging in release builds | Leaks sensitive data | Gate logging on `BuildConfig.DEBUG` |
| Swallow `CancellationException` | Breaks structured concurrency | Always rethrow |

## Cross References

- Related rules: `net-status-validation`, `net-nullable-responses`, `net-retry-backoff`, `net-token-refresh`, `net-suspend-only`
- Related references: [`dependency-injection.md`](dependency-injection.md), [`persistence.md`](persistence.md), [`build-configuration.md`](build-configuration.md)
