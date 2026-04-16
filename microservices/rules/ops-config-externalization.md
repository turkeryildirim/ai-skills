---
title: Config via env vars and secret manager — same image everywhere
impact: HIGH
tags: [operations, 12-factor]
---

# ops-config-externalization

The container image you tested in staging must be **bit-identical** to the one you ship to prod. The only thing that differs is config, supplied at runtime via env vars (non-secret) and a secret manager (secrets). No environment-specific branches in code.

## Bad — PHP

```php
// Environment-specific code path
if (app()->environment('production')) {
    $dsn = 'postgres://prod-db.internal/app';
    $apiKey = 'sk_live_hardcoded...';          // secret in the image!
} else {
    $dsn = 'postgres://localhost/app';
}
```

## Bad — TypeScript

```ts
const dsn = process.env.NODE_ENV === 'production'
  ? 'postgres://prod-db.internal/app'
  : 'postgres://localhost/app';
const apiKey = 'sk_live_hardcoded...';
```

## Good — PHP

```php
// config/services.php (env vars only, with explicit typing and defaults)
return [
    'database_url'      => env('DATABASE_URL'),
    'stripe_api_key'    => env('STRIPE_API_KEY'),  // injected from secret manager
    'http_timeout_ms'   => (int) env('HTTP_TIMEOUT_MS', 1000),
    'feature_new_cart'  => filter_var(env('FEATURE_NEW_CART', false), FILTER_VALIDATE_BOOL),
];

// Fail fast at boot if required config is missing
if (empty(config('services.database_url'))) {
    throw new \RuntimeException('DATABASE_URL is required');
}
```

## Good — TypeScript

```ts
// config/env.ts — validated at boot with zod
import { z } from 'zod';

const EnvSchema = z.object({
  DATABASE_URL:    z.string().url(),
  STRIPE_API_KEY:  z.string().min(1),
  HTTP_TIMEOUT_MS: z.coerce.number().int().positive().default(1000),
  FEATURE_NEW_CART: z.coerce.boolean().default(false),
});
export const env = EnvSchema.parse(process.env);  // throws at startup if invalid
```

Secrets come from a secret manager (AWS SM, GCP SM, Vault) mounted as env vars by the platform — never committed, never logged. One image, 12-factor, every env.
