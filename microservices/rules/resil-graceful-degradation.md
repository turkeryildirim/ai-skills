---
title: Serve a reduced feature set when a dependency is down
impact: CRITICAL
tags: [resilience, fallback]
---

# resil-graceful-degradation

A product page without personalised recommendations is better than no product page. When a non-critical dependency fails, serve cached or default data; only surface a hard error for genuinely essential dependencies (auth, payment-at-checkout).

## Bad — PHP

```php
public function show(string $sku): View {
    return view('product', [
        'product' => $this->catalog->get($sku),
        'recs'    => $this->recommender->for($sku),  // throws → whole page 500s
        'reviews' => $this->reviews->for($sku),      // throws → whole page 500s
    ]);
}
```

## Bad — TypeScript

```ts
@Get(':sku')
async show(@Param('sku') sku: string) {
  return {
    product: await this.catalog.get(sku),
    recs:    await this.recommender.for(sku),  // one failure tanks the page
    reviews: await this.reviews.for(sku),
  };
}
```

## Good — PHP

```php
public function show(string $sku): View {
    $product = $this->catalog->get($sku);  // core — must succeed
    $recs    = $this->safe(fn() => $this->recommender->for($sku), fallback: []);
    $reviews = $this->safe(fn() => $this->reviews->for($sku),     fallback: ['items' => [], 'degraded' => true]);
    return view('product', compact('product', 'recs', 'reviews'));
}

private function safe(callable $fn, mixed $fallback): mixed {
    try { return $fn(); }
    catch (\Throwable $e) {
        $this->logger->warning('degraded', ['err' => $e->getMessage()]);
        $this->metrics->increment('degraded_fallback');
        return $fallback;
    }
}
```

## Good — TypeScript

```ts
@Get(':sku')
async show(@Param('sku') sku: string) {
  const product = await this.catalog.get(sku);
  const [recs, reviews] = await Promise.all([
    this.safe(() => this.recommender.for(sku), []),
    this.safe(() => this.reviews.for(sku), { items: [], degraded: true }),
  ]);
  return { product, recs, reviews };
}

private async safe<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try { return await fn(); }
  catch (e) {
    this.logger.warn({ err: e }, 'degraded');
    this.metrics.inc('degraded_fallback');
    return fallback;
  }
}
```

Log + meter every degradation so you see when you're serving reduced experiences — silent fallbacks become silent outages.
