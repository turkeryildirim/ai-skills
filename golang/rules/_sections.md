# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Idiomatic Go (idiomatic)

**Impact:** CRITICAL
**Description:** Go has strong conventions enforced by the community and toolchain. Names, receivers, package layout, and exported documentation must follow these conventions for code to be accepted in professional Go projects.

## 2. Error Handling (error)

**Impact:** CRITICAL
**Description:** Go uses explicit error values instead of exceptions. Rules cover wrapping errors with context, defining sentinel errors, creating custom error types, and avoiding `panic` for expected conditions.

## 3. Concurrency (conc)

**Impact:** CRITICAL
**Description:** Go's goroutines and channels are powerful but require discipline. Rules cover goroutine lifecycle, channel directionality, context cancellation, data race prevention, and proper use of `sync.Mutex` / `sync.WaitGroup`.

## 4. Types & Interfaces (type)

**Impact:** HIGH
**Description:** Go's type system rewards small interfaces, zero-value usability, and composition. Rules cover interface design, generics, embedding, and type assertion safety.

## 5. Testing (test)

**Impact:** HIGH
**Description:** Table-driven tests, subtests (`t.Run`), and interface-based mocking are Go idioms. Rules cover test structure, benchmark writing, and avoiding test pollution.

## 6. Code Style (style)

**Impact:** HIGH
**Description:** Style rules that require human judgment — linters handle formatting, this section handles clarity. Covers early returns, eliminating unnecessary else, switch over if-else chains, extracting complex conditions, function design, value vs pointer arguments, and string handling.

## 7. Performance (perf)

**Impact:** MEDIUM
**Description:** Performance optimizations including pre-allocation, `strings.Builder`, `sync.Pool`, and escape analysis. Profile before optimizing — measure, then act.

## 8. Security (sec)

**Impact:** CRITICAL
**Description:** Security practices including input validation, prepared SQL statements, cryptographic primitives from `crypto/...`, and safe TLS configuration to protect against common vulnerabilities.
