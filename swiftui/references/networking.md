# Networking in SwiftUI

Modern networking patterns for iOS 15+ using URLSession with async/await and structured concurrency in Swift 6.3. No third-party dependencies required.

## Core Rule

**Never use completion-handler variants in new code.** Use only async/await variants.

## 1. URLSession with Async/Await

```swift
// ✅ Data request
let (data, response) = try await URLSession.shared.data(for: request)
guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
    throw NetworkError.badStatus((response as? HTTPURLResponse)?.statusCode ?? 0)
}
let result = try JSONDecoder().decode(MyModel.self, from: data)

// ✅ Download to disk
let (url, _) = try await session.download(for: request)

// ✅ Streaming (Server-Sent Events)
for try await line in session.bytes(for: request).lines { process(line) }
```

**CRITICAL:** URLSession does NOT throw for 4xx/5xx responses — it only throws for transport failures. Always validate HTTP status codes before decoding.

## 2. Production URLSession Configuration

```swift
let session: URLSession = {
    let config = URLSessionConfiguration.default
    config.timeoutIntervalForRequest = 30
    config.timeoutIntervalForResource = 300
    config.requestCachePolicy = .useProtocolCachePolicy
    config.httpAdditionalHeaders = ["Accept": "application/json"]
    return URLSession(configuration: config)
}()
```

Never use `URLSession.shared` in production code that requires custom configuration.

## 3. Protocol-Based API Client

```swift
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
}

final class UserService: UserServiceProtocol {
    private let session: URLSession

    init(session: URLSession = .shared) { self.session = session }

    func fetchUser(id: String) async throws -> User {
        let request = try URLRequest.user(id: id)
        let (data, response) = try await session.data(for: request)
        try validate(response)
        return try JSONDecoder().decode(User.self, from: data)
    }
}

// Testing: inject a mock URLProtocol subclass, NOT a mock URLSession
final class MockUserService: UserServiceProtocol {
    var stubbedUser: User?
    func fetchUser(id: String) async throws -> User { stubbedUser! }
}
```

## 4. Error Handling

```swift
enum NetworkError: Error {
    case noConnection
    case timedOut
    case cancelled
    case badStatus(Int)
    case decodingFailed(Error)
    case unknown(Error)

    init(_ urlError: URLError) {
        switch urlError.code {
        case .notConnectedToInternet: self = .noConnection
        case .timedOut: self = .timedOut
        case .cancelled: self = .cancelled
        default: self = .unknown(urlError)
        }
    }
}
```

## 5. Retry Logic

```swift
func fetch<T: Decodable>(_ request: URLRequest, maxRetries: Int = 3) async throws -> T {
    var attempt = 0
    while true {
        do {
            let (data, response) = try await session.data(for: request)
            try validate(response)
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            attempt += 1
            guard attempt < maxRetries,
                  !Task.isCancelled,
                  !is4xxError(error) else { throw error } // skip retry on 4xx
            try await Task.sleep(for: .seconds(pow(2.0, Double(attempt)))) // exponential backoff
        }
    }
}
```

- Respect cancellation: check `Task.isCancelled` before retrying.
- Skip 4xx errors (except 429 Too Many Requests).
- Use exponential backoff.

## 6. JSON Decoding

```swift
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
decoder.dateDecodingStrategy = .iso8601
```

## 7. Token Refresh (401 Handling)

Handle 401 responses with a single retry after refreshing the access token. Use an actor to prevent concurrent refresh races:

```swift
actor TokenRefreshActor {
    private var task: Task<String, Error>?

    func refreshToken() async throws -> String {
        if let existing = task { return try await existing.value }
        let newTask = Task<String, Error> { try await performRefresh() }
        task = newTask
        defer { task = nil }
        return try await newTask.value
    }
}
```

## 8. Background Transfers

Use `URLSessionConfiguration.background(withIdentifier:)` for large file downloads/uploads that must survive app termination. Implement `URLSessionDelegate` for progress and completion handling.

## 9. WebSocket

```swift
let task = session.webSocketTask(with: url)
task.resume()
let message = try await task.receive()
try await task.send(.string("ping"))
```

## 10. MUST NOT DO

## Cross References

- Related rules: `net-status-validation`, `net-no-shared-session`, `net-protocol-client`, `net-no-completion-handlers`, `conc-cooperative-cancellation`
- Related references: [`security.md`](security.md), [`concurrency.md`](concurrency.md), [`architecture.md`](architecture.md), [`../../swiftui-tester/references/swift-testing.md`](../../swiftui-tester/references/swift-testing.md)

- **URLSession.shared in production:** Never for code requiring timeouts, headers, or custom configuration.
- **Mock URLSession directly:** Use `URLProtocol` subclasses for testing instead.
- **Ignore HTTP status codes:** Always validate before decoding.
- **Requests in view body/init:** Fire requests only in `.task {}` or explicit user actions.
- **Third-party libraries (Alamofire, Moya):** Avoid when URLSession suffices.
- **Disable ATS:** Never in production. Exception domains require justification and are for legacy servers only.
- **Completion handlers:** All new networking code uses async/await exclusively.
