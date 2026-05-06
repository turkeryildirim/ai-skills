---
title: PHP Namespace and Directory Structure
impact: HIGH
impactDescription: "Misaligned namespaces break autoloading and signal lack of framework understanding"
tags: php, namespace, psr-4, autoloading, structure
---

## PHP Namespace and Directory Structure

**Impact: HIGH (Misaligned namespaces break autoloading and signal lack of framework understanding)**

PSR-4 autoloading is the foundation of modern PHP projects. When namespace declarations don't match the directory structure defined in `composer.json`, classes fail to autoload, tests break, and the project cannot be reliably refactored. This is one of the first things to check in a PHP project scan.

## Incorrect

```php
// ❌ composer.json defines:
{
  "autoload": {
    "psr-4": {
      "App\\": "app/"
    }
  }
}

// ❌ But the file is at: app/Services/Payment/StripeService.php
// with namespace declaration:
namespace App\Services\Payments\Stripe; // "Payments" plural — doesn't match "Payment" directory

// ❌ Or worse: no namespace at all
// app/helpers.php
function formatCurrency($amount) { ... }  // global function pollution

// ❌ Class name doesn't match filename
// File: app/Services/payment_service.php
class PaymentService { ... }  // PSR-4 requires PascalCase matching filename
```

```
// ❌ Flat structure — all classes in one directory
app/
├── UserController.php
├── ProductController.php
├── UserService.php
├── ProductService.php
├── User.php
├── Product.php
// No domain separation, no discoverability
```

## Correct

```php
// ✅ composer.json with proper PSR-4 mapping
{
  "autoload": {
    "psr-4": {
      "App\\": "app/"
    }
  },
  "autoload-dev": {
    "psr-4": {
      "Tests\\": "tests/"
    }
  }
}

// ✅ File: app/Services/Payment/StripePaymentService.php
namespace App\Services\Payment;

class StripePaymentService implements PaymentGateway
{
    // namespace App\Services\Payment matches path app/Services/Payment/
}
```

```
// ✅ Domain-organized structure (Laravel)
app/
├── Actions/
│   └── Order/
│       ├── CreateOrderAction.php     → App\Actions\Order\CreateOrderAction
│       └── CancelOrderAction.php
├── Contracts/
│   └── PaymentGateway.php            → App\Contracts\PaymentGateway
├── Http/
│   └── Controllers/
│       └── OrderController.php       → App\Http\Controllers\OrderController
├── Models/
│   └── Order.php                     → App\Models\Order
└── Services/
    └── Payment/
        └── StripePaymentService.php  → App\Services\Payment\StripePaymentService
```

## What to Look For During Analysis

```
✅ Namespace declaration matches directory path exactly
✅ Class filename matches class name (PascalCase)
✅ autoload-dev section present for test namespaces
✅ No global functions outside of explicitly registered helpers
✅ Domain-organized subdirectories (not flat app/ dump)

❌ "Payments" namespace for "Payment" directory (pluralization mismatch)
❌ Lowercase filenames for class files
❌ Missing composer.json autoload section
❌ Classes outside of declared PSR-4 roots (causing require_once fallbacks)
❌ test files in app/ instead of tests/
```

## Why

- **Autoloading reliability**: Mismatched namespaces cause `Class not found` errors during testing and refactoring
- **Discoverability**: Domain-organized namespaces let developers find classes by business concept, not by type
- **Tooling compatibility**: PHPStan, IDE autocompletion, and `php artisan ide-helper` all depend on correct PSR-4 mapping
