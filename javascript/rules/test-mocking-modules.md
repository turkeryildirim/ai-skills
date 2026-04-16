---
title: Mock External Modules with vi.mock
impact: HIGH
impactDescription: Hitting real SMTP servers, APIs, or databases in unit tests causes flaky failures and exposes secrets.
tags: testing, mocking, vitest, jest, best-practices
---

# Mock External Modules with vi.mock

External services (email, APIs, databases) must be mocked at the module level using `vi.mock()` with a factory function.

## Bad Example

```typescript
// Actually connects to a real SMTP server in tests
import nodemailer from "nodemailer";

it("sends an email", async () => {
  const service = new EmailService();
  // This fires a real network request!
  await service.sendEmail("user@test.com", "Hello", "<p>Hi</p>");
});

// Partially mocking by overwriting internals after import
import { paymentGateway } from "payment-sdk";
it("charges a card", async () => {
  (paymentGateway as any).charge = () => ({ success: true });
  // Other methods still hit the real SDK
});
```

## Good Example

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { EmailService } from "./email.service";

// Mock the entire module at the top with a factory
vi.mock("nodemailer", () => ({
  default: {
    createTransport: vi.fn(() => ({
      sendMail: vi.fn().mockResolvedValue({ messageId: "123" }),
    })),
  },
}));

describe("EmailService", () => {
  let service: EmailService;

  beforeEach(() => {
    service = new EmailService();
  });

  it("should send email successfully", async () => {
    await service.sendEmail(
      "test@example.com",
      "Test Subject",
      "<p>Test Body</p>",
    );

    // Verify the mock was called with correct arguments
    expect(service["transporter"].sendMail).toHaveBeenCalledWith(
      expect.objectContaining({
        to: "test@example.com",
        subject: "Test Subject",
      }),
    );
  });

  it("should propagate send failures", async () => {
    service["transporter"].sendMail.mockRejectedValueOnce(
      new Error("SMTP refused"),
    );

    await expect(
      service.sendEmail("test@example.com", "Fail", "<p>Nope</p>"),
    ).rejects.toThrow("SMTP refused");
  });
});
```

## Why

- **Benefit**: `vi.mock()` with a factory replaces the entire module before import, guaranteeing no real network calls.
- **Benefit**: Mock return values let you control every scenario (success, failure, edge cases) without infrastructure.
- **Benefit**: Verifying call arguments ensures your code interacts with the dependency correctly.
