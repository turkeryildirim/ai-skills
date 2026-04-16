---
title: Write Pure Functions and Preserve Immutability
impact: HIGH
impactDescription: Mutating inputs causes hidden bugs across shared references and makes code hard to test
tags: functional, immutability, pure-functions, spread, structuredClone
---

# Write Pure Functions and Preserve Immutability

Never mutate input arrays or objects. Return new copies instead. Use spread for shallow updates and `structuredClone` for deep copies.

## Bad Example

```javascript
// Mutates the input array — callers see their data changed
function addItem(cart, item) {
  cart.items.push(item);
  cart.total += item.price;
  return cart;
}

// Mutates the input object
function updateAge(user, newAge) {
  user.age = newAge;
  return user;
}

// Removes a property by mutating
function removePassword(user) {
  delete user.password;
  return user;
}

// Side effect: modifies external state
let totalCount = 0;
function processOrder(order) {
  totalCount += order.amount;
  return order;
}
```

## Good Example

```javascript
// Pure function — returns a new object, input untouched
function addItem(cart, item) {
  return {
    ...cart,
    items: [...cart.items, item],
    total: cart.total + item.price,
  };
}

// Immutable update with spread
function updateAge(user, newAge) {
  return { ...user, age: newAge };
}

// Remove a property with rest destructuring (no mutation)
function removePassword(user) {
  const { password, ...safeUser } = user;
  return safeUser;
}

// Immutable array operations
const added = [...numbers, 6];                        // Add item
const removed = numbers.filter(n => n !== 3);         // Remove item
const updated = numbers.map(n => n === 3 ? 99 : n);   // Update item

// Deep copy for nested structures
const deepCopy = globalThis.structuredClone(nestedObject);

// Pure function: same input always gives same output, no side effects
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

## Why

- **Predictability**: Pure functions with no side effects always produce the same output for the same input, eliminating hidden state dependencies.
- **Safety**: Immutable updates prevent bugs where shared references are accidentally modified elsewhere in the codebase.
- **Testability**: Pure functions are trivial to unit test — call with input, assert on output, no mocking or setup required.
