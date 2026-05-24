# Coordinator Pattern for Android Navigation

Expert guidance for decoupling navigation logic from Activities, Fragments, and ViewModels using the Coordinator pattern.

## 1. Problem Statement

Traditional Android navigation suffers from tight coupling:

```kotlin
// BAD - Activity knows about all destinations
class MainActivity : AppCompatActivity() {
    fun onLoginSuccess(userId: String) {
        startActivity(HomeActivity.newIntent(this, userId))
    }

    fun onOnboardingComplete() {
        startActivity(DashboardActivity.newIntent(this))
    }
}

// BAD - ViewModel knows about navigation
class LoginViewModel : ViewModel() {
    fun login(email: String, password: String) {
        viewModelScope.launch {
            val result = loginUseCase(email, password)
            if (result is Try.Success) {
                _navigationEvent.emit(NavigateToHome(result.value.id))
            }
        }
    }
}
```

### Problems with Traditional Approach

| Problem | Description |
|---------|-------------|
| Activity is a God object | Knows every screen and flow |
| ViewModel mixes concerns | Navigation + business logic in one place |
| Hard to test | Navigation requires Activity/Fragment instance |
| A/B testing is invasive | Conditional navigation scattered everywhere |
| Deep link handling is fragile | Complex intent parsing in Activity |
| Reuse is impossible | Cannot reuse a flow in a different context |

## 2. Coordinator Concept

A Coordinator is a **stateless** object that knows **where to go next**. It encapsulates navigation decisions without owning UI state.

### Core Principles

| Principle | Description |
|-----------|-------------|
| Stateless | Holds no UI state, only navigation logic |
| Single Responsibility | One flow per coordinator |
| Composable | Coordinators can nest (parent-child) |
| Testable | Pure functions / lambdas, no Android dependencies |
| Decoupled | ViewModels don't know about screens |

### Basic Coordinator
```kotlin
class LoginCoordinator(
    private val navigator: Navigator,
    private val onLoginComplete: (userId: String) -> Unit
) {
    fun start() {
        navigator.navigateTo(R.id.loginFragment)
    }

    fun onLoginSuccess(userId: String) {
        onLoginComplete(userId)
    }

    fun onForgotPassword() {
        navigator.navigateTo(R.id.forgotPasswordFragment)
    }

    fun onRegisterClicked() {
        navigator.navigateTo(R.id.registerFragment)
    }
}
```

## 3. Flow Coordinator Pattern

A Flow Coordinator manages a multi-step sequence of screens.

### News Flow Coordinator
```kotlin
class NewsFlowCoordinator(
    private val navigator: Navigator
) {
    fun start() {
        navigator.navigateTo(NewsRoutes.NEWS_LIST)
    }

    fun onNewsItemSelected(newsId: String) {
        navigator.navigateTo(NewsRoutes.newsDetail(newsId))
    }

    fun onCommentsClicked(newsId: String) {
        navigator.navigateTo(NewsRoutes.newsComments(newsId))
    }

    fun onAuthorClicked(authorId: String) {
        navigator.navigateTo(ProfileRoutes.authorProfile(authorId))
    }

    fun onBack(): Boolean = navigator.pop()
}
```

### Login Flow Coordinator
```kotlin
class LoginFlowCoordinator(
    private val navigator: Navigator,
    private val onLoginComplete: (userId: String) -> Unit
) {
    fun start() {
        navigator.navigateTo(LoginRoutes.WELCOME)
    }

    fun onGetStartedClicked() {
        navigator.navigateTo(LoginRoutes.EMAIL_INPUT)
    }

    fun onEmailSubmitted(email: String) {
        navigator.navigateTo(LoginRoutes.PASSWORD_INPUT, bundleOf("email" to email))
    }

    fun onLoginSuccess(userId: String) {
        onLoginComplete(userId)
    }

    fun onForgotPassword(email: String) {
        navigator.navigateTo(LoginRoutes.FORGOT_PASSWORD, bundleOf("email" to email))
    }

    fun onSignUpClicked() {
        navigator.navigateTo(LoginRoutes.SIGN_UP)
    }

    fun onSignUpComplete(userId: String) {
        onLoginComplete(userId)
    }
}
```

