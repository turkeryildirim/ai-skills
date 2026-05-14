# Go Fuzz Testing

Fuzz targets, seed corpus, property invariants, and crash reproduction.

## What is Fuzzing?

Fuzzing automatically generates random inputs to find inputs that cause panics, incorrect behavior, or security vulnerabilities. The Go fuzzing engine (`go test -fuzz`) learns from code coverage to generate inputs that explore new code paths.

## Fuzz Function Structure

```go
func FuzzReverse(f *testing.F) {
    // 1. Seed corpus — initial interesting inputs
    f.Add("hello")
    f.Add("")
    f.Add("a")
    f.Add("日本語")                   // unicode
    f.Add("\x00\xff\xfe")           // binary data

    // 2. Fuzz target — called with generated inputs
    f.Fuzz(func(t *testing.T, input string) {
        // 3. Property invariants — must hold for all inputs
        reversed := Reverse(input)

        // Invariant: reversing twice returns original
        if Reverse(reversed) != input {
            t.Errorf("Reverse(Reverse(%q)) != original", input)
        }

        // Invariant: length is preserved
        if len(reversed) != len(input) {
            t.Errorf("Reverse changed length: %d -> %d", len(input), len(reversed))
        }
    })
}
```

## Running Fuzz Tests

```bash
# Run only seed corpus (fast, runs in CI like unit tests)
go test -run FuzzReverse ./...

# Enable fuzzing — runs until timeout or crash
go test -fuzz=FuzzReverse ./...

# Fuzz with time limit
go test -fuzz=FuzzReverse -fuzztime=60s ./...

# Fuzz with specific seed
go test -fuzz=FuzzReverse -fuzztime=30s ./pkg/...

# After finding a crash — reproduce it
go test -run FuzzReverse/testdata/fuzz/FuzzReverse/crash-file ./...
```

## Crash Corpus

When the fuzzer finds a failing input, it saves it to `testdata/fuzz/FuzzFunctionName/`:

```
testdata/
  fuzz/
    FuzzReverse/
      7c5f4f6e9b3c2a1d    ← crash that was found
      seed1               ← your f.Add() seeds (stored as files)
```

These files become permanent regression tests — they run with `go test ./...` without `-fuzz`.

## Supported Fuzz Input Types

```go
// Supported types: string, []byte, int, int8-64, uint, uint8-64, float32/64, bool, rune
f.Fuzz(func(t *testing.T,
    data []byte,
    n int,
    s string,
    flag bool,
) {
    // test logic
})

// For multiple inputs of the same type
f.Add([]byte{0x01, 0x02}, 42, "test", true)
```

## Good Fuzz Targets

Fuzzing works best for:

1. **Parsers and decoders** — find inputs that panic or corrupt state

```go
func FuzzParseConfig(f *testing.F) {
    f.Add(`{"key": "value"}`)
    f.Add(``)
    f.Add(`{invalid json`)

    f.Fuzz(func(t *testing.T, data string) {
        // Should never panic — must handle malformed input gracefully
        cfg, err := ParseConfig([]byte(data))
        if err != nil {
            return // error is acceptable
        }
        // If parse succeeded, round-trip should be stable
        if cfg != nil {
            out, err := cfg.Marshal()
            if err != nil {
                return
            }
            cfg2, err := ParseConfig(out)
            if err != nil {
                t.Errorf("round-trip failed: %v", err)
            }
            _ = cfg2
        }
    })
}
```

2. **Security-sensitive code** — path handling, input validation, crypto

```go
func FuzzSanitizePath(f *testing.F) {
    f.Add("../../../etc/passwd")
    f.Add("normal/path/to/file.txt")
    f.Add("")
    f.Add("/absolute/path")

    f.Fuzz(func(t *testing.T, input string) {
        result := SanitizePath(input)

        // Invariant: result must never contain ".."
        if strings.Contains(result, "..") {
            t.Errorf("SanitizePath(%q) = %q contains path traversal", input, result)
        }

        // Invariant: result must not start with "/"
        if strings.HasPrefix(result, "/") {
            t.Errorf("SanitizePath(%q) = %q is absolute", input, result)
        }
    })
}
```

3. **Serialization round-trips** — encode/decode should be inverse operations

```go
func FuzzJSONRoundTrip(f *testing.F) {
    f.Add(`{"name":"Alice","age":30}`)

    f.Fuzz(func(t *testing.T, data []byte) {
        var v map[string]any
        if err := json.Unmarshal(data, &v); err != nil {
            return // invalid JSON — skip
        }
        out, err := json.Marshal(v)
        if err != nil {
            t.Errorf("Marshal failed for valid data: %v", err)
        }
        var v2 map[string]any
        if err := json.Unmarshal(out, &v2); err != nil {
            t.Errorf("second Unmarshal failed: %v", err)
        }
    })
}
```

## What Makes a Good Property Invariant

```go
f.Fuzz(func(t *testing.T, input []byte) {
    result, err := Process(input)

    // 1. Must not panic (implicit — fuzzer catches panics automatically)

    // 2. Error/success is consistent — no silent failures
    if err != nil {
        // error path — verify error is meaningful
        if result != nil {
            t.Error("result must be nil on error")
        }
        return
    }

    // 3. Output invariants on the success path
    if len(result) == 0 {
        t.Error("successful result must not be empty")
    }

    // 4. Round-trip properties
    restored, err := Unprocess(result)
    if err != nil {
        t.Errorf("Unprocess(Process(input)) failed: %v", err)
    }
    if !bytes.Equal(restored, input) {
        t.Errorf("round-trip mismatch: got %x, want %x", restored, input)
    }
})
```

## Corpus Files in testdata/

You can add interesting inputs directly as files:

```
testdata/fuzz/FuzzMyFunc/
  corpus1    ← text file, one value per line
  corpus2
```

Format for `[]byte` and `string`:
```
go test fuzz v1
[]byte("hello\x00world")
```

## CI Integration

Fuzz targets run their seed corpus in CI (without `-fuzz` flag):

```yaml
# .github/workflows/test.yml
- name: Run tests (including fuzz seed corpus)
  run: go test -race ./...  # runs FuzzXxx seed corpus, not full fuzzing
```

For continuous fuzzing in CI, use `gotip` or run with a short timeout:

```yaml
- name: Fuzz (short run)
  run: go test -fuzz=FuzzParseConfig -fuzztime=30s ./pkg/config/
```
