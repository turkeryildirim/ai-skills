---
title: Ship structured JSON logs with correlation and trace IDs
impact: HIGH
tags: [observability, logging]
---

# obs-structured-logging

Text logs are ungreppable once you have 10 services. JSON logs with consistent fields (`service`, `level`, `correlation_id`, `trace_id`) make aggregation, filtering, and alerting trivial.

## Bad — PHP

```php
error_log("[".date('c')."] user $email logged in from $ip");
// ungreppable; leaks email into free text; no correlation
```

## Bad — TypeScript

```ts
console.log(`[${new Date().toISOString()}] user ${email} logged in from ${ip}`);
```

## Good — PHP (Monolog JSON formatter)

```php
// config/logging.php
'stack' => [
    'driver' => 'stack',
    'channels' => ['stdout'],
    'processors' => [CorrelationIdProcessor::class, TraceContextProcessor::class],
    'formatter' => JsonFormatter::class,
],

$log->info('user logged in', [
    'user_id' => $user->id,   // stable ID, not PII
    'ip'      => $ip,
]);
// → {"ts":"...","level":"info","service":"auth","correlation_id":"req_abc","trace_id":"...","msg":"user logged in","user_id":42,"ip":"1.2.3.4"}
```

## Good — TypeScript (pino)

```ts
const logger = pino({
  base: { service: 'auth', env: process.env.APP_ENV },
  formatters: { level: (l) => ({ level: l }) },
  mixin: () => ({
    correlation_id: store()?.correlationId,
    trace_id: trace.getActiveSpan()?.spanContext().traceId,
  }),
  redact: ['password', 'token', 'authorization', '*.secret'],
});

logger.info({ user_id: user.id, ip }, 'user logged in');
```

Redaction lives in the logger config — developers can't forget it at call sites. Never log: passwords, tokens, full request bodies, full card numbers.
