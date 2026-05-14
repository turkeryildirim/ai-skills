# Go Dependency Management

`go mod`, semantic versioning, vulnerability scanning, and dependency hygiene.

## When to Load

- Adding, removing, or upgrading dependencies
- Auditing dependencies for vulnerabilities or bloat
- Setting up automated dependency updates
- Resolving version conflicts in go.mod

## Key Rules

1. **Ask before adding** — does the standard library already solve this? Every dependency adds attack surface and maintenance burden
2. **Commit `go.sum`** — records cryptographic checksums; prevents supply-chain tampering
3. **Run `govulncheck ./...` before every release** — catches known CVEs
4. **Run `go mod tidy` before every commit** that changes dependencies
5. Prefer packages from `golang.org/x/...` or well-established organizations over obscure alternatives

## Essential Commands

```bash
# Module setup
go mod init github.com/user/project
go mod tidy        # add missing, remove unused
go mod download    # download to local cache
go mod verify      # verify checksums match go.sum
go mod vendor      # copy deps into vendor/

# Add / upgrade
go get github.com/pkg/errors           # latest
go get github.com/pkg/errors@v0.9.1    # specific version
go get -u ./...                        # upgrade all to latest minor/patch
go get -u=patch ./...                  # safer: patch versions only

# Remove
go get github.com/pkg/errors@none && go mod tidy

# Inspect
go mod graph       # full dependency tree
go mod why github.com/foo/bar  # why is this module needed?

# Tools
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Vulnerability scanning
govulncheck ./...  # scan for known CVEs
```

## Prefer Patch Updates

```bash
go get -u=patch ./...   # safer — patch versions don't change public API
go get -u ./...         # minor updates — may have behavior changes
```

Semver promise: patch versions (`x.y.Z`) fix bugs without API changes. Minor versions (`x.Y.z`) add features but may change behavior.

## Pinning Tool Versions — tools.go Pattern

```go
//go:build tools

package tools

import (
    _ "github.com/golangci/golangci-lint/cmd/golangci-lint"
    _ "golang.org/x/vuln/cmd/govulncheck"
)
```

The build constraint prevents compilation. The blank imports keep tools in `go.mod` so `go install` uses the pinned version.

## Vendoring

Use `vendor/` when you need hermetic builds (no network access in CI, Docker):

```bash
go mod vendor             # create vendor/ directory
go build -mod=vendor ./... # build using vendor/
```

Commit `vendor/` to the repository. Re-run `go mod vendor` after any dependency change.

## Vulnerability Scanning

```bash
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...   # reports CVEs reachable from your code (not just in go.mod)
```

Run in CI before every release. `govulncheck` only reports CVEs in code paths that your binary actually calls — no false positives from unused transitive dependencies.

## Semantic Versioning

| Change | Bump | Example |
|---|---|---|
| Bug fix, no API change | Patch | v1.2.3 → v1.2.4 |
| New feature, backward-compatible | Minor | v1.2.3 → v1.3.0 |
| Breaking API change | Major | v1.x.x → v2.0.0 |

For v2+, the module path must include the major version:
```
module github.com/user/pkg/v2
```

## Automated Updates

### Dependabot (.github/dependabot.yml)

```yaml
version: 2
updates:
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

### Renovate (renovate.json)

```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchManagers": ["gomod"],
      "automerge": true,
      "matchUpdateTypes": ["patch"]
    }
  ]
}
```

Auto-merge patch updates; require human review for minor and major.

## References

- [Go Modules Reference](https://go.dev/ref/mod)
- [govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck)
- [Semantic Versioning](https://semver.org)
- [Minimal Version Selection](https://research.swtch.com/vgo-mvs)
