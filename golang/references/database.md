# Go Database Access

Safe, explicit, and observable database code. SQL as a first-class language — no ORMs, no magic.

## When to Load

- Writing repository functions, query helpers, or transaction wrappers
- Auditing for SQL injection, missing `rows.Close()`, or absent context propagation
- Choosing between `database/sql`, `sqlx`, and `pgx`
- Handling nullable columns, transactions, or connection pool configuration

## Library Choice

| Library | Best for | Struct scanning | PostgreSQL-specific |
|---|---|---|---|
| `database/sql` | Portability, minimal deps | Manual `Scan` | No |
| `sqlx` | Multi-database projects | `StructScan`, `GetContext`, `SelectContext` | No |
| `pgx` | PostgreSQL (30–50% faster) | `pgx.RowToStructByName` | Yes (COPY, LISTEN, arrays) |
| GORM/ent | **Avoid** — unpredictable queries | Magic | Abstracted away |

**Why NOT ORMs:**
- Unpredictable query generation, N+1 problems invisible in code
- Magic hooks and callbacks make debugging harder
- Schema migrations coupled to application code

## Core Rules

1. Queries MUST use parameterized placeholders — NEVER concatenate user input into SQL
2. Context MUST be passed to all operations — use `*Context` variants (`QueryContext`, `ExecContext`, `GetContext`)
3. `sql.ErrNoRows` MUST be handled explicitly — distinguish "not found" from real errors
4. Rows MUST be closed after iteration — `defer rows.Close()` immediately after `QueryContext`
5. NEVER use `db.Query` for non-SELECT statements — use `db.Exec` to avoid connection leaks
6. Connection pool MUST be configured — `SetMaxOpenConns`, `SetMaxIdleConns`, `SetConnMaxLifetime`
7. Use `SELECT ... FOR UPDATE` when reading data you intend to modify
8. Wrap related writes in transactions for multi-statement operations
9. Handle nullable columns with pointer fields (`*string`, `*int`) or `sql.NullXxx` types
10. Use external tools for migrations — golang-migrate or Flyway, never hand-rolled SQL

## Parameterized Queries

```go
// Bad — SQL injection vulnerability
query := fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email)

// Good — parameterized (PostgreSQL)
var user User
err := db.GetContext(ctx, &user,
    "SELECT id, name, email FROM users WHERE email = $1", email)

// Good — parameterized (MySQL)
err := db.GetContext(ctx, &user,
    "SELECT id, name, email FROM users WHERE email = ?", email)
```

### Dynamic IN clauses

```go
query, args, err := sqlx.In("SELECT * FROM users WHERE id IN (?)", ids)
if err != nil {
    return fmt.Errorf("building IN clause: %w", err)
}
query = db.Rebind(query)
err = db.SelectContext(ctx, &users, query, args...)
```

### Dynamic column names — use an allowlist

```go
allowed := map[string]bool{"name": true, "email": true, "created_at": true}
if !allowed[sortCol] {
    return fmt.Errorf("invalid sort column: %s", sortCol)
}
query := fmt.Sprintf("SELECT id, name FROM users ORDER BY %s", sortCol)
```

## Error Handling

```go
func GetUser(ctx context.Context, id string) (*User, error) {
    var user User
    err := db.GetContext(ctx, &user,
        "SELECT id, name FROM users WHERE id = $1", id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrUserNotFound // translate to domain error
        }
        return nil, fmt.Errorf("querying user %s: %w", id, err)
    }
    return &user, nil
}
```

Alternative — returning existence flag instead of sentinel error:

```go
func GetUser(ctx context.Context, id string) (*User, bool, error) {
    var user User
    err := db.GetContext(ctx, &user,
        "SELECT id, name FROM users WHERE id = $1", id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, false, nil
        }
        return nil, false, fmt.Errorf("querying user %s: %w", id, err)
    }
    return &user, true, nil
}
```

### Always close rows

```go
rows, err := db.QueryContext(ctx, "SELECT id, name FROM users")
if err != nil {
    return fmt.Errorf("querying users: %w", err)
}
defer rows.Close() // prevents connection leaks

for rows.Next() {
    var u User
    if err := rows.Scan(&u.ID, &u.Name); err != nil {
        return fmt.Errorf("scanning user: %w", err)
    }
    users = append(users, u)
}
if err := rows.Err(); err != nil { // always check after iteration
    return fmt.Errorf("iterating users: %w", err)
}
```

### Common error patterns

