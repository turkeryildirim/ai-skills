# Swift Security — Keychain, CryptoKit, and Biometrics

Client-side security patterns for Apple platforms: Keychain Services, CryptoKit, Secure Enclave, biometric authentication, and credential lifecycle management.

## Seven Core Invariants (Non-Advisory — Always Apply)

1. **Always check `OSStatus` return values** from `SecItem*` calls exhaustively.
2. **Never use `LAContext.evaluatePolicy()` alone** for authentication — bind biometrics to keychain items.
3. **Never store secrets** in `UserDefaults`, plists, Info.plist, or source code.
4. **Never call `SecItem*` on `@MainActor`** — use dedicated background actors or queues.
5. **Always set `kSecAttrAccessible` explicitly** in keychain additions.
6. **Always implement add-or-update patterns** (avoid delete-then-add races).
7. **Always set `kSecUseDataProtectionKeychain: true` on macOS**.

## 1. Keychain Storage

```swift
// ✅ Dedicated background actor for keychain work
actor KeychainService {
    func store(secret: Data, key: String) throws {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrAccount: key,
            kSecAttrAccessible: kSecAttrAccessibleAfterFirstUnlock, // Always explicit
            kSecValueData: secret,
            kSecUseDataProtectionKeychain: true  // Required on macOS
        ]

        var status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecDuplicateItem {
            // Add-or-update pattern — not delete-then-add
            let update: [CFString: Any] = [kSecValueData: secret]
            status = SecItemUpdate(query as CFDictionary, update as CFDictionary)
        }

        guard status == errSecSuccess else {
            throw KeychainError.osStatus(status)
        }
    }
}

// ❌ Never on @MainActor
@MainActor
func store() {
    SecItemAdd(...) // Blocks UI thread
}
```

## 2. Keychain Accessibility Constants

| Constant | Available When | Use For |
|----------|---------------|---------|
| `kSecAttrAccessibleAfterFirstUnlock` | After first device unlock | Background refresh tokens |
| `kSecAttrAccessibleWhenUnlocked` | Device unlocked only | Interactive auth tokens |
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | Passcode set, no migration | High-security, no backup |
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Unlocked, no iCloud backup | Device-bound credentials |

## 3. Biometric Authentication (Bound to Keychain)

```swift
// ✅ Correct — biometrics bound to keychain item via Access Control
let access = SecAccessControlCreateWithFlags(
    nil,
    kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
    .biometryCurrentSet,  // Invalidates if biometrics change
    nil
)!

let query: [CFString: Any] = [
    kSecClass: kSecClassGenericPassword,
    kSecAttrAccount: "user-credential",
    kSecAttrAccessControl: access,
    kSecValueData: credentialData
]

// ❌ Wrong — boolean gate without keychain binding
let context = LAContext()
context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, ...) { success, _ in
    if success { /* nothing actually secured */ }
}
```

## 4. CryptoKit

### Symmetric Cryptography (iOS 13+)

```swift
import CryptoKit

// AES-GCM (preferred for encryption)
let key = SymmetricKey(size: .bits256)
let sealedBox = try AES.GCM.seal(plaintext, using: key)
let plaintext = try AES.GCM.open(sealedBox, using: key)

// HMAC for message authentication
let mac = HMAC<SHA256>.authenticationCode(for: data, using: key)
let isValid = HMAC<SHA256>.isValidAuthenticationCode(mac, authenticating: data, using: key)

// SHA-2 hashing
let digest = SHA256.hash(data: data)

// SHA-3 (iOS 26+)
let sha3Digest = SHA3_256.hash(data: data)  // iOS 26+
```

### Asymmetric Cryptography (iOS 13+)

```swift
// ECDSA signing
let privateKey = P256.Signing.PrivateKey()
let signature = try privateKey.signature(for: data)
let isValid = privateKey.publicKey.isValidSignature(signature, for: data)

// ECDH key agreement
let theirKey = P256.KeyAgreement.PublicKey(...)
let sharedSecret = try myPrivateKey.sharedSecretFromKeyAgreement(with: theirKey)
// Always derive from shared secret with HKDF — never use raw shared secret
let derivedKey = sharedSecret.hkdfDerivedSymmetricKey(using: SHA256.self, ...)
```

