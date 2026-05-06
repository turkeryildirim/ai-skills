---
title: React Component Design and Hierarchy Analysis
impact: HIGH
impactDescription: "Oversized components with mixed concerns become impossible to test and reuse"
tags: react, components, decomposition, props-drilling, code-splitting
---

## React Component Design and Hierarchy Analysis

**Impact: HIGH (Oversized components with mixed concerns become impossible to test and reuse)**

React components should follow the Single Responsibility Principle: one component, one job. When a component fetches data, handles business logic, manages form state, and renders complex UI simultaneously, it cannot be reused, tested in isolation, or understood quickly.

## Incorrect

```tsx
// ❌ God component — does everything in one place (350+ lines)

export function OrderDashboard() {
    // ❌ Data fetching mixed with UI
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/orders')
            .then(r => r.json())
            .then(data => { setOrders(data); setLoading(false); });
    }, []);

    // ❌ Business logic inside component
    const calculateTotal = (items) =>
        items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    // ❌ Form state mixed with display state
    const [newOrderForm, setNewOrderForm] = useState({ items: [], note: '' });
    const [filterTerm, setFilterTerm] = useState('');
    const [sortOrder, setSortOrder] = useState('asc');
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);

    // 200 lines of JSX with inline styles, conditional rendering,
    // table, modal, form, and pagination all in one return statement
}
```

```tsx
// ❌ Props drilling — 4 levels deep
<App>                               // owns: currentUser
  <Layout user={currentUser}>       // passes: currentUser
    <Sidebar user={currentUser}>    // passes: currentUser
      <UserAvatar user={currentUser} /> // finally uses it
    </Sidebar>
  </Layout>
</App>
```

## Correct

```tsx
// ✅ Decomposed components with single responsibilities

// 1. Data fetching hook — separated from UI
function useOrders() {
    return useQuery({
        queryKey: ['orders'],
        queryFn: () => fetch('/api/orders').then(r => r.json()),
    });
}

// 2. Pure display component — no data fetching, no state
function OrderRow({ order }: { order: Order }) {
    return (
        <tr>
            <td>{order.id}</td>
            <td>{formatCurrency(order.total)}</td>
            <td><OrderStatusBadge status={order.status} /></td>
        </tr>
    );
}

// 3. Container component — coordinates data + child components
export function OrderDashboard() {
    const { data: orders, isLoading } = useOrders();

    if (isLoading) return <LoadingSpinner />;

    return (
        <div>
            <OrderFilters />
            <OrderTable orders={orders} />
            <OrderPagination />
        </div>
    );
}

// 4. Props drilling avoided with Context for global state
const UserContext = createContext<User | null>(null);

export function useCurrentUser() {
    return useContext(UserContext);
}

// UserAvatar consumes directly — no prop threading
function UserAvatar() {
    const user = useCurrentUser();
    return <img src={user?.avatar} alt={user?.name} />;
}
```

## Component Quality Signals to Detect

```
✅ Healthy signals:
- Components under 100 lines (200 max for complex ones with justification)
- Custom hooks extract data fetching and business logic
- Props count: 3-5 props per component (more = decompose)
- Route-level code splitting: React.lazy() for page components
- Loading, error, empty states handled separately

❌ Problem signals:
- useState count > 5 in one component (god state)
- useEffect with multiple dependencies fetching different data
- JSX return statement > 80 lines
- Props passed more than 3 component levels deep without Context
- No route-based code splitting (one massive bundle)
- Mixing framework routing styles (Next.js pages/ and app/ mixed)
```

## Props Drilling Depth Assessment

```
1 level:  FINE     — Parent → Child
2 levels: FINE     — Parent → Child → Grandchild
3 levels: WATCH    — Consider Context if it grows
4+ levels: FLAG    → HIGH issue: use Context or state manager
```

## Why

- **Testability**: Small, focused components are tested with simple prop inputs — god components require complex environment setup
- **Reusability**: A component that only renders cannot be broken by data fetching changes
- **Bundle size**: Route-level `React.lazy()` splits the bundle and reduces initial load
- **Readability**: 100-line components can be understood in 2 minutes; 350-line components require 20 minutes
