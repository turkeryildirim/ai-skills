# Persistence Layer Patterns

Local persistence patterns for Android using Room and SQLDelight for KMP. Covers entity design, DAOs, repository pattern, mappers, migrations, and testing.

## 1. Room Entity Definition

```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?,
    val createdAt: Long,
    val updatedAt: Long,
)

@Entity(
    tableName = "orders",
    foreignKeys = [
        ForeignKey(
            entity = UserEntity::class,
            parentColumns = ["id"],
            childColumns = ["userId"],
            onDelete = ForeignKey.CASCADE,
        ),
    ],
    indices = [Index("userId")],
)
data class OrderEntity(
    @PrimaryKey
    val id: String,
    val userId: String,
    val title: String,
    val status: String,
    val totalCents: Int,
    val createdAt: Long,
)
```

| Annotation | Purpose |
|---|---|
| `@Entity(tableName = "...")` | Defines a database table |
| `@PrimaryKey` | Marks the primary key column |
| `@PrimaryKey(autoGenerate = true)` | Auto-increment integer primary key |
| `@ColumnInfo(name = "...")` | Custom column name |
| `@Ignore` | Exclude field from persistence |
| `@Embedded` | Nest another data class as columns |
| `@ForeignKey` | Define referential integrity |
| `@Index` | Add database index for query performance |

### Column Type Mapping

| Kotlin Type | SQLite Type |
|---|---|
| `String` | TEXT |
| `Int` | INTEGER |
| `Long` | INTEGER |
| `Double` | REAL |
| `Boolean` | INTEGER (0/1) |
| `Float` | REAL |
| `ByteArray` | BLOB |

For complex types (enums, dates), use `@TypeConverter`:

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? = date?.time

    @TypeConverter
    fun fromOrderStatus(value: String): OrderStatus = OrderStatus.valueOf(value)

    @TypeConverter
    fun orderStatusToString(status: OrderStatus): String = status.name
}
```

## 2. Room DAO Interfaces

```kotlin
@Dao
interface UserDao {

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserById(id: String): UserEntity?