## 4. Root Coordinator

The Root Coordinator manages top-level app routing based on authentication state.

```kotlin
class RootCoordinator(
    private val navigator: Navigator,
    private val userManager: UserManager
) {
    private val loginCoordinator by lazy {
        LoginFlowCoordinator(navigator, ::onLoginComplete)
    }

    private val mainCoordinator by lazy {
        MainFlowCoordinator(navigator)
    }

    fun start() {
        if (userManager.isLoggedIn) {
            mainCoordinator.start()
        } else {
            loginCoordinator.start()
        }
    }

    private fun onLoginComplete(userId: String) {
        navigator.clearBackStack()
        mainCoordinator.start()
    }

    fun onLogout() {
        navigator.clearBackStack()
        loginCoordinator.start()
    }
}
```

### Auth-Based Routing with State Observation
```kotlin
class RootCoordinator(
    private val navigator: Navigator,
    private val userManager: UserManager,
    private val scope: CoroutineScope
) {
    init {
        scope.launch {
            userManager.authState.collect { state ->
                when (state) {
                    AuthState.LOGGED_IN -> showMain()
                    AuthState.LOGGED_OUT -> showLogin()
                    AuthState.ONBOARDING_INCOMPLETE -> showOnboarding()
                }
            }
        }
    }

    private fun showMain() {
        navigator.clearBackStack()
        MainFlowCoordinator(navigator).start()
    }

    private fun showLogin() {
        navigator.clearBackStack()
        LoginFlowCoordinator(navigator, ::onLoginComplete).start()
    }

    private fun showOnboarding() {
        navigator.clearBackStack()
        OnboardingFlowCoordinator(navigator, ::onOnboardingComplete).start()
    }

    private fun onLoginComplete(userId: String) = showMain()

    private fun onOnboardingComplete() = showMain()
}
```

## 5. Parent-Child Relationships

Coordinators communicate through lambdas, creating a clean parent-child hierarchy.

```
RootCoordinator
├── LoginFlowCoordinator (onLoginComplete → RootCoordinator.showMain)
├── OnboardingFlowCoordinator (onOnboardingComplete → RootCoordinator.showMain)
└── MainFlowCoordinator
    ├── HomeCoordinator (onSettingsClicked → MainFlowCoordinator.showSettings)
    ├── SettingsCoordinator (onLogout → RootCoordinator.onLogout)
    └── ProfileCoordinator
```

### Example Chain
```kotlin
class MainFlowCoordinator(
    private val navigator: Navigator,
    private val onLogout: () -> Unit = {}
) {
    private val homeCoordinator = HomeCoordinator(
        navigator = navigator,
        onProfileClicked = { userId -> showProfile(userId) },
        onSettingsClicked = { showSettings() }
    )

    fun start() {
        homeCoordinator.start()
    }

    private fun showProfile(userId: String) {
        ProfileCoordinator(
            navigator = navigator,
            userId = userId,
            onLogout = onLogout
        ).start()
    }

    private fun showSettings() {
        SettingsCoordinator(
            navigator = navigator,
            onLogout = onLogout
        ).start()
    }
}
```

## 6. Navigator Pattern

The Navigator handles the actual Fragment/Activity transactions. It is stateless and unaware of business logic.

### Fragment-Based Navigator
```kotlin
interface Navigator {
    fun navigateTo(route: String, args: Bundle? = null)
    fun pop(): Boolean
    fun popTo(route: String)
    fun clearBackStack()
}

class FragmentNavigator(
    private val fragmentManager: FragmentManager,
    private val containerId: Int
) : Navigator {

    override fun navigateTo(route: String, args: Bundle? = null) {
        val fragment = createFragmentForRoute(route, args)
        fragmentManager.commit {
            replace(containerId, fragment)
            addToBackStack(route)
        }
    }

    override fun pop(): Boolean {
        if (fragmentManager.backStackEntryCount > 0) {
            fragmentManager.popBackStackImmediate()
            return true
        }
        return false
    }

    override fun popTo(route: String) {
        fragmentManager.popBackStack(route, 0)
    }

    override fun clearBackStack() {
        repeat(fragmentManager.backStackEntryCount) {
            fragmentManager.popBackStackImmediate()
        }
    }

    private fun createFragmentForRoute(route: String, args: Bundle?): Fragment =
        when (route) {
            LoginRoutes.WELCOME -> WelcomeFragment()
            LoginRoutes.EMAIL_INPUT -> EmailInputFragment().apply { arguments = args }
            LoginRoutes.PASSWORD_INPUT -> PasswordInputFragment().apply { arguments = args }
            LoginRoutes.FORGOT_PASSWORD -> ForgotPasswordFragment().apply { arguments = args }
            LoginRoutes.SIGN_UP -> SignUpFragment()
            else -> error("Unknown route: $route")
        }
}
```

