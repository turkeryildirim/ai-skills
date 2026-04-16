---
title: Use Modern ES6+ Syntax for Concise, Expressive Code
impact: MEDIUM
impactDescription: Verbose property access, string concatenation, and manual copies make code harder to read and maintain
tags: es6, destructuring, spread, template-literals, arrow-functions
---

# Use Modern ES6+ Syntax for Concise, Expressive Code

Leverage destructuring, spread/rest, template literals, arrow functions, shorthand properties, and private fields to write cleaner JavaScript.

## Bad Example

```javascript
// Verbose property access and variable assignment
const name = user.name;
const email = user.email;
const age = user.age;

// String concatenation
const greeting = "Hello, " + name + "! You are " + age + " years old.";

// Manual object copy and merge
const settings = Object.assign({}, defaults, userPrefs);

// Function expression with 'this' binding issues
class Counter {
  constructor() {
    this.count = 0;
  }
  increment() {
    setTimeout(function () {
      this.count++; // 'this' is wrong here
    }, 1000);
  }
}

// No encapsulation — password is public
class User {
  constructor(name, password) {
    this.name = name;
    this.password = password; // accessible as user.password
  }
}
```

## Good Example

```javascript
// Destructuring with defaults and rest
const { name, email, age = 25, ...rest } = user;

// Nested destructuring
const { address: { city, country } } = user;

// Template literals with embedded expressions
const greeting = `Hello, ${name}! You are ${age} years old.`;
const total = `Total: $${(price * 1.2).toFixed(2)}`;

// Spread for immutable updates and merges (later overrides earlier)
const settings = { ...defaults, ...userPrefs };
const updated = { ...user, age: 31 };

// Arrow functions with lexical 'this'
class Counter {
  #count = 0;                          // Private field
  increment = () => { this.#count++; }; // Arrow preserves 'this'

  delayedIncrement() {
    setTimeout(() => {
      this.#count++; // 'this' correctly refers to Counter instance
    }, 1000);
  }
}

// Private fields for encapsulation
class User {
  #password; // truly private — not accessible outside the class

  constructor(name, password) {
    this.name = name;
    this.#password = password;
  }

  #hashPassword(pwd) {
    return `hashed_${pwd}`;
  }

  get displayName() {
    return this.name.toUpperCase();
  }
}

// Array destructuring with rest
const [head, ...tail] = numbers;
```

## Why

- **Conciseness**: Destructuring, spread, and shorthand properties reduce boilerplate and make the intent clear at a glance.
- **Safety**: Arrow functions inherit `this` from the enclosing scope, eliminating the most common `this`-binding bug. Private fields (`#`) prevent external access to internal state.
- **Expressiveness**: Template literals embed expressions directly in strings, and spread enables immutable object/array updates without `Object.assign` or manual copying.