| Error | How to detect | Action |
|---|---|---|
| Row not found | `errors.Is(err, sql.ErrNoRows)` | Return domain error |
| Unique constraint | Driver-specific error code | Return conflict error |
| Connection refused | `err != nil` on `db.PingContext` | Fail fast, retry with backoff |
| Serialization failure | PostgreSQL error code `40001` | Retry the entire transaction |
| Context canceled | `errors.Is(err, context.Canceled)` | Stop processing, propagate |

## Struct Scanning

```go
// sqlx — db:"column_name" tags
type User struct {
    ID        string     `db:"id"`
    Name      string     `db:"name"`
    Email     *string    `db:"email"`       // nullable
    CreatedAt time.Time  `db:"created_at"`
    DeletedAt *time.Time `db:"deleted_at"`  // nullable
}

var user User
err := db.GetContext(ctx, &user, "SELECT id, name, email FROM users WHERE id = $1", id)

var users []User
err := db.SelectContext(ctx, &users, "SELECT id, name, email FROM users")
```

## Transactions

```go
func Transfer(ctx context.Context, db *sqlx.DB, fromID, toID string, amount int) error {
    tx, err := db.BeginTxx(ctx, nil)
    if err != nil {
        return fmt.Errorf("begin transaction: %w", err)
    }
    defer tx.Rollback() // no-op after Commit; safe to always defer

    var balance int
    if err := tx.QueryRowContext(ctx,
        "SELECT balance FROM accounts WHERE id = $1 FOR UPDATE", fromID,
    ).Scan(&balance); err != nil {
        return fmt.Errorf("querying balance: %w", err)
    }

    if balance < amount {
        return ErrInsufficientFunds
    }

    if _, err := tx.ExecContext(ctx,
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2", amount, fromID,
    ); err != nil {
        return fmt.Errorf("deducting balance: %w", err)
    }

    if _, err := tx.ExecContext(ctx,
        "UPDATE accounts SET balance = balance + $1 WHERE id = $2", amount, toID,
    ); err != nil {
        return fmt.Errorf("adding balance: %w", err)
    }

    return tx.Commit()
}
```

### Isolation Levels

```go
// Default is READ COMMITTED — override when needed
tx, err := db.BeginTxx(ctx, &sql.TxOptions{
    Isolation: sql.LevelSerializable, // for financial operations
    ReadOnly:  false,
})
```

| Level | When to use |
|---|---|
| `READ COMMITTED` | Default — suitable for most reads |
| `REPEATABLE READ` | Multiple reads in same transaction must see same data |
| `SERIALIZABLE` | Financial operations, inventory updates — prevents phantom reads |

### SELECT FOR UPDATE

```go
// Read + lock row before modifying
var qty int
err := tx.QueryRowContext(ctx,
    "SELECT quantity FROM inventory WHERE id = $1 FOR UPDATE", itemID,
).Scan(&qty)
```

## Connection Pool Configuration

```go
db, err := sqlx.Open("pgx", connStr)
if err != nil {
    return fmt.Errorf("opening db: %w", err)
}

db.SetMaxOpenConns(25)                      // limit total connections
db.SetMaxIdleConns(10)                      // keep warm connections ready
db.SetConnMaxLifetime(5 * time.Minute)      // recycle stale connections
db.SetConnMaxIdleTime(1 * time.Minute)      // close idle connections faster

if err := db.PingContext(ctx); err != nil {
    return fmt.Errorf("db not reachable: %w", err)
}
```

## Batch Processing

```go
// Bad — one round trip per row
for _, user := range users {
    _, err := db.ExecContext(ctx, "INSERT INTO users (id, name) VALUES ($1, $2)", user.ID, user.Name)
    // ...
}

// Good — batch in reasonable sizes (100–1000)
const batchSize = 500
for i := 0; i < len(users); i += batchSize {
    batch := users[i:min(i+batchSize, len(users))]
    // use sqlx.NamedExec or pgx COPY for bulk inserts
}
```

## Context Propagation

Always use `*Context` variants — they propagate deadlines and cancellation to the database driver:

```go
// Bad — query runs until completion even if client disconnects
db.Query("SELECT ...")

// Good — respects context cancellation and timeouts
db.QueryContext(ctx, "SELECT ...")
```

## References

- [database/sql documentation](https://pkg.go.dev/database/sql)
- [sqlx](https://github.com/jmoiron/sqlx)
- [pgx](https://github.com/jackc/pgx)
- [golang-migrate](https://github.com/golang-migrate/migrate)