### Compose-Based Navigator
```kotlin
class ComposeNavigator(
    private val navController: NavHostController
) : Navigator {

    override fun navigateTo(route: String, args: Bundle? = null) {
        navController.navigate(route)
    }

    override fun pop(): Boolean = navController.popBackStack()

    override fun popTo(route: String) {
        navController.popBackStack(route, inclusive = false)
    }

    override fun clearBackStack() {
        navController.popBackStack(navController.graph.startDestinationId, inclusive = false)
    }
}
```

## 7. ViewModel → Coordinator Connection

ViewModels communicate with Coordinators via lambda callbacks. The ViewModel never knows about screens.

### Single-Event Pattern
```kotlin
class LoginViewModel(
    private val loginUseCase: LoginUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<LoginUiState>(LoginUiState.Idle)
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    var onSuccess: ((String) -> Unit)? = null
    var onForgotPassword: ((String) -> Unit)? = null
    var onSignUp: (() -> Unit)? = null

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.update { LoginUiState.Loading }
            when (val result = loginUseCase(email, password)) {
                is Try.Success -> onSuccess?.invoke(result.value.id)
                is Try.Failure -> _uiState.update { LoginUiState.Error(result.error.message) }
            }
        }
    }

    fun forgotPassword(email: String) {
        onForgotPassword?.invoke(email)
    }

    fun signUp() {
        onSignUp?.invoke()
    }

    override fun onCleared() {
        onSuccess = null
        onForgotPassword = null
        onSignUp = null
    }
}
```

### Coordinator Binds Callbacks
```kotlin
class LoginFlowCoordinator(
    private val navigator: Navigator,
    private val viewModelProvider: (Bundle?) -> LoginViewModel,
    private val onLoginComplete: (String) -> Unit
) {
    fun start(args: Bundle? = null) {
        val viewModel = viewModelProvider(args)
        viewModel.onSuccess = { userId -> onLoginComplete(userId) }
        viewModel.onForgotPassword = { email -> showForgotPassword(email) }
        viewModel.onSignUp = { showSignUp() }
        navigator.navigateTo(LoginRoutes.EMAIL_INPUT, args)
    }

    private fun showForgotPassword(email: String) {
        navigator.navigateTo(LoginRoutes.FORGOT_PASSWORD, bundleOf("email" to email))
    }

    private fun showSignUp() {
        navigator.navigateTo(LoginRoutes.SIGN_UP)
    }
}
```

### SharedFlow Alternative (for Compose)
```kotlin
class LoginViewModel(
    private val loginUseCase: LoginUseCase
) : ViewModel() {

    private val _navigation = MutableSharedFlow<LoginNavigation>()
    val navigation: SharedFlow<LoginNavigation> = _navigation.asSharedFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            when (val result = loginUseCase(email, password)) {
                is Try.Success -> _navigation.emit(LoginNavigation.ToHome(result.value.id))
                is Try.Failure -> _uiState.update { LoginUiState.Error(result.error.message) }
            }
        }
    }
}

sealed interface LoginNavigation {
    data class ToHome(val userId: String) : LoginNavigation
    data class ToForgotPassword(val email: String) : LoginNavigation
    data object ToSignUp : LoginNavigation
}
```

## 8. A/B Testing with Coordinators

Coordinators make A/B testing navigation trivial — inject a strategy instead of scattering conditionals.

### Strategy Interface
```kotlin
interface OnboardingStrategy {
    fun isFirstStep(): String
    fun nextStep(current: String, result: StepResult): String?
}
```

