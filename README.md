# AI Skills & Agents

A collection of specialized expert skills and CLI wrapper agents designed for AI coding agents. Includes structured rules, hook references, best practices, and CLI wrappers across multiple domains.

## Agent Definitions

### CLI Wrapper Agents

Non-interactive CLI wrappers that format commands, execute via CLI, and return raw output. They never interpret or synthesize results.

| Agent | CLI Tool | Key Flags |
| :--- | :--- | :--- |
| **Gemini** | `gemini` | `--all-files`, `--yolo`, Here-Doc pipe |
| **Claude** | `claude` | `-p` (print mode), `--allowedTools`, `--output-format` |
| **Codex** | `codex` | `exec`, `-s read-only`, `-a never`, `-o` |
| **OpenCode** | `opencode` | `run`, `-f` (file attach), `--format json`, `--attach` |

Each CLI wrapper includes:
- Flag reference and command patterns
- Prompt formulation examples (`references/prompt-examples.md`)
- Dual-memory architecture for CLI behavior persistence

## Expert Skills

### Development Skills

| Skill | Description | Key Focus Areas |
| :--- | :--- | :--- |
| **API Design Patterns** | RESTful API design and best practices. | Resource design, Error handling (RFC 7807), Security, Pagination, gRPC, Versioning. |
| **Code Standards** | Universal code design and clean code principles. | SOLID, KISS, YAGNI, DRY, TDA, Testability, Complexity, Naming conventions. |
| **JavaScript / TypeScript** | Modern JS/TS for backend and advanced logic. | Node.js, Type systems, TS migration/interop, Runtime validation (Zod/io-ts), Backend architecture. |
| **Laravel** | Comprehensive Laravel 13 development. | Eloquent, Pest/PHPUnit, Database optimization, Caching, OWASP security, Inertia.js. |
| **Microservices** | Distributed systems patterns (PHP & TS). | Service boundaries, Data consistency (Saga/CQRS), Resilience, Observability, Idempotency. |
| **PHP** | Modern PHP 8.x patterns and PSR standards. | Type safety, PHP 8.4+ features, Enums, `declare(strict_types=1)`, Readonly, PSR-12, SOLID. |
| **PHPUnit** | Expert guidance for PHP testing. | AAA pattern, Framework-aware testing, Snapshot testing, CI/CD, Test isolation. |
| **SQL Expert** | Database design, queries, and optimization. | PostgreSQL/MySQL/SQLite/SQL Server, JSON/Full-text, Connection pooling, CTEs, Window functions. |

### Domain Skills

| Skill | Description | Key Focus Areas |
| :--- | :--- | :--- |
| **WordPress** | WordPress plugin/theme/backend development. | Block editor, Plugin architecture, REST API, Performance, WP-CLI, Theme dev, Hook reference (2672 hooks). |
| **WooCommerce** | WooCommerce development extending WordPress. | Products, Orders, Cart/Checkout, Payments, Shipping, Emails, REST API, Admin, Hook reference (2723 hooks). |

## How It Works

### Skill Structure

Each skill directory follows a consistent structure:
- **`SKILL.md`**: Entry point with core instructions and high-level overview.
- **`rules/`**: Discrete, actionable rules with "Bad" vs "Good" code examples.
- **`references/`**: Detailed documentation, deep-dives, and hook references.
- **`agents/`**: (Optional) Specialized system prompts for different agent roles.

### CLI Wrapper Structure

Each CLI wrapper directory contains:
- **`<name>.md`**: Agent definition with flag reference, command patterns, restrictions, and dual-memory system.
- **`references/prompt-examples.md`**: Proven prompt templates for common analysis tasks.

### Hook References (WordPress & WooCommerce)

Hook references are organized by domain in `references/hooks/`:
- **WordPress**: 20 files (10 action + 10 filter categories, 2672 non-deprecated hooks)
- **WooCommerce**: 22 files (11 action + 11 filter categories, 2723 hooks)
- **Variable hooks**: Dynamic hook patterns documented in `references/variable-hooks.md`

## Usage

### For Users
- Ask for a **code review** based on a specific skill (e.g., "Review this PHP code using the PHP skill").
- Request a **new feature** following specific standards (e.g., "Design a REST API endpoint following the API Design Patterns skill").
- Use for **debugging** (e.g., "Explain why this SQL query is slow using the SQL Expert skill").
- Delegate to a **CLI wrapper** for multi-agent analysis (e.g., "Use the OpenCode wrapper to analyze this codebase").

### For AI Agents
- Proactively load the relevant `SKILL.md` when a task matches its description.
- **Separation of Concerns (Mandatory):** Implementation agents (e.g., `typescript-pro`, `laravel-pro`) MUST NOT write tests. They should focus on architectural integrity and code generation, then explicitly request the calling agent to invoke the appropriate test-writing subagent (`js-test-writer`, `php-test-writer`).
- Reference specific rules in `rules/*.md` for concrete, example-backed feedback.
- Use `references/*.md` for deeper understanding of patterns or hook lookups.
- Invoke CLI wrapper agents for cross-model code analysis without interpreting results.

## Agent Delegation Flow

To maintain high specialization and context efficiency, follow this delegation pattern:

1.  **Architectural Design/Research:** Use `codebase_investigator` or `architecture-advisor`.
2.  **Implementation:** Use the specific `<domain>-pro` agent (e.g., `laravel-pro`).
3.  **Verification/Testing:** Use `js-test-writer` or `php-test-writer`. **Never combine implementation and testing in a single agent call.**
4.  **Review:** Use `js-code-reviewer` or `php-code-reviewer` for final validation.

## Scope

- **Covered**: Best practices, modern syntax (PHP 8.5, TS 5.x, Laravel 13, WordPress 6.9+, WooCommerce 9.6+), industry-standard design patterns, comprehensive hook references.
- **Not Covered**: Project-specific business logic, legacy framework versions, or non-technical project management.
