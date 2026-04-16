---
title: One service per bounded context
impact: CRITICAL
tags: [boundaries, ddd]
---

# boundary-ddd-bounded-contexts

A microservice maps to **one** bounded context with its own ubiquitous language. A `Customer` in Billing is not the same entity as a `Customer` in Shipping — they share an ID, nothing else. Forcing one model across contexts produces a god-object that every team must coordinate on.

## Bad — PHP

```php
// shared/Models/Customer.php — used by billing, shipping, support
class Customer {
    public string $id;
    public string $name;
    public string $vatNumber;      // billing cares
    public string $shippingNotes;  // shipping cares
    public int $supportTier;       // support cares
    public array $invoices;        // billing
    public array $shipments;       // shipping
    public array $tickets;         // support
}
```

## Bad — TypeScript

```ts
// @org/shared/customer.ts
export interface Customer {
  id: string;
  name: string;
  vatNumber: string;
  shippingNotes: string;
  supportTier: number;
  invoices: Invoice[];
  shipments: Shipment[];
  tickets: Ticket[];
}
```

Every team must coordinate on this shape; a field change ripples across three services.

## Good — PHP

```php
// billing-service/src/Domain/Customer.php
final class Customer {
    public function __construct(
        public readonly CustomerId $id,
        public readonly string $legalName,
        public readonly VatNumber $vat,
    ) {}
}

// shipping-service/src/Domain/Customer.php
final class Customer {
    public function __construct(
        public readonly CustomerId $id,
        public readonly Address $defaultAddress,
        public readonly ?string $deliveryNotes,
    ) {}
}
```

## Good — TypeScript

```ts
// billing-service/src/domain/customer.ts
export interface Customer {
  id: CustomerId;
  legalName: string;
  vat: VatNumber;
}

// shipping-service/src/domain/customer.ts
export interface Customer {
  id: CustomerId;
  defaultAddress: Address;
  deliveryNotes?: string;
}
```

Each service owns the shape it needs. The only shared contract is `CustomerId` — usually propagated via events.
