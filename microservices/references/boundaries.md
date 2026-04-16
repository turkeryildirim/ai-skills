# Service Boundaries & Decomposition

**Impact:** CRITICAL · **Prefix:** `boundary-` · **4 rules**

Bad boundaries cause every problem later — chatty calls, shared databases, deploy coupling. Get them right first.

## Load When

- Splitting a monolith into services
- Greenfield system design (draw the boundaries before writing code)
- Reviewing whether a new feature should go in an existing service or a new one
- Deciding whether to merge two chatty services

## Rules

| Rule | Summary |
|------|---------|
| [`boundary-ddd-bounded-contexts`](../rules/boundary-ddd-bounded-contexts.md) | One service = one bounded context; use ubiquitous language per context |
| [`boundary-database-per-service`](../rules/boundary-database-per-service.md) | Each service owns its schema; no shared DB access |
| [`boundary-single-responsibility`](../rules/boundary-single-responsibility.md) | One business capability per service — split when responsibilities drift |
| [`boundary-strangler-fig`](../rules/boundary-strangler-fig.md) | Extract from monolith incrementally behind a router |

## Decomposition Playbook

1. **Event storming** — gather team, map domain events on a wall, cluster into aggregates
2. **Identify bounded contexts** — each cluster of aggregates with a consistent ubiquitous language
3. **Map data ownership** — which aggregate owns which entity (no entity owned by two contexts)
4. **Check Conway's law** — can one team own each context? If not, split the team or the context
5. **Extract the weakest-coupled context first** (notifications, auth, reporting are common starting points)
6. **Strangler fig** — new feature goes in the new service; old path keeps running; route migrates

## Ownership Rules

- A service **owns** an entity if it is the source of truth for writes
- Other services hold **read projections** (cached copies updated via events) — never direct reads
- If two services both need to write the same entity → wrong boundary, merge or re-split

## Service Size Heuristic

- **Too small** — every feature touches 3+ services, chatty RPCs, deploy-coupling
- **Too large** — team can't understand it end-to-end, multiple unrelated bounded contexts inside
- **About right** — one team owns it; one bounded context; can be rewritten in ~2 sprints