    @Query("SELECT * FROM users ORDER BY createdAt DESC")
    fun getAllUsers(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE name LIKE '%' || :query || '%'")
    fun searchUsers(query: String): Flow<List<UserEntity>>

    @Upsert
    suspend fun upsertUser(user: UserEntity)

    @Upsert
    suspend fun upsertUsers(users: List<UserEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertUsers(users: List<UserEntity>)

    @Delete
    suspend fun deleteUser(user: UserEntity)

    @Query("DELETE FROM users WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM users")
    suspend fun deleteAll()

    @Query("SELECT COUNT(*) FROM users")
    suspend fun count(): Int

    @Transaction
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserWithOrders(id: String): UserWithOrders?
}
```

### Return Type Guide

| Return Type | Use Case | Thread Safety |
|---|---|---|
| `suspend fun ...` | One-shot read/write | Safe (Room ensures not on main) |
| `Flow<T>` | Observe data changes reactively | Safe (emits on background) |
| `LiveData<T>` | Legacy observe pattern | Safe |
| `PagingSource<Int, T>` | Paging 3 integration | Safe |

**Use `Flow` return types for data the UI observes.** Use `suspend` for one-shot operations (insert, delete, count).

### Upsert vs Insert

| Operation | Behavior |
|---|---|
| `@Insert(REPLACE)` | Deletes old row, inserts new (triggers CASCADE) |
| `@Upsert` | Updates existing row or inserts new (no CASCADE) |
| `@Insert(IGNORE)` | Skips if row exists |

Prefer `@Upsert` over `@Insert(REPLACE)` to avoid unintended cascade deletions.

### Relations

```kotlin
data class UserWithOrders(
    @Embedded val user: UserEntity,
    @Relation(
        parentColumn = "id",
        entityColumn = "userId",
    )
    val orders: List<OrderEntity>,
)
```

## 3. Room Database Class

```kotlin
@Database(
    entities = [
        UserEntity::class,
        OrderEntity::class,
    ],
    version = 2,
    exportSchema = true,
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun orderDao(): OrderDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app-database",
                )
                    .addMigrations(MIGRATION_1_2)
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}
```

With Hilt:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app-database",
        ).build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao = database.userDao()

    @Provides
    fun provideOrderDao(database: AppDatabase): OrderDao = database.orderDao()
}
```

## 4. Repository Pattern with Room

```kotlin
interface UserRepository {
    fun getUsers(): Flow<List<User>>
    suspend fun getUser(id: String): Result<User>
    suspend fun saveUser(user: User)
    suspend fun deleteUsers(ids: List<String>)
}

class UserRepositoryImpl @Inject constructor(
    private val userDao: UserDao,
    private val api: UserApi,
) : UserRepository {

    override fun getUsers(): Flow<List<User>> =
        userDao.getAllUsers().map { entities ->
            entities.map { it.toDomain() }
        }

    override suspend fun getUser(id: String): Result<User> = runCatching {
        userDao.getUserById(id)?.toDomain() ?: fetchFromRemote(id)
    }

    override suspend fun saveUser(user: User) {
        userDao.upsertUser(user.toEntity())
    }

    override suspend fun deleteUsers(ids: List<String>) {
        ids.forEach { userDao.deleteById(it) }
    }

    private suspend fun fetchFromRemote(id: String): User {
        val response = api.getUser(id)
        val entity = response.toEntity()
        userDao.upsertUser(entity)
        return entity.toDomain()
    }
}
```

The repository exposes `Flow` for observed data and `suspend` for one-shot operations. Data flows from Room → Entity → Mapper → Domain.

## 5. Mapper Pattern

```kotlin
fun UserEntity.toDomain(): User = User(
    id = id,
    name = name,
    email = email,
    avatarUrl = avatarUrl ?: "",
    createdAt = Instant.fromEpochMilliseconds(createdAt),
)

fun User.toEntity(): UserEntity = UserEntity(
    id = id,
    name = name,
    email = email,
    avatarUrl = avatarUrl,
    createdAt = createdAt.toEpochMilliseconds(),
    updatedAt = Clock.System.now().toEpochMilliseconds(),
)

fun UserResponse.toEntity(): UserEntity = UserEntity(
    id = id.orEmpty(),
    name = name.orEmpty(),
    email = email.orEmpty(),
    avatarUrl = avatarUrl,
    createdAt = System.currentTimeMillis(),
    updatedAt = System.currentTimeMillis(),
)

fun UserResponse.toDomain(): User = toEntity().toDomain()
```

| Mapper | Direction | Location |
|---|---|---|
| `Entity.toDomain()` | Data → Domain | `data/mapper/` |
| `Domain.toEntity()` | Domain → Data | `data/mapper/` |
| `Response.toEntity()` | Network → Data | `data/mapper/` |
| `Response.toDomain()` | Network → Domain | `data/mapper/` (via Entity) |

Keep mappers as extension functions in the `data` module. The `domain` module has no knowledge of entities or DTOs.

## 6. SQLDelight for KMP

### .sq File

```sql
-- sqldelight/com/example/data/UserQueries.sq

CREATE TABLE users (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    avatar_url TEXT,
    created_at INTEGER NOT NULL
);

getById:
SELECT * FROM users WHERE id = ?;

getAll:
SELECT * FROM users ORDER BY created_at DESC;

search:
SELECT * FROM users WHERE name LIKE '%' || ? || '%';

upsert:
INSERT OR REPLACE INTO users (id, name, email, avatar_url, created_at)
VALUES (?, ?, ?, ?, ?);

deleteById:
DELETE FROM users WHERE id = ?;

count:
SELECT COUNT(*) FROM users;
```

### Usage

```kotlin
class UserRepositoryImpl(
    private val database: AppDatabase,
) : UserRepository {

    override fun getUsers(): Flow<List<User>> =
        database.userQueries.getAll()
            .asFlow()
            .mapToList(Dispatchers.IO)
            .map { rows -> rows.map { it.toDomain() } }

    override suspend fun getUser(id: String): Result<User> = runCatching {
        database.userQueries.getById(id).executeAsOne().toDomain()
    }

    override suspend fun saveUser(user: User) {
        database.userQueries.upsert(
            user.id,
            user.name,
            user.email,
            user.avatarUrl,
            user.createdAt.toEpochMilliseconds(),
        )
    }
}
```

| Room | SQLDelight | KMP Support |
|---|---|---|
| `@Entity` | `CREATE TABLE` in `.sq` file | SQLDelight only |
| `@Dao` | Named queries in `.sq` file | SQLDelight only |
| `@Database` | Generated `AppDatabase` | SQLDelight only |
| `Flow<T>` | `.asFlow().mapToList()` | Both |
| `@TypeConverter` | Adapter classes | SQLDelight only |
| `@Migration` | `SqlSchema` | Both |

## 7. In-Memory Database for Testing

```kotlin
@HiltAndroidTest
class UserDaoTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var database: AppDatabase

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun insertAndRetrieve() = runTest {
        val dao = database.userDao()
        dao.upsertUser(testUserEntity)
        val result = dao.getUserById("123")
        assertEquals("John", result?.name)
    }
}
```

For pure unit tests without Hilt:

```kotlin
class UserDaoTest {

    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(
            context,
            AppDatabase::class.java,
        ).allowMainThreadQueries().build()
        userDao = database.userDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun insertAndRetrieve() = runTest {
        userDao.upsertUser(testUserEntity)
        val result = userDao.getUserById("123")
        assertEquals("John", result?.name)
    }
}
```

`Room.inMemoryDatabaseBuilder` creates a database in memory that is destroyed when the test completes. Use `allowMainThreadQueries()` only in tests.

## 8. Migration Strategies

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("CREATE TABLE orders (id TEXT NOT NULL PRIMARY KEY, userId TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, totalCents INTEGER NOT NULL, createdAt INTEGER NOT NULL)")
        db.execSQL("CREATE INDEX index_orders_userId ON orders (userId)")
    }
}

