---
title: Redis Caching with Invalidation
impact: MEDIUM
impactDescription: Skipping caching or failing to invalidate stale data wastes database resources and serves outdated information.
tags: caching, redis, performance, express
---

# Redis Caching with Invalidation

Use a CacheService with get/set/delete/pattern invalidation and a `@Cacheable` decorator so that expensive queries are cached and correctly invalidated.

## Bad Example

```typescript
// No caching — every request hits the database
export class ProductService {
  async getProduct(id: string) {
    const result = await pool.query("SELECT * FROM products WHERE id = $1", [id]);
    return result.rows[0];
  }

  async getProductsByCategory(category: string) {
    const result = await pool.query(
      "SELECT * FROM products WHERE category = $1",
      [category],
    );
    return result.rows;
  }

  async updateProduct(id: string, data: UpdateProductDTO) {
    await pool.query("UPDATE products SET name = $1 WHERE id = $2", [data.name, id]);
    // Stale cached data — no invalidation happens
  }
}
```

## Good Example

```typescript
// utils/cache.ts — reusable caching layer
export class CacheService {
  private redis = new Redis({ host: process.env.REDIS_HOST, port: 6379 });

  async get<T>(key: string): Promise<T | null> {
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : null;
  }

  async set(key: string, value: any, ttl: number = 300): Promise<void> {
    await this.redis.setex(key, ttl, JSON.stringify(value));
  }

  async delete(key: string): Promise<void> {
    await this.redis.del(key);
  }

  async invalidatePattern(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) await this.redis.del(...keys);
  }
}

// Decorator for cache-through methods
export function Cacheable(ttl: number = 300) {
  return function (target: any, key: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = async function (...args: any[]) {
      const cache = new CacheService();
      const cacheKey = `${key}:${JSON.stringify(args)}`;
      const cached = await cache.get(cacheKey);
      if (cached) return cached;

      const result = await original.apply(this, args);
      await cache.set(cacheKey, result, ttl);
      return result;
    };
    return descriptor;
  };
}

// Usage — reads are cached, writes invalidate related keys
export class ProductService {
  constructor(private cache: CacheService) {}

  @Cacheable(300)
  async getProduct(id: string) {
    return this.productRepo.findById(id);
  }

  async updateProduct(id: string, data: UpdateProductDTO) {
    const product = await this.productRepo.update(id, data);
    await this.cache.delete(`getProduct:${JSON.stringify([id])}`);
    await this.cache.invalidatePattern(`getProductsByCategory:*`);
    return product;
  }
}
```

## Why

- **Benefit**: Expensive queries execute once per TTL window, dramatically reducing database load for read-heavy endpoints.
- **Benefit**: Pattern-based invalidation (`products:category:*`) clears all related cache entries when data changes, preventing stale responses.
- **Benefit**: The `@Cacheable` decorator separates caching concerns from business logic -- adding or removing caching is a one-line annotation change.
