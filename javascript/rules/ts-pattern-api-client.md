---
title: Type-Safe API Client Over Untyped Fetch
impact: HIGH
impactDescription: Untyped fetch calls with loose strings allow wrong endpoints, missing params, and incorrect response types.
tags: typescript, api-client, conditional-types, infer, pattern
---

# Type-Safe API Client Over Untyped Fetch

A generic API client with an endpoint configuration type map uses conditional types and `infer` to extract params, body, and response types automatically.

## Bad Example

```typescript
// Everything is stringly typed - no compile-time checks
async function fetchAPI(endpoint: string, method: string, body?: any): Promise<any> {
  const response = await fetch(endpoint, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  return response.json();
}

// No validation of endpoint, method, params, or response shape
const users = await fetchAPI("/users", "GET");            // any
const user = await fetchAPI("/users/123", "GET");         // wrong path format, no params
await fetchAPI("/users", "POST", { name: "John" });       // missing email, no error
await fetchAPI("/unknown", "DELETE");                      // wrong endpoint, no error
```

## Good Example

```typescript
type HTTPMethod = "GET" | "POST" | "PUT" | "DELETE";

// Endpoint config maps path + method to params, body, and response
type EndpointConfig = {
  "/users": {
    GET: { response: User[] };
    POST: { body: { name: string; email: string }; response: User };
  };
  "/users/:id": {
    GET: { params: { id: string }; response: User };
    PUT: { params: { id: string }; body: Partial<User>; response: User };
    DELETE: { params: { id: string }; response: void };
  };
};

// Extract types with conditional + infer
type ExtractParams<T> = T extends { params: infer P } ? P : never;
type ExtractBody<T> = T extends { body: infer B } ? B : never;
type ExtractResponse<T> = T extends { response: infer R } ? R : never;

class APIClient<Config extends Record<string, Record<HTTPMethod, any>>> {
  async request<Path extends keyof Config, Method extends keyof Config[Path]>(
    path: Path,
    method: Method,
    ...[options]: ExtractParams<Config[Path][Method]> extends never
      ? ExtractBody<Config[Path][Method]> extends never
        ? []
        : [{ body: ExtractBody<Config[Path][Method]> }]
      : [{ params: ExtractParams<Config[Path][Method]>; body?: ExtractBody<Config[Path][Method]> }]
  ): Promise<ExtractResponse<Config[Path][Method]>> {
    return {} as any; // implementation omitted
  }
}

const api = new APIClient<EndpointConfig>();

// All calls are fully type-checked
const users = await api.request("/users", "GET");           // Type: User[]
const user = await api.request("/users/:id", "GET", {       // Type: User
  params: { id: "123" },
});
// await api.request("/unknown", "GET");                     // Error: not in EndpointConfig
// await api.request("/users/:id", "GET");                   // Error: missing params
```

## Why

- **Endpoint safety**: Only paths defined in the config are accepted; typos are compile errors.
- **Conditional parameters**: The `options` argument appears only when the endpoint requires params or body, via conditional type inference.
- **Response typing**: Return type is inferred from the config, so callers never cast manually.
- **Single source of truth**: The endpoint config serves as both documentation and compile-time contract.
