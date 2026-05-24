# Dependency Injection for Android

DI patterns for Android using Hilt (standard Android) and Koin (Kotlin Multiplatform). Covers setup, modules, scoping, testing, and anti-patterns.

## 1. Hilt Setup

### Application Class

```kotlin
@HiltAndroidApp
class MyApp : Application()
```

Annotate your `Application` class with `@HiltAndroidApp` to trigger Hilt's code generation. This must be declared in `AndroidManifest.xml`.

### Activity and Fragment

```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    @Inject lateinit var analytics: AnalyticsService
}

@AndroidEntryPoint
class ProfileFragment : Fragment() {
    @Inject lateinit var userRepository: UserRepository
}
```

Hilt can only inject into classes annotated with `@AndroidEntryPoint`. Supported classes: `Activity`, `Fragment`, `View`, `Service`, `BroadcastReceiver`.

### ViewModel

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUser: GetUserUseCase,
    private val userRepository: UserRepository,
) : ViewModel() {

    val uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)

    init {
        viewModelScope.launch {
            uiState.value = UserUiState.Success(getUser("123"))
        }
    }
}
```

`@HiltViewModel` replaces manual `ViewModelProvider.Factory`. All constructor parameters are provided by Hilt.

## 2. Hilt Modules

### @Module with @Binds (Interface Binding)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl,
    ): UserRepository

    @Binds
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl,
    ): AuthRepository
}
```

Use `@Binds` when you want to map an interface to its implementation. The module must be `abstract`.

### @Module with @Provides (Factory Methods)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
            .create()
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        gson: Gson,
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi {
        return retrofit.create(UserApi::class.java)
    }
}
```

Use `@Provides` when you need to construct objects that are not owned by your code (Retrofit, OkHttpClient, Gson).

| Annotation | Use Case | Module Type |
|---|---|---|
| `@Binds` | Interface → implementation mapping | `abstract class` |
| `@Provides` | Factory construction logic | `object` |
| `@InstallIn` | Declares which Hilt component the module lives in | Both |

## 3. Scoping Table

| Scope Annotation | Hilt Component | Lifetime |
|---|---|---|
| `@Singleton` | `SingletonComponent` | App process lifetime |
| `@ActivityRetainedScoped` | `ActivityRetainedComponent` | Across Activity recreations (e.g., config change) |
| `@ActivityScoped` | `ActivityComponent` | Single Activity instance |
| `@FragmentScoped` | `FragmentComponent` | Single Fragment instance |
| `@ViewModelScoped` | `ViewModelComponent` | ViewModel lifetime |
| `@ViewScoped` | `ViewComponent` | Single View instance |
| (unscoped) | N/A | New instance every injection |

```kotlin
@Provides
@Singleton
fun provideUserApi(retrofit: Retrofit): UserApi =
    retrofit.create(UserApi::class.java)

@Provides
@ActivityScoped
fun provideNavigationController(activity: FragmentActivity): NavController =
    NavHostFragment.findNavController(activity.supportFragmentManager.findFragmentById(R.id.nav_host)!!)
```

**Rule:** Only apply scopes when you genuinely need a single instance. Unscoped dependencies create a new instance per injection, which is correct for most use cases.

## 4. Constructor Injection in Feature/Component Modules

For classes you own, use `@Inject constructor` instead of `@Provides`:

```kotlin
class GetUserUseCase @Inject constructor(
    private val userRepository: UserRepository,
) {
    suspend operator fun invoke(id: String): Result<User> =
        userRepository.getUser(id)
}

class UserOrchestrator @Inject constructor(
    private val getUser: GetUserUseCase,
    private val analytics: AnalyticsService,
) {
    suspend fun execute(id: String): Result<User> {
        val result = getUser(id)
        analytics.trackEvent("user_fetched")
        return result
    }
}
```

Hilt automatically resolves `@Inject constructor` dependencies. No module needed unless binding to an interface.

## 5. NetworkModule Example

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor =
        HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                    else HttpLoggingInterceptor.Level.NONE
        }

    @Provides
    @Singleton
    fun provideAuthInterceptor(tokenProvider: TokenProvider): AuthInterceptor =
        AuthInterceptor(tokenProvider)

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        loggingInterceptor: HttpLoggingInterceptor,
    ): OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .build()

    @Provides
    @Singleton
    fun provideGson(): Gson = GsonBuilder()
        .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
        .create()

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient, gson: Gson): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi =
        retrofit.create(UserApi::class.java)
}
```

