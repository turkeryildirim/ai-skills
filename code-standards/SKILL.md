---
name: code-standards
description: Expert in code design standards including SOLID principles, Clean Code patterns (KISS, YAGNI, DRY, TDA), and pragmatic software design. **ALWAYS use when designing ANY classes/modules, implementing features, fixing bugs, refactoring code, or writing functions.** Use proactively to ensure proper design, separation of concerns, simplicity, and maintainability. Examples - "create class", "design module", "implement feature", "refactor code", "fix bug", "is this too complex", "apply SOLID", "keep it simple", "avoid over-engineering".
model: inherit
---

# Code Standards & Design Principles

Universal code design and clean code principles for building maintainable, scalable, and simple software. Covers SOLID, KISS, YAGNI, DRY, and TDA patterns.

## Specialized Agents

Specialized personas for code design. Load these from `agents/` to provide expert context.

| Agent | Role | Focus |
|-------|------|-------|
| **code-standards-pro** | Design Expert | SOLID, Clean Code, KISS/YAGNI, complexity reduction. |

## When to Use

Proactively assist when:
- Designing new classes or modules
- Implementing features without over-abstraction
- Refactoring to remove unnecessary complexity
- Fixing bugs without adding abstractions
- Code reviews focused on simplicity
- User asks "is this too complex?"
- Detecting/preventing over-engineering
- Choosing duplication over coupling

**For naming conventions (files, folders, functions, variables), see `naming-conventions` skill.**

## Core Philosophy

1. **"Duplication Over Coupling"** — Prefer duplicating code between contexts over creating shared abstractions.
2. **"Start Ugly, Refactor Later"** — Don't create abstractions until you have 3+ real use cases.
3. **KISS Over DRY** — Simplicity beats premature abstraction every time.
4. **YAGNI Always** — Never add features or abstractions "just in case".

```typescript
// ✅ GOOD: Each entity is independent
export class User { /* Only what User needs */ }
export class Product { /* Only what Product needs */ }
```

## Core Directives

### MUST DO

- Keep functions small (< 20 lines) and focused on a single task
- Use meaningful names that explain **WHY**, not **WHAT**
- Apply the **Rule of Three**: only abstract after the 3rd occurrence
- Favor **Composition** over Inheritance
- Implement **Early Returns** to reduce nesting and improve readability
- Practice **Tell, Don't Ask (TDA)**: behavior should live with the data it operates on
- Ensure every class has a **Single Responsibility (SRP)**

### MUST NOT DO

- Create "God Classes" that handle multiple unrelated responsibilities
- Abstract code "just in case" it might be reused later (YAGNI violation)
- Use deep inheritance hierarchies (prefer shallow or flat structures)
- Suppress or ignore linter/compiler warnings without a very strong reason
- Add complex design patterns (e.g., Factory, Strategy) to simple problems
- Hardcode "magic numbers" or strings (use constants or enums)

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference | Rules |
|--:|----------|:------:|------------|-----------|:-----:|
| 1 | SOLID Principles | CRITICAL | Designing OOP systems, ensuring extensibility and maintainability | [`references/solid-principles.md`](references/solid-principles.md) | 5 |
| 2 | Clean Code Patterns | CRITICAL | Writing daily code, choosing between simplicity and abstraction | [`references/clean-code-principles.md`](references/clean-code-principles.md) | 4 |
| 3 | Function Design | HIGH | Designing methods, organizing logic, reducing complexity | [`references/function-design.md`](references/function-design.md) | 4 |
| 4 | Anti-Patterns | MEDIUM | Identifying common design mistakes and refactoring code | [`references/anti-patterns-and-examples.md`](references/anti-patterns-and-examples.md) | - |
| 5 | Pragmatic Software Design | HIGH | Enhancing readability, input safety, early returns, and cognitive simplicity | [`references/pragmatic-software-design.md`](references/pragmatic-software-design.md) | 5 |

## Rule Index

- **SOLID (OOP Design)**: SRP, OCP, LSP, ISP, DIP
- **Clean Code**: KISS, YAGNI, DRY, TDA
- **Function Design**: Small size, Meaningful names, Single level of abstraction, Early returns
- **Pragmatic Design**: Guard clauses (Fail-fast), No exceptions for control flow, No flag arguments, Explaining variables, DOP vs OOP boundaries

## Validation Checklist

- [ ] Each class/function has a single, well-defined responsibility (SRP)
- [ ] Code is as simple as possible; no premature abstractions (KISS/YAGNI)
- [ ] Duplication is only abstracted after the 3rd occurrence (DRY)
- [ ] Functions are small (< 20 lines) and easy to read
- [ ] Early returns are used to minimize nesting
- [ ] Names are meaningful and self-documenting
- [ ] Behavior lives with the data (TDA)
- [ ] Dependencies point toward abstractions, not concretions (DIP)
- [ ] Complexity is justified by the requirements, not "dogma"
- [ ] Guard clauses are used to validate inputs immediately and fail-fast
- [ ] Exceptions are not used for normal business control flow
- [ ] Methods do not use boolean flag parameters to steer execution paths
- [ ] Complex conditionals are broken down into well-named explaining variables

## External References

- [Clean Code, Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Refactoring, Martin Fowler](https://refactoring.com)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [KISS Principle](https://en.wikipedia.org/wiki/KISS_principle)
