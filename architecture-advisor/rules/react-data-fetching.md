---
title: React Data Fetching Pattern Analysis
impact: HIGH
impactDescription: "Waterfall fetches and missing error boundaries cause poor UX and hard-to-debug failures"
tags: react, data-fetching, react-query, suspense, error-boundaries, waterfall
---

## React Data Fetching Pattern Analysis

**Impact: HIGH (Waterfall fetches and missing error boundaries cause poor UX and hard-to-debug failures)**

Data fetching is where React architecture most often breaks down. Waterfall requests (each fetch waits for the previous), absent error boundaries, unhandled loading states, and duplicated fetch logic are the most common performance and reliability issues in React projects.

## Incorrect

```tsx
// ❌ Waterfall fetching — each request waits for the previous

function OrderDetail({ orderId }: { orderId: string }) {
    const [order, setOrder] = useState(null);
    const [customer, setCustomer] = useState(null);
    const [products, setProducts] = useState([]);

    useEffect(() => {
        // ❌ Sequential fetches — total time = t1 + t2 + t3
        fetch(`/api/orders/${orderId}`)
            .then(r => r.json())
            .then(order => {
                setOrder(order);
                // ❌ Only starts after order loads
                return fetch(`/api/customers/${order.customerId}`);
            })
            .then(r => r.json())
            .then(customer => {
                setCustomer(customer);
                // ❌ Only starts after customer loads
                return fetch(`/api/products?orderId=${orderId}`);
            })
            .then(r => r.json())
            .then(setProducts);
    }, [orderId]);
}
```

```tsx
// ❌ No error boundaries — uncaught async errors crash the entire app

function App() {
    return (
        // ❌ If any child throws during data fetching, entire UI breaks
        <Router>
            <ProductList />      // throws? → white screen
            <OrderDashboard />   // throws? → white screen
        </Router>
    );
}
```

```tsx
// ❌ Duplicate fetch logic — same endpoint fetched in 5 components

// ProductList.tsx
useEffect(() => { fetch('/api/products').then(setProducts) }, []);

// ProductSearch.tsx
useEffect(() => { fetch('/api/products').then(setProducts) }, []);

// ProductPicker.tsx
useEffect(() => { fetch('/api/products').then(setProducts) }, []);
// → 3 network requests for identical data
```

## Correct

```tsx
// ✅ Parallel fetching with React Query — all requests start simultaneously

function OrderDetail({ orderId }: { orderId: string }) {
    // ✅ All three queries fire in parallel — total time = max(t1, t2, t3)
    const { data: order } = useQuery({
        queryKey: ['order', orderId],
        queryFn: () => fetchOrder(orderId),
    });

    const { data: customer } = useQuery({
        queryKey: ['customer', order?.customerId],
        queryFn: () => fetchCustomer(order!.customerId),
        enabled: !!order?.customerId, // only runs when customerId is known
    });

    const { data: products } = useQuery({
        queryKey: ['order-products', orderId],
        queryFn: () => fetchOrderProducts(orderId),
    });
}
```

```tsx
// ✅ Error boundaries at route and section level

function App() {
    return (
        <Router>
            <ErrorBoundary fallback={<PageError />}>
                <Suspense fallback={<PageLoader />}>
                    <Routes>
                        <Route path="/products" element={
                            <ErrorBoundary fallback={<SectionError />}>
                                <ProductList />
                            </ErrorBoundary>
                        } />
                    </Routes>
                </Suspense>
            </ErrorBoundary>
        </Router>
    );
}
```

```tsx
// ✅ Shared query key = automatic deduplication

// React Query deduplicates: all three components use the same cache entry
// queryKey: ['products'] — fetched once, shared across all consumers

function useProducts() {
    return useQuery({
        queryKey: ['products'],
        queryFn: () => fetch('/api/products').then(r => r.json()),
    });
}

// Now ProductList, ProductSearch, ProductPicker all use useProducts()
// → 1 network request total, shared cache
```

## Data Fetching Assessment Checklist

```
Waterfall Analysis:
[ ] Are fetch calls inside useEffect chained (one starts after another completes)?
[ ] Are Promise.all() or parallel useQuery calls used where independent data is needed?
[ ] Are dependent queries using the `enabled` option (not nested useEffects)?

Error Handling:
[ ] Is there at least one <ErrorBoundary> at the route level?
[ ] Are async errors surfaced with user-friendly messages (not just console.error)?
[ ] Are 4xx/5xx API errors handled separately from network errors?

Loading States:
[ ] Are loading states shown at appropriate granularity (skeleton > spinner > nothing)?
[ ] Are empty states handled (no data ≠ loading)?

Deduplication:
[ ] Is the same API endpoint fetched independently in multiple components?
[ ] If yes: are shared query keys or a shared hook used to deduplicate?

Next.js Specific:
[ ] Are Server Components used for initial data load where applicable?
[ ] Is getServerSideProps avoided in favor of App Router fetch + React Server Components?
```

## Why

- **Performance**: Sequential waterfall of 3×200ms requests takes 600ms; parallel takes 200ms
- **Reliability**: Without `<ErrorBoundary>`, a single fetch failure crashes the entire React tree
- **Network efficiency**: Deduplicated queries reduce server load and improve cache hit rates
- **UX quality**: Proper loading and empty states prevent "blank screen" experiences
