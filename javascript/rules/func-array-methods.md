---
title: Use Array Methods Instead of Manual Loops
impact: HIGH
impactDescription: Manual loops with push/index produce harder-to-read, bug-prone code vs declarative array methods
tags: functional, arrays, map, filter, reduce, chaining
---

# Use Array Methods Instead of Manual Loops

Prefer `map`, `filter`, `reduce`, `find`, `some`, `every`, and `flatMap` over imperative `for` loops with manual accumulation. Chain methods for data transformations.

## Bad Example

```javascript
const users = [
  { id: 1, name: "John", age: 30, active: true },
  { id: 2, name: "Jane", age: 25, active: false },
  { id: 3, name: "Bob", age: 35, active: true },
];

// Manual loop to get active user names
const names = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].active) {
    names.push(users[i].name);
  }
}

// Manual loop to compute total age
let totalAge = 0;
for (let i = 0; i < users.length; i++) {
  totalAge += users[i].age;
}

// Manual loop to find a user
let found = null;
for (let i = 0; i < users.length; i++) {
  if (users[i].id === 2) {
    found = users[i];
    break;
  }
}

// Manual loop to check if any are active
let anyActive = false;
for (let i = 0; i < users.length; i++) {
  if (users[i].active) {
    anyActive = true;
    break;
  }
}
```

## Good Example

```javascript
const users = [
  { id: 1, name: "John", age: 30, active: true },
  { id: 2, name: "Jane", age: 25, active: false },
  { id: 3, name: "Bob", age: 35, active: true },
];

// filter + map for transform and select
const names = users.filter(u => u.active).map(u => u.name);

// reduce for aggregation
const totalAge = users.reduce((sum, u) => sum + u.age, 0);

// find for first match
const found = users.find(u => u.id === 2);

// some for "any" check
const anyActive = users.some(u => u.active);

// every for "all" check
const allAdults = users.every(u => u.age >= 18);

// flatMap to map and flatten in one step
const allTags = userTags.flatMap(u => u.tags);

// Method chaining for multi-step transforms
const sortedActiveNames = users
  .filter(u => u.active)
  .map(u => u.name)
  .sort()
  .join(", ");

// Group by with reduce
const byActive = users.reduce((groups, user) => {
  const key = user.active ? "active" : "inactive";
  return { ...groups, [key]: [...(groups[key] || []), user] };
}, {});
```

## Why

- **Readability**: Declarative methods express intent directly — `filter` selects, `map` transforms, `reduce` aggregates — no need to parse loop mechanics.
- **Chaining**: Methods return arrays, enabling fluent pipelines that replace nested loops with a linear sequence of steps.
- **Safety**: No off-by-one errors, no accidental mutation of loop variables, and built-in handling of empty arrays.
