---
name: react-architecture-guide
description: React, Next.js, and Remix architecture patterns, state management benchmarks, and component quality metrics for architectural analysis.
type: reference
---

# React Architecture Guide

Reference for analyzing React, Next.js, and Remix projects.

## Maturity Levels

| Level | Signals |
|-------|---------|
| **Level 1** | Class components, no hooks, jQuery mixed |
| **Level 2** | Functional components, useState everywhere, data in useEffect |
| **Level 3** | Custom hooks, component decomposition, React Query for server state |
| **Level 4** | Feature-based folder structure, typed (TypeScript), code splitting |
| **Level 5** | Server Components (Next.js), typed API layer (tRPC), >60% test coverage |

---

## State Management Selection Guide

### Rule of thumb: match the solution to the scale

| App Scale | Recommended State Solution |
|-----------|---------------------------|
| <5 pages, 1-2 global pieces of state | useState + Context |
| 5-20 pages, auth/theme/cart global | Zustand (1-3 stores) |
| 20+ pages, complex interactions | Zustand + React Query |
| Enterprise with normalized data | Redux Toolkit + React Query |
| Next.js App Router | Server Components + `use()` + Zustand for client state |

### State Type → Correct Tool Mapping
```
Server data (API responses)     → React Query / SWR / tRPC
Local UI state (modal, toggle)  → useState
Form state                      → React Hook Form / Formik
URL-reflected state (filters)   → useSearchParams
Global auth/theme/cart          → Zustand / Context
```

---

## Component Quality Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|---------|
| Component file size | <100 lines | 100-200 lines | >200 lines |
| Props count | ≤4 | 5-7 | >7 |
| State variables (useState) | ≤3 | 4-5 | >5 |
| useEffect count | ≤2 | 3 | >3 |
| Props drilling depth | 1-2 | 3 | >3 |
| JSX return lines | <40 | 40-80 | >80 |

---

## Folder Structure Patterns

### Feature-Based (Recommended for >10 routes)
```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── index.ts        → Public API of feature
│   ├── orders/
│   └── products/
├── shared/
│   ├── components/         → Truly reusable UI (Button, Modal, Input)
│   ├── hooks/              → App-wide hooks (useDebounce, useLocalStorage)
│   └── lib/                → Third-party client setup (queryClient, axios)
└── app/                    → Next.js App Router or router config
```

### Type-Based (Acceptable for <5 routes, gets messy quickly)
```
src/
├── components/
├── hooks/
├── pages/ or app/
├── services/
└── store/
```

---

## Next.js Specific Benchmarks

### App Router (Next.js 13+) — Preferred
```typescript
// ✅ Server Component — data fetching at the server level
// app/orders/page.tsx
async function OrdersPage() {
    const orders = await fetchOrders(); // No useEffect, no loading state
    return <OrderList orders={orders} />;
}

// ✅ Client Component — only where interactivity is needed
'use client';
function OrderFilter() {
    const [filter, setFilter] = useState('all');
    // ...
}
```

### Pages Router (Legacy) Anti-Patterns
```typescript
// ❌ getServerSideProps for data that doesn't change per-request
export async function getServerSideProps() {
    const categories = await fetchCategories(); // Never changes — use getStaticProps
    return { props: { categories } };
}

// ✅ Use getStaticProps for static or infrequently changing data
export async function getStaticProps() {
    const categories = await fetchCategories();
    return { props: { categories }, revalidate: 3600 }; // ISR
}
```

---

## Data Fetching Pattern Matrix

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| React Query `useQuery` | Client-rendered, user-specific data | SSR pages with SEO requirements |
| React Query `useMutation` | POST/PUT/DELETE from client | Server Actions (Next.js App Router) |
| Next.js Server Components | SEO pages, public data | Highly interactive, real-time UI |
| Next.js Server Actions | Form submissions, mutations | Complex client-side optimistic UI |
| SWR | Simple fetch-and-cache | Complex query invalidation chains |

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **God Component** | >200 lines, fetches + displays + handles form | Untestable, unmaintainable |
| **Server State in Redux** | API data in Redux slices | Cache staleness, sync complexity |
| **Prop Drilling >3 levels** | Same prop passed through 4+ components | Fragile, refactoring-resistant |
| **Context for hot state** | Shopping cart qty in Context | Full tree re-render on every add |
| **No Error Boundary** | Async errors crash entire app | White screen in production |
| **No Code Splitting** | All routes in one bundle | Large initial load time |
| **useEffect for server data** | `useEffect(() => fetch('/api/...'))` | Race conditions, no cache, no retry |
