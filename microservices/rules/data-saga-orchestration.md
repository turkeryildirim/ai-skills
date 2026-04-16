---
title: Central orchestrator drives saga steps and compensations
impact: CRITICAL
tags: [data, saga]
---

# data-saga-orchestration

For complex workflows with branches or 4+ steps, an orchestrator owns the state machine: it calls each service, records progress, and triggers compensations on failure. The flow lives in one file instead of being scattered across event handlers.

## Bad — PHP

```php
// Pseudo-2PC across services: doomed
DB::beginTransaction();
$this->inventory->reserve($order);
$this->payments->charge($order);   // network failure here = inconsistent state
$this->shipping->schedule($order);
DB::commit();
```

## Bad — TypeScript

```ts
await Promise.all([
  inventory.reserve(order),
  payments.charge(order),   // if this fails, inventory already reserved forever
  shipping.schedule(order),
]);
```

## Good — PHP

```php
final class PlaceOrderSaga {
    public function run(OrderId $id): void {
        $state = $this->store->load($id) ?? SagaState::started($id);
        try {
            if (!$state->hasDone('reserve'))  { $this->inventory->reserve($id); $state->mark('reserve'); $this->store->save($state); }
            if (!$state->hasDone('charge'))   { $this->payments->charge($id);   $state->mark('charge');  $this->store->save($state); }
            if (!$state->hasDone('schedule')) { $this->shipping->schedule($id); $state->mark('schedule');$this->store->save($state); }
            $state->complete();
        } catch (\Throwable $e) {
            if ($state->hasDone('charge'))   $this->payments->refund($id);
            if ($state->hasDone('reserve'))  $this->inventory->release($id);
            $state->fail($e->getMessage());
            throw $e;
        } finally {
            $this->store->save($state);
        }
    }
}
```

## Good — TypeScript

```ts
export class PlaceOrderSaga {
  async run(id: OrderId): Promise<void> {
    const state = (await this.store.load(id)) ?? SagaState.started(id);
    try {
      if (!state.has('reserve'))  { await this.inventory.reserve(id); state.mark('reserve');  await this.store.save(state); }
      if (!state.has('charge'))   { await this.payments.charge(id);   state.mark('charge');   await this.store.save(state); }
      if (!state.has('schedule')) { await this.shipping.schedule(id); state.mark('schedule'); await this.store.save(state); }
      state.complete();
    } catch (err) {
      if (state.has('charge'))   await this.payments.refund(id);
      if (state.has('reserve'))  await this.inventory.release(id);
      state.fail(String(err));
      throw err;
    } finally {
      await this.store.save(state);
    }
  }
}
```

State persisted after every step → saga is resumable after a crash. Each step and compensation is idempotent.