### A Variant
```kotlin
class OnboardingStrategyA : OnboardingStrategy {
    override fun isFirstStep() = OnboardingRoutes.WELCOME

    override fun nextStep(current: String, result: StepResult): String? = when (current) {
        OnboardingRoutes.WELCOME -> OnboardingRoutes.PROFILE_SETUP
        OnboardingRoutes.PROFILE_SETUP -> OnboardingRoutes.INTERESTS
        OnboardingRoutes.INTERESTS -> null
        else -> null
    }
}
```

### B Variant
```kotlin
class OnboardingStrategyB : OnboardingStrategy {
    override fun isFirstStep() = OnboardingRoutes.UNIFIED_FORM

    override fun nextStep(current: String, result: StepResult): String? = when (current) {
        OnboardingRoutes.UNIFIED_FORM -> OnboardingRoutes.TUTORIAL
        OnboardingRoutes.TUTORIAL -> null
        else -> null
    }
}
```

### Coordinator with Strategy
```kotlin
class OnboardingFlowCoordinator(
    private val navigator: Navigator,
    private val strategy: OnboardingStrategy,
    private val onComplete: () -> Unit
) {
    fun start() {
        navigator.navigateTo(strategy.isFirstStep())
    }

    fun onStepComplete(result: StepResult, currentRoute: String) {
        val next = strategy.nextStep(currentRoute, result)
        if (next != null) {
            navigator.navigateTo(next)
        } else {
            onComplete()
        }
    }
}
```

### DI Selection
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object OnboardingModule {

    @Provides
    fun provideOnboardingStrategy(experimentManager: ExperimentManager): OnboardingStrategy =
        if (experimentManager.isVariant("onboarding", "b")) {
            OnboardingStrategyB()
        } else {
            OnboardingStrategyA()
        }
}
```

## 9. Kotlin DSL for Coordinators

```kotlin
@DslMarker
annotation class CoordinatorDsl

@CoordinatorDsl
class FlowBuilder {
    var start: String = ""
    private val steps = mutableMapOf<String, StepBuilder>()

    fun step(route: String, block: StepBuilder.() -> Unit) {
        steps[route] = StepBuilder().apply(block)
    }

    fun build(): FlowDefinition = FlowDefinition(start, steps.mapValues { it.value.build() })
}

@CoordinatorDsl
class StepBuilder {
    var route: String = ""
    var next: String? = null
    private var _condition: ((StepResult?) -> String?) = { next }

    fun condition(block: (StepResult?) -> String?) {
        _condition = block
    }

    fun build(): StepDefinition = StepDefinition(route, _condition)
}

data class FlowDefinition(
    val startRoute: String,
    val steps: Map<String, StepDefinition>
)

data class StepDefinition(
    val route: String,
    val nextRoute: (StepResult?) -> String?
)

fun flow(block: FlowBuilder.() -> Unit): FlowDefinition =
    FlowBuilder().apply(block).build()
