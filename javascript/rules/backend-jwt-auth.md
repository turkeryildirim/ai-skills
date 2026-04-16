---
title: Secure JWT Authentication
impact: CRITICAL
impactDescription: Plaintext passwords and long-lived tokens expose users to credential theft and account takeover.
tags: authentication, jwt, bcrypt, security
---

# Secure JWT Authentication

Hash passwords with bcrypt, issue short-lived access tokens paired with refresh tokens, and store secrets in environment variables.

## Bad Example

```typescript
// Plaintext passwords, single long-lived token, hardcoded secret
export class AuthService {
  async register(email: string, password: string) {
    const result = await pool.query(
      "INSERT INTO users (email, password) VALUES ($1, $2) RETURNING id, email",
      [email, password], // stored in plaintext — catastrophic on breach
    );

    const token = jwt.sign(
      { userId: result.rows[0].id },
      "my-super-secret-key", // hardcoded secret in source code
      { expiresIn: "365d" }, // token valid for a year — no revocation possible
    );

    return { token, user: result.rows[0] };
  }

  async login(email: string, password: string) {
    const { rows } = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (rows[0]?.password === password) { // timing-unsafe string comparison
      return jwt.sign({ userId: rows[0].id }, "my-super-secret-key", { expiresIn: "365d" });
    }
    throw new Error("Invalid credentials");
  }
}
```

## Good Example

```typescript
export class AuthService {
  constructor(private userRepo: UserRepository) {}

  async register(data: RegisterDTO) {
    const hashedPassword = await bcrypt.hash(data.password, 10); // salted hash
    const user = await this.userRepo.create({ ...data, password: hashedPassword });

    return {
      accessToken: this.generateToken({ userId: user.id, email: user.email }),
      refreshToken: this.generateRefreshToken({ userId: user.id }),
      user: { id: user.id, name: user.name, email: user.email },
    };
  }

  async login(email: string, password: string) {
    const user = await this.userRepo.findByEmail(email);
    if (!user) throw new UnauthorizedError("Invalid credentials");

    const isValid = await bcrypt.compare(password, user.password); // constant-time compare
    if (!isValid) throw new UnauthorizedError("Invalid credentials");

    return {
      accessToken: this.generateToken({ userId: user.id, email: user.email }),
      refreshToken: this.generateRefreshToken({ userId: user.id }),
    };
  }

  async refresh(token: string) {
    const payload = jwt.verify(token, process.env.REFRESH_TOKEN_SECRET!) as { userId: string };
    const user = await this.userRepo.findById(payload.userId);
    if (!user) throw new UnauthorizedError("User not found");

    return { accessToken: this.generateToken({ userId: user.id, email: user.email }) };
  }

  private generateToken(payload: any): string {
    return jwt.sign(payload, process.env.JWT_SECRET!, { expiresIn: "15m" });
  }

  private generateRefreshToken(payload: any): string {
    return jwt.sign(payload, process.env.REFRESH_TOKEN_SECRET!, { expiresIn: "7d" });
  }
}
```

## Why

- **Benefit**: bcrypt hashing with a cost factor of 10 makes offline brute-force attacks computationally infeasible even if the database is breached.
- **Benefit**: Short-lived access tokens (15 min) limit the window of exploitation; refresh tokens (7 days) let users stay logged in without re-entering credentials.
- **Benefit**: Secrets read from environment variables never appear in source code or version control, eliminating accidental credential leaks.
