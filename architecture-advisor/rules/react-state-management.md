---
title: React State Management Pattern Analysis
impact: HIGH
impactDescription: "Wrong state management solution creates either over-engineering or performance problems"
tags: react, state-management, context, zustand, redux, jotai, server-state
---

## React State Management Pattern Analysis

**Impact: HIGH (Wrong state management solution creates either over-engineering or performance problems)**

State management is where many React projects make costly architectural mistakes. Using Redux for a small app adds unnecessary complexity. Using `useState` for global state creates prop drilling. Using Context for high-frequency updates causes whole-tree re-renders. Using a client store for server data creates synchronization bugs.

## The State Classification Framework

```
State Type              │ Right Tool
──────────────────────────────────────────────────────
Server/async state      │ React Query, SWR, tRPC
(fetched data)          │ (NOT Redux, NOT useState+useEffect)
──────────────────────────────────────────────────────
Global UI state         │ Zustand, Jotai, Context (low-freq)
(auth, theme, cart)     │
──────────────────────────────────────────────────────
Local UI state          │ useState, useReducer
(form, modal, toggle)   │
──────────────────────────────────────────────────────
URL state               │ URL search params, router state
(filters, page, tab)    │
──────────────────────────────────────────────────────
Form state              │ React Hook Form, Formik
                        │ (NOT useState for each field)
```

## Incorrect

```tsx
// ❌ Server state managed with useState + useEffect (common anti-pattern)

function ProductList() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // ❌ Manual cache management, no deduplication, no background refresh,
    // re-fetches on every mount, no stale-while-revalidate
    useEffect(() => {
        setLoading(true);
        fetch('/api/products')
            .then(r => r.json())
            .then(data => { setProducts(data); setLoading(false); })
            .catch(err => { setError(err); setLoading(false); });
    }, []);
}
```

```tsx
// ❌ Context used for frequently changing state (causes full re-render tree)

const CartContext = createContext(null);

export function CartProvider({ children }) {
    // ❌ Every Context value change re-renders ALL consumers
    const [items, setItems] = useState([]);
    const [total, setTotal] = useState(0);  // changes on every item add/remove

    return (
        <CartContext.Provider value={{ items, setItems, total, setTotal }}>
            {children}
        </CartContext.Provider>
    );
}
// Entire app re-renders on every cart change
```

```tsx
// ❌ Redux Toolkit for a 5-page app with minimal global state
// 8 slice files, 3 middleware configs, complex selector memoization
// for state that could be 2 Zustand stores
```

## Correct

```tsx
// ✅ Server state with React Query — caching, background refetch, dedup
function ProductList() {
    const { data: products, isLoading, error } = useQuery({
        queryKey: ['products'],
        queryFn: () => fetch('/api/products').then(r => r.json()),
        staleTime: 1000 * 60 * 5, // 5 min cache
    });

    if (isLoading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return <ProductGrid products={products} />;
}
```

```tsx
// ✅ Zustand for global client state (cart, auth, theme)
const useCartStore = create<CartStore>((set, get) => ({
    items: [],
    addItem: (product) => set(state => ({
        items: [...state.items, product],
    })),
    total: () => get().items.reduce((sum, item) => sum + item.price, 0),
}));

// Only components that call useCartStore re-render — no Context tree thrash
```

```tsx
// ✅ URL state for filters and pagination (survives refresh, shareable)
function ProductList() {
    const [searchParams, setSearchParams] = useSearchParams();
    const page = Number(searchParams.get('page') ?? 1);
    const category = searchParams.get('category') ?? 'all';
    // Filters reflected in URL — browser back works, links are shareable
}
```

## State Management Assessment Questions

```
1. Is server data (fetched from API) stored in useState/Redux?
   → HIGH issue: use React Query or SWR

2. Is Context updating more than once per second?
   → HIGH issue: use Zustand or split Context into smaller pieces

3. Is the same data fetched in multiple components independently?
   → MEDIUM issue: centralize in React Query with shared queryKey

4. Are filters/pagination stored in component state (lost on refresh)?
   → MEDIUM issue: move to URL search params

5. Is Redux/Zustand used for purely local UI state (modal open/close)?
   → MEDIUM issue: use useState — don't overshoot the solution

6. Are there >5 separate useEffect data fetches in one component?
   → HIGH issue: extract to custom hook + consider React Query
```

## Why

- **Cache correctness**: React Query handles stale data, background refresh, and deduplication — `useState+useEffect` does none of this
- **Performance**: Zustand updates only subscribed components; Context updates all consumers
- **URL state**: Filters and pagination in URL survive page refresh and are bookmarkable/shareable
- **Right tool sizing**: Redux for a 5-page app adds weeks of boilerplate for no architectural benefit
