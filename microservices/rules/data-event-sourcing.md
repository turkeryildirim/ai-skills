---
title: Events are the source of truth; state is a projection
impact: CRITICAL
tags: [data, event-sourcing]
---

# data-event-sourcing

Instead of storing current state, append every state-changing event. Current state is a fold over the event stream. You get a complete audit log, replayable projections, and the ability to answer "what was the state at time T?" — at the cost of operational complexity.

## Bad — PHP

```php
// State-only: history is lost forever
DB::table('accounts')->where('id', $id)->update([
    'balance_cents' => DB::raw('balance_cents - 500'),
    'updated_at' => now(),
]);
```

## Bad — TypeScript

```ts
await db.query('UPDATE accounts SET balance_cents = balance_cents - $1 WHERE id = $2', [500, id]);
```

## Good — PHP

```php
// Append-only event store
$this->eventStore->append('account-'.$id, [
    new MoneyWithdrawn($id, amountCents: 500, at: new \DateTimeImmutable(), version: $current + 1),
], expectedVersion: $current);

// Current state is built by folding events
final class Account {
    public int $balanceCents = 0;
    public int $version = 0;
    public function apply(object $e): void {
        match (true) {
            $e instanceof MoneyDeposited => $this->balanceCents += $e->amountCents,
            $e instanceof MoneyWithdrawn => $this->balanceCents -= $e->amountCents,
        };
        $this->version++;
    }
    public static function rehydrate(iterable $events): self {
        $a = new self();
        foreach ($events as $e) $a->apply($e);
        return $a;
    }
}
```

## Good — TypeScript

```ts
await eventStore.append(`account-${id}`, [
  { type: 'MoneyWithdrawn', aggregateId: id, amountCents: 500, at: new Date(), version: current + 1 },
], { expectedVersion: current });

class Account {
  balanceCents = 0;
  version = 0;
  apply(e: DomainEvent) {
    if (e.type === 'MoneyDeposited') this.balanceCents += e.amountCents;
    if (e.type === 'MoneyWithdrawn') this.balanceCents -= e.amountCents;
    this.version++;
  }
  static rehydrate(events: DomainEvent[]): Account {
    const a = new Account();
    events.forEach(e => a.apply(e));
    return a;
  }
}
```

`expectedVersion` is optimistic concurrency — concurrent writers get rejected instead of corrupting the stream. Snapshots every N events keep rehydration fast.