Room.databaseBuilder(context, AppDatabase::class.java, "app-database")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .fallbackToDestructiveMigration()
    .build()
```

| Strategy | When to Use | Data Loss |
|---|---|---|
| `Migration` | Production app updates | None |
| `fallbackToDestructiveMigration` | Debug builds only | All data lost |
| `destructiveMigration` never in release | Never | All data lost |

Migration testing:

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {

    private val testHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java,
    )

    @Test
    fun migrate1To2() {
        val db = testHelper.createDatabase("app-database", 1)
        db.execSQL("INSERT INTO users (id, name, email, createdAt) VALUES ('1', 'John', 'john@test.com', 0)")
        db.close()

        val migratedDb = testHelper.runMigrationsAndValidate(
            "app-database",
            2,
            true,
            MIGRATION_1_2,
        )
        val cursor = migratedDb.query("SELECT avatar_url FROM users WHERE id = '1'")
        cursor.moveToFirst()
        assertNull(cursor.getString(0))
        migratedDb.close()
    }
}
```

## 9. Anti-Patterns

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| Exposing entities to UI | Couples UI to database schema | Map entities to domain models via mappers |
| Queries on main thread | ANR and UI jank | Use `suspend` or `Flow` return types |
| No error handling in DAOs | Room exceptions crash the app | Wrap in `runCatching` or `Result` at repository level |
| `fallbackToDestructiveMigration` in release | Users lose all data | Write proper `Migration` classes |
| `allowMainThreadQueries()` in production | ANR | Only use in tests |
| Large objects in single table | Performance degradation | Normalize or use `@Embedded` |
| Missing `@TypeConverters` | Compile error for unsupported types | Add converter for Date, Enum, etc. |
| No indexes on query columns | Full table scans | Add `@Index` on frequently queried columns |
| `@Insert(REPLACE)` with foreign keys | Triggers CASCADE deletes unexpectedly | Use `@Upsert` instead |

## Cross References

- Related rules: `arch-no-entity-in-ui`, `arch-repo-iface-in-domain`, `arch-mapper-in-data`, `arch-repo-returns-flow`
- Related references: [`dependency-injection.md`](dependency-injection.md), [`networking.md`](networking.md), [`build-configuration.md`](build-configuration.md)