```

### DSL Usage
```kotlin
val loginFlow = flow {
    start = LoginRoutes.WELCOME
    step(LoginRoutes.WELCOME) {
        next = LoginRoutes.EMAIL_INPUT
    }
    step(LoginRoutes.EMAIL_INPUT) {
        condition { result ->
            when (result) {
                is StepResult.Success -> LoginRoutes.PASSWORD_INPUT
                is StepResult.ForgotPassword -> LoginRoutes.FORGOT_PASSWORD
                is StepResult.SignUp -> LoginRoutes.SIGN_UP
                else -> null
            }
        }
    }
    step(LoginRoutes.PASSWORD_INPUT) {
        condition { result ->
            if (result is StepResult.Success) null else LoginRoutes.PASSWORD_INPUT
        }
    }
}
```

## 10. Coroutine-Based Coordinator (Actor Pattern)

Process navigation intentions sequentially to avoid race conditions.

```kotlin
class ActorCoordinator(
    private val navigator: Navigator,
    private val scope: CoroutineScope
) {
    private val intentions = Channel<NavigationIntention>(Channel.UNLIMITED)

    sealed interface NavigationIntention {
        data class Navigate(val route: String, val args: Bundle? = null) : NavigationIntention
        data object Pop : NavigationIntention
        data class PopTo(val route: String) : NavigationIntention
        data object Clear : NavigationIntention
    }

    init {
        scope.launch {
            for (intention in intentions) {
                when (intention) {
                    is NavigationIntention.Navigate -> navigator.navigateTo(intention.route, intention.args)
                    NavigationIntention.Pop -> navigator.pop()
                    is NavigationIntention.PopTo -> navigator.popTo(intention.route)
                    NavigationIntention.Clear -> navigator.clearBackStack()
                }
            }
        }
    }

    fun navigate(route: String, args: Bundle? = null) {
        intentions.trySend(NavigationIntention.Navigate(route, args))
    }

    fun pop() {
        intentions.trySend(NavigationIntention.Pop)
    }

    fun clear() {
        intentions.trySend(NavigationIntention.Clear)
    }
}
```

The Channel ensures navigation actions are processed one at a time, preventing race conditions during rapid user interaction.

## 11. Flow Navigator with CompletableDeferred for Activity Results

```kotlin
class FlowNavigator(
    private val activity: FragmentActivity
) {
    private val _results = MutableSharedFlow<ActivityResult>(extraBufferCapacity = 1)

    suspend fun navigateForResult(
        intent: Intent,
        requestCode: Int
    ): ActivityResult {
        val deferred = CompletableDeferred<ActivityResult>()
        val launcher = activity.activityResultRegistry.register(
            "nav_$requestCode",
            ActivityResultContracts.StartActivityForResult()
        ) { result ->
            deferred.complete(result)
        }
        launcher.launch(intent)
        return deferred.await()
    }
}
```

### Usage in Coordinator
```kotlin
class PaymentCoordinator(
    private val navigator: FlowNavigator,
    private val onPaymentComplete: (PaymentResult) -> Unit
) {
    suspend fun startPayment(orderId: String) {
        val intent = PaymentActivity.newIntent(orderId)
        val result = navigator.navigateForResult(intent, REQUEST_PAYMENT)
        when (result.resultCode) {
            Activity.RESULT_OK -> {
                val data = result.data?.getParcelableExtra<PaymentResult>("result")
                data?.let { onPaymentComplete(it) }
            }
            Activity.RESULT_CANCELED -> handleCancellation()
        }
    }

    companion object {
        private const val REQUEST_PAYMENT = 1001
    }
}
```

## 12. Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| God Coordinator | One coordinator handles all flows | One coordinator per flow, parent-child hierarchy |
| Stateful Coordinator | Stores UI state, breaks predictability | Stateless — only navigation decisions |
| Navigation in ViewModel | Couples business logic to navigation | ViewModel emits events, Coordinator handles routing |
| Navigation in Fragment/Activity | Cannot test, hard to change | Use Coordinator + Navigator abstraction |
| Hard-coded routes in ViewModel | ViewModel knows about UI structure | ViewModel emits domain events, Coordinator maps to routes |
| Singleton Coordinator | Global state, lifecycle issues | Create per-flow, dispose when flow completes |
| Nested Coordinator inheritance | Fragile base class, tight coupling | Composition with lambdas |
| Blocking navigation calls | ANR on main thread | Use Channel or Flow for async navigation |
| Ignoring back stack | Broken back navigation | Coordinator manages pop/clear explicitly |
| Coordinator doing business logic | Mixed concerns | Coordinator only routes, UseCases handle logic |
| Multiple Coordinators for one flow | Confusion, duplicated routing | One flow = one coordinator |
| Coordinator directly referencing Views | Lifecycle crashes | Coordinator talks to Navigator abstraction |

## Cross References

- Related rules: `nav-coordinator-pattern`, `nav-no-navigation-in-vm`, `nav-flow-coordinator`, `nav-root-coordinator`, `nav-parent-child`, `nav-navigator-abstraction`, `nav-ab-testing`, `nav-dsl-builder`, `nav-actor-coordinator`, `nav-no-god-coordinator`, `nav-stateless-coordinator`
- Related references: [`kotlin-conventions.md`](kotlin-conventions.md), [`coroutines.md`](coroutines.md), [`architecture.md`](architecture.md), [`compose-ui.md`](compose-ui.md)
