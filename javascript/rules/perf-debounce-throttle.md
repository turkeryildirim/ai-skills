---
title: Debounce and Throttle High-Frequency Event Handlers
impact: MEDIUM
impactDescription: Unthrottled events fire dozens of times per second, wasting CPU and flooding APIs
tags: performance, debounce, throttle, events, generators
---

# Debounce and Throttle High-Frequency Event Handlers

Use debounce for actions that should wait until input settles (search, resize). Use throttle for actions that should run at a capped rate (scroll, mousemove). Consider lazy generator evaluation for expensive data pipelines.

## Bad Example

```javascript
// Fires an API call on every single keystroke
searchInput.addEventListener("input", (e) => {
  fetch(`/api/search?q=${e.target.value}`);
  // Typing "hello" sends 5 requests: "h", "he", "hel", "hell", "hello"
});

// Recalculates layout on every scroll frame
window.addEventListener("scroll", () => {
  recalculateLayout(); // runs 60+ times per second while scrolling
});

// Expensive operation runs on every resize event
window.addEventListener("resize", () => {
  const data = generateReport(); // heavy computation every pixel change
  updateDashboard(data);
});
```

## Good Example

```javascript
// Debounce — wait until input settles, then fire once
function debounce(fn, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

// Search fires only after user stops typing for 300ms
searchInput.addEventListener(
  "input",
  debounce((e) => {
    fetch(`/api/search?q=${e.target.value}`);
  }, 300)
);

// Throttle — run at most once per interval, never skip the last call
function throttle(fn, limit) {
  let inThrottle;
  let lastArgs;
  return (...args) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
        if (lastArgs) {
          fn(...lastArgs);
          lastArgs = null;
        }
      }, limit);
    } else {
      lastArgs = args;
    }
  };
}

// Scroll handler runs at most once every 100ms
window.addEventListener(
  "scroll",
  throttle(() => {
    recalculateLayout();
  }, 100)
);

// Debounced resize — fires once after user stops resizing
window.addEventListener(
  "resize",
  debounce(() => {
    const data = generateReport();
    updateDashboard(data);
  }, 250)
);

// Lazy generator evaluation — compute only what is consumed
function* lazyMap(iterable, transform) {
  for (const item of iterable) {
    yield transform(item);
  }
}

const results = lazyMap(hugeArray, expensiveTransform);
const first10 = [...results].slice(0, 10); // only 10 transforms run
```

## Why

- **Reduced API load**: Debounce batches rapid input into a single request, preventing unnecessary server calls during typing.
- **Smooth performance**: Throttle caps execution rate so expensive handlers do not block the main thread during high-frequency events like scroll and resize.
- **Efficiency**: Lazy generator evaluation computes values only when consumed, avoiding wasted work on data that is never used.