### HPKE (iOS 17+)

```swift
// Hybrid Public Key Encryption
let sender = try HPKE.Sender(recipientKey: recipientPublicKey, ciphersuite: .P256_SHA256_AES_GCM_256)
let encryptedMessage = try sender.seal(plaintext)
```

### Post-Quantum (iOS 26+)

```swift
// ML-KEM (Key Encapsulation Mechanism)
let recipientKey = try MLKem768.PrivateKey()
let (sharedSecret, encapsulated) = try MLKem768.encapsulate(recipientKey.publicKey)

// ML-DSA (Digital Signature)
let signingKey = try MLDSA65.PrivateKey()
let signature = try signingKey.signature(for: data)
```

## 5. Secure Enclave (iOS 13+)

```swift
// Hardware-generated P256 keys — cannot be imported or exported
guard SecureEnclave.isAvailable else {
    // Handle simulator / older devices without SE
    return
}

let privateKey = try SecureEnclave.P256.Signing.PrivateKey()
let storedKey = privateKey.dataRepresentation  // Store this reference, not the key

// CRITICAL: Cannot import keys into SE — they're hardware-generated only
// CRITICAL: Only P256 is supported in SE
```

## 6. Certificate Pinning

Prefer SPKI pinning or CA pinning over leaf certificate pinning:

```swift
// Via URLSession delegate
func urlSession(_ session: URLSession, task: URLSessionTask,
                didReceive challenge: URLAuthenticationChallenge,
                completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
    guard let serverTrust = challenge.protectionSpace.serverTrust,
          validatePinning(serverTrust) else {
        completionHandler(.cancelAuthenticationChallenge, nil)
        return
    }
    completionHandler(.useCredential, URLCredential(trust: serverTrust))
}
```

## 7. Credential Lifecycle

```swift
// On logout — clean up all credentials
func logout() async throws {
    try keychainService.deleteItem(key: "access-token")
    try keychainService.deleteItem(key: "refresh-token")
    try keychainService.deleteItem(key: "user-credential")
    // Clear in-memory token references
}

// First-launch cleanup (app reinstall doesn't clear Keychain)
func cleanStaleCredentials() throws {
    if !UserDefaults.standard.bool(forKey: "hasLaunchedBefore") {
        try keychainService.deleteAll()
        UserDefaults.standard.set(true, forKey: "hasLaunchedBefore")
    }
}
```

## 8. Common AI Generation Mistakes

| Mistake | Fix |
|---------|-----|
| LAContext boolean gate without keychain | Bind biometrics to keychain Access Control |
| `SecureEnclave.isAvailable` without simulator guard | Always guard SE with availability check |
| Importing keys into SE | Impossible — SE keys are hardware-generated |
| Missing `kSecAttrAccessible` | Always explicit in every `SecItemAdd` call |
| Ignoring `errSecDuplicateItem` | Implement add-or-update, not delete-then-add |
| Manual AES-GCM nonces | Let CryptoKit generate nonces — manual = reuse risk |
| Raw ECDH shared secret used directly | Always derive with HKDF |
| Missing first-launch keychain cleanup | Keychain persists across reinstalls |

## 9. Version Baseline

| API | Minimum iOS |
|-----|-------------|
| CryptoKit core (SHA-2, AES-GCM, P256) | iOS 13 |
| Secure Enclave P256 | iOS 13 |
| HPKE | iOS 17 |
| SHA-3 in CryptoKit | iOS 26 |
| ML-KEM / ML-DSA | iOS 26 |

## 10. Out of Scope

## Cross References

- Related rules: `sec-keychain-accessible`, `sec-no-userdefaults-secrets`, `sec-biometric-binding`, `sec-no-mainactor-secitem`
- Related references: [`networking.md`](networking.md), [`concurrency.md`](concurrency.md)

App Transport Security config, CloudKit encryption, server-side auth, WebAuthn server logic, code signing, jailbreak detection, and third-party crypto libraries.