## 6. RepositoryModule Example

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    @Binds
    abstract fun bindAuthRepository(impl: AuthRepositoryImpl): AuthRepository

    @Binds
    abstract fun bindOrderRepository(impl: OrderRepositoryImpl): OrderRepository
}
```

Each `@Binds` maps one interface to one implementation. Keep this module in the `data` module, not in `app`.

## 7. Koin Setup for KMP

### Module Definition

```kotlin
val domainModule = module {
    factory { GetUserUseCase(get()) }
    factory { SearchUsersUseCase(get()) }
    factory { ValidateEmailUseCase() }
}

val dataModule = module {
    single<UserRepository> { UserRepositoryImpl(get()) }
    single<AuthRepository> { AuthRepositoryImpl(get()) }
    single { provideHttpClient() }
    single { provideKtorHttpClient(get()) }
}

val presentationModule = module {
    viewModelOf(::UserViewModel)
    viewModelOf(::SearchViewModel)
    viewModelOf(::ProfileViewModel)
}
```

### Application Startup

```kotlin
fun initKoin() {
    startKoin {
        modules(domainModule, dataModule, presentationModule)
    }
}
```

### Koin Scope Functions

| Function | Scope | Lifetime |
|---|---|---|
| `single { }` | Singleton | App lifetime |
| `factory { }` | Factory | New instance every time |
| `viewModelOf(::)` | ViewModel | ViewModel lifetime |
| `scoped { }` | Scoped | Lifetime of the scope |

## 8. Koin Modules Organization

```
domain/
  └── di/
      └── DomainModule.kt     (use cases)
data/
  └── di/
      └── DataModule.kt       (repositories, API clients)
presentation/
  └── di/
      └── PresentationModule.kt (ViewModels)
```

Each layer owns its own Koin module. The app module loads all three. This mirrors the Hilt `@InstallIn` approach but is explicit.

## 9. Testing with DI

### Hilt Testing

```kotlin
@HiltAndroidTest
class UserViewModelTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @BindValue
    @JvmField
    val mockUserRepository: UserRepository = mockk()

    @Inject
    lateinit var getUser: GetUserUseCase

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun loadsUserSuccessfully() = runTest {
        every { mockUserRepository.getUser("123") } returns Result.success(mockUser)
        val result = getUser("123")
        assertEquals(mockUser, result.getOrThrow())
    }
}
```

### Koin Testing

```kotlin
class UserViewModelTest : KoinTest {

    private val mockUserRepository: UserRepository = mockk()

    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(
            module {
                single<UserRepository> { mockUserRepository }
                factory { GetUserUseCase(get()) }
            }
        )
    }

    @Test
    fun loadsUserSuccessfully() = runTest {
        every { mockUserRepository.getUser("123") } returns Result.success(mockUser)
        val useCase by inject<GetUserUseCase>()
        val result = useCase("123")
        assertEquals(mockUser, result.getOrThrow())
    }
}
```

| Approach | Mechanism | Scope |
|---|---|---|
| `@BindValue` (Hilt) | Replaces binding in test | Per test class |
| Koin override | `module { single<MyInterface> { mock } }` | Per test rule |
| `@UninstallModules` (Hilt) | Remove production module | Per test class |

## 10. Anti-Patterns

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| DI modules in feature modules | Hilt modules must be in `app` or `data`, not feature | Move modules to the appropriate layer |
| Global singletons (object) | Cannot be swapped for testing | Use `@Singleton` with Hilt or `single { }` with Koin |
| Field injection (`@Inject lateinit`) | Only for framework classes (Activity, Fragment, Service) | Use constructor injection for all other classes |
| `@Inject` on Activity fields for ViewModels | ViewModel creation is handled by Hilt | Use `@HiltViewModel` with `@Inject constructor` |
| Binding concrete classes | Defeats the purpose of DI (testability) | Always bind interfaces to implementations |
| `EntryPoints.get()` | Indicates wrong DI architecture | Rethink dependency graph |
| Circular dependencies | Causes compile-time or runtime errors | Introduce a mediator or refactor |
| `@Singleton` on everything | Wastes memory and hides design issues | Only scope when a single instance is required |

## Cross References

- Related rules: `arch-di-only-in-app`, `arch-repo-iface-in-domain`, `arch-no-entity-in-ui`, `net-protocol-client`
- Related references: [`networking.md`](networking.md), [`persistence.md`](persistence.md), [`build-configuration.md`](build-configuration.md)
