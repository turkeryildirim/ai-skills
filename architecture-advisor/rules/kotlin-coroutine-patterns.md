---
title: Kotlin Coroutine and Concurrency Analysis
impact: CRITICAL
impactDescription: "Improper coroutine scope management, blocking dispatchers, and uncaught exceptions crash applications and block thread execution"
tags: kotlin, coroutines, flow, concurrency, async
---

## Kotlin Coroutine and Concurrency Analysis

**Impact: CRITICAL (Improper coroutine scope management, blocking dispatchers, and uncaught exceptions crash applications and block thread execution)**

Kotlin Coroutines offer simple, powerful asynchronous programming. However, mismanaging scopes, blocking main dispatchers, ignoring exceptions, or leaking subscriptions will lead to performance bottlenecks, memory leaks, and frequent app crashes.

## Incorrect

```kotlin
// ❌ Dangerous Scope management, blocking Main dispatcher, and lack of error handling

class OrderViewModel : ViewModel() {
    private val _orderState = MutableStateFlow<OrderState>(OrderState.Idle)
    val orderState: StateFlow<OrderState> = _orderState

    fun loadOrderDetails(orderId: String) {
        // ❌ Leaks scope, ignores ViewModel destruction, runs indefinitely
        GlobalScope.launch {
            try {
                // ❌ Blocks the UI thread if executed directly on Dispatchers.Main (implicit default for Hilt/View scope)
                val response = networkApi.fetchOrder(orderId) 
                
                // ❌ Reading local disk blocking I/O directly in UI Coroutine context
                val localDbData = readDatabaseBlocking() 

                _orderState.value = OrderState.Success(response, localDbData)
            } catch (e: Exception) {
                // ❌ Swallows or crashes without SupervisorJob context
                Log.e("Order", "Error", e)
            }
        }
    }

    private fun readDatabaseBlocking(): List<Item> {
        Thread.sleep(2000) // ❌ Simulation of heavy synchronous I/O blocking thread
        return emptyList()
    }
}
```

## Correct

```kotlin
// ✅ ViewModel-scoped concurrency, injected dispatchers, non-blocking I/O, and safe Flows

// CoroutineDispatcherProvider.kt (DI abstraction for testability)
interface DispatcherProvider {
    fun main(): CoroutineDispatcher
    fun io(): CoroutineDispatcher
    fun default(): CoroutineDispatcher
}

class DefaultDispatcherProvider @Inject constructor() : DispatcherProvider {
    override fun main() = Dispatchers.Main
    override fun io() = Dispatchers.IO
    override fun default() = Dispatchers.Default
}

class OrderViewModel @Inject constructor(
    private val orderRepository: OrderRepository,
    private val dispatchers: DispatcherProvider // ✅ Inject dispatchers to make tests predictable
) : ViewModel() {

    private val _orderState = MutableStateFlow<OrderState>(OrderState.Idle)
    val orderState: StateFlow<OrderState> = _orderState.asStateFlow() // ✅ Encapsulate mutable state

    fun loadOrderDetails(orderId: String) {
        // ✅ ViewModelScope cancels automatically when ViewModel is cleared
        viewModelScope.launch(dispatchers.main()) {
            _orderState.value = OrderState.Loading
            
            // ✅ supervisorScope prevents failure of one task from canceling neighboring tasks
            supervisorScope {
                val dbTask = async(dispatchers.io()) { 
                    orderRepository.getLocalItems() // ✅ Swapped to IO Thread pool
                }
                val networkTask = async(dispatchers.io()) { 
                    orderRepository.fetchRemoteOrder(orderId) // ✅ Swapped to IO Thread pool
                }

                try {
                    val dbData = dbTask.await()
                    val remoteData = networkTask.await()
                    _orderState.value = OrderState.Success(remoteData, dbData)
                } catch (e: Exception) {
                    _orderState.value = OrderState.Error(e.message ?: "Unknown error")
                }
            }
        }
    }
}
```

## Concurrency Compliance Assessment

```
CRITICAL violations:
├── `runBlocking` used in production main-thread paths (e.g. Android main thread or Ktor endpoints)
├── `GlobalScope` used for launching non-application-wide long-running operations
└── Blocking I/O or CPU-heavy calls executed in UI or Main coroutine context without switching context

HIGH violations:
├── Hardcoded Dispatchers (e.g. `Dispatchers.IO`) in constructor/class bodies without injection
├── Catching all exceptions with `catch (t: Throwable)` without re-throwing `CancellationException`
└── Coroutines launched in long-lived repositories/services without cancellation tracking

MEDIUM violations:
├── Flows collected inside Android activities/fragments without `repeatOnLifecycle` or `flowWithLifecycle`
├── `SharedFlow` or `StateFlow` instantiated without clean fallback or initial state
└── `Channel` usage when `StateFlow`/`SharedFlow` would represent state transitions more reliably

LOW violations:
├── Excessive use of `withContext(Dispatchers.IO)` on methods that are already suspend-safe
└── Re-creating CoroutineContext elements unnecessarily on every launch
```

## Concurrency Signals

```
✅ Healthy Coroutine patterns:
viewModelScope.launch { ... }           → tied to component lifecycles
withContext(dispatchers.io()) { ... }  → shifting I/O off the main thread
repeatOnLifecycle(Lifecycle.State.STARTED) → collecting flows safely in UI
suspend functions                     → naturally non-blocking and safe to call from any thread

❌ Warning signals:
GlobalScope.launch { ... }            → memory leakage and unmanaged execution
runBlocking { ... }                   → freezes active thread, blocks execution
Thread.sleep(...)                     → blocking API inside coroutine scope (use delay(...) instead)
```

## Why

- **Structured Concurrency**: Coroutines launched within predefined scopes (like `viewModelScope` or custom scopes with a parent `Job`) ensure that when the scope is cancelled, all active child tasks are cleaned up, preventing memory leaks and orphaned tasks.
- **Dispatcher Isolation**: Delegating database, file I/O, or massive serialization tasks to `Dispatchers.IO` keeps the main (UI) thread highly responsive, preventing Frame Drops (Jank) and "Application Not Responding" (ANR) errors.
- **Cancellation Cooperative**: Coroutines must be cooperative with cancellation. Standard suspend functions check for cancellation automatically, but custom loops must check `isActive` or call `yield()` to avoid running infinitely after cancellation.
