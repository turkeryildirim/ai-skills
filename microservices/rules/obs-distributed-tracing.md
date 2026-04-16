---
title: OpenTelemetry spans across services, brokers, and DBs
impact: HIGH
tags: [observability, tracing]
---

# obs-distributed-tracing

Spans tell you **where** time went. A trace = tree of spans, joined by trace/span IDs propagated via W3C Trace Context headers. Auto-instrumentation covers most of it; add manual spans around critical business operations.

## Bad — PHP

```php
// No tracing. Latency debugging = 5 people in a war room with grep.
public function placeOrder(Request $r) {
    $order = $this->orders->create($r->all());
    return response()->json($order);
}
```

## Bad — TypeScript

```ts
async place(dto: PlaceOrderDto) {
  return this.orders.create(dto);
}
```

## Good — PHP (OpenTelemetry PHP SDK)

```php
$tracer = Globals::tracerProvider()->getTracer('orders-service');

public function placeOrder(Request $r) {
    $span = $tracer->spanBuilder('PlaceOrder')->startSpan();
    $scope = $span->activate();
    try {
        $span->setAttribute('customer.id', $r->input('customer_id'));
        $order = $this->orders->create($r->all());
        $span->setAttribute('order.id', $order->id);
        return response()->json($order);
    } catch (\Throwable $e) {
        $span->recordException($e);
        $span->setStatus(StatusCode::STATUS_ERROR);
        throw $e;
    } finally {
        $scope->detach();
        $span->end();
    }
}
```

## Good — TypeScript (@opentelemetry/sdk-node)

```ts
const tracer = trace.getTracer('orders-service');

async place(dto: PlaceOrderDto) {
  return tracer.startActiveSpan('PlaceOrder', async (span) => {
    span.setAttribute('customer.id', dto.customerId);
    try {
      const order = await this.orders.create(dto);
      span.setAttribute('order.id', order.id);
      return order;
    } catch (err) {
      span.recordException(err as Error);
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw err;
    } finally {
      span.end();
    }
  });
}
```

Export via OTLP to a collector → Jaeger/Tempo/Honeycomb. Attach `correlation_id` as a span attribute so pivots work both directions.
