# Go Project Layout

Project structure, module naming, directory conventions, and initialization checklist. Right-size structure to the problem — a script stays flat, a service gets layers only when justified by actual complexity.

## When to Load

- Starting a new Go project
- Organizing an existing codebase
- Setting up a monorepo or workspace
- Deciding on directory structure

## Architecture Decision: Ask First

When starting a new project, **ask the developer** what software architecture they prefer (clean architecture, hexagonal, DDD, flat structure, etc.). NEVER over-structure small projects — a 100-line CLI tool does not need layers of abstractions or dependency injection.

## 12-Factor App

For applications (services, APIs, workers), follow [12-Factor App](https://12factor.net/) conventions:
- Config via environment variables
- Logs to stdout
- Stateless processes
- Graceful shutdown
- Backing services as attached resources
- Admin tasks as one-off commands (e.g., `cmd/migrate/`)

## Project Types

| Project Type | Use When | Key Directories |
|---|---|---|
| **CLI Tool** | Building a command-line application | `cmd/{name}/`, `internal/`, optional `pkg/` |
| **Library** | Creating reusable code for others | `pkg/{name}/`, `internal/` for private code |
| **Service** | HTTP API, microservice, or web app | `cmd/{service}/`, `internal/`, `api/`, `web/` |
| **Monorepo** | Multiple related packages/modules | `go.work`, separate modules per package |

## Module Naming

Your module path in `go.mod` must:
- **Match your repository URL**: `github.com/username/project-name`
- **Use lowercase only**: `github.com/you/my-app` not `MyApp`
- **Use hyphens for multi-word**: `user-auth` not `user_auth` or `userAuth`

```go
// Good
module github.com/jdoe/payment-processor
module github.com/company/cli-tool

// Bad
module myproject              // no repo path
module github.com/jdoe/MyProject  // uppercase
module utils                  // non-descriptive
```

## Directory Layout

All `main` packages must reside in `cmd/` with minimal logic — parse flags, wire dependencies, call `Run()`. Business logic belongs in `internal/` or `pkg/`. Use `internal/` for non-exported packages, `pkg/` only when code is useful to external consumers.

### Standard Service Layout

```
myservice/
  cmd/
    server/
      main.go          ← wire + start only
    migrate/
      main.go          ← admin command
  internal/
    user/
      user.go
      user_repo.go
      user_service.go
      user_test.go
    order/
      order.go
      ...
  pkg/                 ← only if external consumers need it
    apiclient/
      client.go
  api/                 ← OpenAPI specs, protobuf
  web/                 ← static assets
  Makefile
  .gitignore
  .golangci.yml
  go.mod
  go.sum
```

### Library Layout

```
mylib/
  mylib.go             ← primary package
  mylib_test.go
  internal/
    helpers/
  examples/
  README.md
  go.mod
```

### CLI Tool Layout

```
mycli/
  cmd/
    root.go
    serve.go
    migrate.go
  internal/
    config/
    runner/
  main.go              ← or cmd/mycli/main.go
```

## Essential Configuration Files

Every Go project should include at the root:

- **`go.mod`** — module definition and dependencies
- **`go.sum`** — dependency checksums (commit this)
- **`Makefile`** — build automation (`make build`, `make test`, `make lint`)
- **`.gitignore`** — include binaries, `vendor/`, `*.prof`
- **`.golangci.yml`** — linter config (see `references/linting.md`)

## Test File Placement

Co-locate `_test.go` files with the code they test:

```
internal/user/
  user.go
  user_test.go         ← white-box tests (same package)
  user_integration_test.go  ← //go:build integration
```

Use `testdata/` for fixtures:

```
internal/parser/
  parser.go
  parser_test.go
  testdata/
    valid.json
    invalid.json
```

## Go Workspaces (Monorepo)

Use `go.work` when developing multiple related modules locally:

```bash
go work init
go work use ./services/user
go work use ./services/order
go work use ./pkg/shared
```

```
monorepo/
  go.work
  go.work.sum
  services/
    user/
      go.mod
      go.sum
    order/
      go.mod
      go.sum
  pkg/
    shared/
      go.mod
      go.sum
```

## Initialization Checklist

When starting a new Go project:

- [ ] Decide project type (CLI, library, service, monorepo)
- [ ] Ask preferred architecture (clean, hexagonal, DDD, flat)
- [ ] Right-size structure to the project scope
- [ ] Choose module name (matches repo URL, lowercase, hyphens)
- [ ] Run `go version` to detect current Go version
- [ ] Run `go mod init github.com/user/project-name`
- [ ] Create `cmd/{name}/main.go` for entry point (minimal — wire + start)
- [ ] Create `internal/` for private business logic
- [ ] Create `pkg/` only if you have packages for external consumers
- [ ] Add `.gitignore` with `/vendor/`, binaries, and `*.prof`
- [ ] Add `.golangci.yml` (see `references/linting.md`)
- [ ] Run `gofmt -s -w .` to ensure formatting

## References

- [Standard Go Project Layout](https://github.com/golang-standards/project-layout)
- [12-Factor App](https://12factor.net/)
- [Go Modules Reference](https://go.dev/ref/mod)
- [Go Workspaces](https://go.dev/doc/tutorial/workspaces)
