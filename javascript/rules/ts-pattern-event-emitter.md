---
title: Type-Safe Event Emitter Over Stringly-Typed Events
impact: HIGH
impactDescription: EventEmitter with string events and any payloads allows typos and mismatched listeners without compile errors.
tags: typescript, event-emitter, mapped-types, pattern
---

# Type-Safe Event Emitter Over Stringly-Typed Events

A generic `TypedEventEmitter` uses mapped types to tie each event name to its payload shape, catching typos and payload mismatches at compile time.

## Bad Example

```typescript
// No connection between event name and payload type
class EventEmitter {
  private listeners: Record<string, Function[]> = {};

  on(event: string, callback: (data: any) => void): void {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }

  emit(event: string, data: any): void {
    this.listeners[event]?.forEach((cb) => cb(data));
  }
}

const emitter = new EventEmitter();

// Typo in event name - no error, silently fails
emitter.on("user:createdd", (data) => {
  console.log(data.namme); // no error, data is any
});

// Wrong payload shape - no error
emitter.emit("user:created", { wrong: "field" });
```

## Good Example

```typescript
// Event map defines the contract between event names and payloads
type EventMap = {
  "user:created": { id: string; name: string };
  "user:updated": { id: string };
  "user:deleted": { id: string };
};

class TypedEventEmitter<T extends Record<string, any>> {
  private listeners: {
    [K in keyof T]?: Array<(data: T[K]) => void>;
  } = {};

  on<K extends keyof T>(event: K, callback: (data: T[K]) => void): void {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event]!.push(callback);
  }

  emit<K extends keyof T>(event: K, data: T[K]): void {
    this.listeners[event]?.forEach((cb) => cb(data));
  }
}

const emitter = new TypedEventEmitter<EventMap>();

// Callback parameter is typed based on the event name
emitter.on("user:created", (data) => {
  console.log(data.id, data.name); // data: { id: string; name: string }
});

// Payload must match the event's shape
emitter.emit("user:created", { id: "1", name: "John" });
// emitter.emit("user:created", { id: "1" }); // Error: missing 'name'
// emitter.emit("user:unknown", {});           // Error: not in EventMap
```

## Why

- **No typos**: Event names are constrained to keys of the event map; misspelled events are compile errors.
- **Payload safety**: Each event carries its exact payload type, so callbacks and emits must match.
- **Refactoring**: Renaming an event or changing a payload type causes errors at every usage site.
- **Scalability**: Adding a new event is a single entry in the map; the class handles the rest.
