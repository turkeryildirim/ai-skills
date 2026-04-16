# AI Skills

A collection of specialized expert skills designed for AI agents to assist with modern software engineering tasks. This repository contains structured rules, references, and best practices across various domains including API design, backend development, and system architecture.

## Available Skills

| Skill | Description | Key Focus Areas |
| :--- | :--- | :--- |
| **API Design Patterns** | RESTful API design and best practices. | Resource design, Error handling, Security, Pagination, Versioning. |
| **Code Standards** | Universal code design and clean code principles. | SOLID, KISS, YAGNI, DRY, TDA, Function design. |
| **JavaScript / TypeScript** | Modern JS/TS for backend and advanced logic. | Node.js, Type systems, Async patterns, Backend architecture, Testing. |
| **Laravel** | Comprehensive Laravel 13 development. | Eloquent, Pest/PHPUnit, Database optimization, OWASP security, Inertia.js. |
| **Microservices** | Distributed systems patterns (PHP & TS). | Boundaries, Resilience, Observability, Sagas, Event sourcing. |
| **PHP** | Modern PHP 8.x patterns and PSR standards. | Type safety, PHP 8.0-8.5 features, PSR-12, SOLID. |
| **PHPUnit** | Expert guidance for PHP testing. | AAA pattern, Mocking/Stubbing, Data providers, AI testing. |
| **SQL Expert** | Database design, queries, and optimization. | Complex JOINs, CTEs, Window functions, EXPLAIN plans, Normalization. |

## How It Works

Each skill directory follows a consistent structure:
- **`SKILL.md`**: The entry point for the AI, containing core instructions and a high-level overview.
- **`rules/`**: Discrete, actionable rules with "Bad" vs "Good" code examples.
- **`references/`**: Detailed documentation and deep-dives into specific sub-topics.
- **`agents/`**: (Optional) Specialized system prompts for different agent roles.

## Usage

These skills are intended to be "activated" or "loaded" by an AI agent (like Gemini CLI) when working on relevant tasks. 

### For Users
When interacting with an agent that has access to these skills:
- Ask for a **code review** based on a specific skill (e.g., "Review this PHP code using the PHP skill").
- Request a **new feature implementation** following specific standards (e.g., "Design a REST API endpoint for user profiles following the API Design Patterns skill").
- Use them for **debugging** (e.g., "Explain why this SQL query is slow using the SQL Expert skill").

### For AI Agents
- Proactively load the relevant `SKILL.md` when a task matches its description.
- Reference specific rules in `rules/*.md` to provide concrete, example-backed feedback.
- Use `references/*.md` when a deeper understanding of a pattern or principle is required.

## Scope

- **What's Covered**: Best practices, modern syntax (up to PHP 8.5, TS 5.x, Laravel 13), and industry-standard design patterns.
- **What's Not Covered**: Project-specific business logic, legacy framework versions (e.g., PHP 5, Laravel 5), or non-technical project management.
