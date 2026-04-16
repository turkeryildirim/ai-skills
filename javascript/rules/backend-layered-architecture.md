---
title: Layered Architecture Separation
impact: HIGH
impactDescription: Mixing concerns in route handlers creates untestable, unmaintainable spaghetti code.
tags: architecture, separation-of-concerns, express
---

# Layered Architecture Separation

Enforce strict Controller / Service / Repository layers so that HTTP handling, business logic, and data access remain decoupled and independently testable.

## Bad Example

```typescript
// routes/user.routes.ts — business logic and SQL crammed into the route handler
router.post("/users", async (req, res) => {
  const { name, email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: "Missing fields" });
  }

  const existing = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
  if (existing.rows.length > 0) {
    return res.status(409).json({ error: "Email taken" });
  }

  const hashed = await bcrypt.hash(password, 10);
  const result = await pool.query(
    "INSERT INTO users (name, email, password) VALUES ($1, $2, $3) RETURNING *",
    [name, email, hashed],
  );

  res.status(201).json(result.rows[0]);
});
```

## Good Example

```typescript
// repositories/user.repository.ts — data access only
export class UserRepository {
  constructor(private db: Pool) {}

  async findByEmail(email: string): Promise<UserEntity | null> {
    const { rows } = await this.db.query("SELECT * FROM users WHERE email = $1", [email]);
    return rows[0] || null;
  }

  async create(userData: CreateUserDTO & { password: string }): Promise<UserEntity> {
    const query = `
      INSERT INTO users (name, email, password)
      VALUES ($1, $2, $3) RETURNING id, name, email, created_at
    `;
    const { rows } = await this.db.query(query, [userData.name, userData.email, userData.password]);
    return rows[0];
  }
}

// services/user.service.ts — business logic only
export class UserService {
  constructor(private userRepo: UserRepository) {}

  async createUser(data: CreateUserDTO): Promise<User> {
    const existing = await this.userRepo.findByEmail(data.email);
    if (existing) throw new ConflictError("Email already exists");

    const hashed = await bcrypt.hash(data.password, 10);
    const user = await this.userRepo.create({ ...data, password: hashed });
    return user;
  }
}

// controllers/user.controller.ts — HTTP orchestration only
export class UserController {
  constructor(private userService: UserService) {}

  async createUser(req: Request, res: Response, next: NextFunction) {
    const user = await this.userService.createUser(req.body);
    res.status(201).json(user);
  }
}
```

## Why

- **Benefit**: Each layer has a single responsibility, making code easier to test -- repositories can be mocked in service tests, services in controller tests.
- **Benefit**: SQL stays in repositories, business rules stay in services, HTTP mapping stays in controllers. Changing the database or the framework only touches one layer.
- **Benefit**: Dependency injection across layers enables loose coupling and straightforward unit testing without spinning up a real server or database.
