---
title: API Rate Limiting
impact: MEDIUM
impactDescription: Without rate limiting, endpoints are vulnerable to brute-force and denial-of-service attacks.
tags: rate-limit, security, redis, express
---

# API Rate Limiting

Apply rate limiting with a Redis-backed store and use stricter limits for authentication endpoints than for general API traffic.

## Bad Example

```typescript
// No rate limiting — every endpoint is unprotected
import express from "express";

const app = express();

app.post("/auth/login", async (req, res) => {
  // Attackers can try unlimited passwords
  const user = await authService.login(req.body.email, req.body.password);
  res.json(user);
});

app.get("/api/products", async (req, res) => {
  // Scrapers can hit this indefinitely
  const products = await productService.listAll();
  res.json(products);
});
```

## Good Example

```typescript
// middleware/rate-limit.middleware.ts
import rateLimit from "express-rate-limit";
import RedisStore from "rate-limit-redis";
import Redis from "ioredis";

const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: parseInt(process.env.REDIS_PORT || "6379"),
});

// General API: 100 requests per 15 minutes
export const apiLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: "rl:" }),
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: "Too many requests from this IP, please try again later",
  standardHeaders: true,
  legacyHeaders: false,
});

// Auth endpoints: 5 failed attempts per 15 minutes
export const authLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: "rl:auth:" }),
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
});

// app.ts
app.use("/api/", apiLimiter);
app.post("/auth/login", authLimiter, authController.login);
```

## Why

- **Benefit**: Redis-backed stores share counters across multiple server instances, keeping limits consistent in distributed deployments.
- **Benefit**: Stricter auth limits (5 failed attempts) protect against credential stuffing while general limits (100/15 min) prevent abuse without hurting normal usage.
- **Benefit**: `standardHeaders: true` returns `RateLimit-*` headers so well-behaved clients can self-throttle, reducing unnecessary 429 responses.
