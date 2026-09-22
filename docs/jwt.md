# JWT authentication and user-owned todos

This guide describes how to add authentication to this project and make every todo belong to exactly one user. It is intentionally implementation-focused, but contains no source-code snippets: use it as a checklist while writing the code yourself.

## 1. Target behavior

The finished API should behave as follows:

- An unauthenticated visitor can register and log in.
- Registration stores a user record and a password hash, never the original password.
- Login verifies the password and returns a short-lived JWT access token.
- Protected todo endpoints require a valid bearer token.
- The authenticated user is taken from the token, not from a request body, query parameter, or path parameter.
- A user can list, create, update, and eventually delete only their own todos.
- A user cannot discover whether another user's todo exists through an update or lookup response.
- Database constraints provide a final ownership guarantee even if an API-layer mistake is introduced later.

The current application creates tables during startup. That is acceptable while learning, but production and shared QA environments should use migrations so that adding authentication does not silently alter or damage existing data.

## 2. Dependencies and their responsibilities

Add these direct dependencies to the project:

- `PyJWT`: signs and verifies JWTs. Use a maintained version and an asymmetric algorithm for deployed environments when you have a key-management process; a strong HMAC secret is simpler for local development.
- `pwdlib` with its Argon2 extra: hashes and verifies passwords using Argon2. Do not hash passwords with plain SHA-256, MD5, or reversible encryption.
- `python-multipart`: required by FastAPI's OAuth2 password-form dependency because login credentials are sent as form data.
- `alembic`: manages schema migrations. This becomes important when adding the users table and the non-null todo ownership column to an existing database.

The project already includes FastAPI's security primitives, Pydantic settings, SQLAlchemy's async ORM, and asyncpg. FastAPI supplies the bearer-token extraction and OAuth2 form helpers; it does not itself hash passwords or issue JWTs.

## 3. Configuration and secrets

Extend the settings model with authentication configuration. Keep separate values in each environment file: development, QA, and production.

Recommended settings are:

- JWT signing algorithm.
- JWT access-token lifetime in minutes, kept short (for example, approximately 15 to 30 minutes).
- A long, random signing secret for local or HMAC-based deployments.
- Production private/public key locations or secret-manager references if you choose an asymmetric algorithm.
- Issuer and audience values if tokens may be consumed by more than this API.

Never commit real signing secrets, database passwords, or production environment files. Ensure the settings loader and the process that launches the application select the same environment file. The current loader uses the lowercase process variable `env` and looks for a file named `.env.<value>`, defaulting to `.env.dev`; the existing `.env` file is therefore not selected by default.

Use a different JWT secret in every environment. Rotating a secret invalidates tokens signed with the old value, so plan a rotation strategy before production. Do not log the secret, raw password, or complete token.

## 4. Database model changes

### User model

Create a user model with at least:

- A primary-key identifier. A UUID is a good long-term choice; matching the existing integer style is also workable if consistency is more important.
- A unique, indexed login identifier such as email. Normalize it before storage and comparison, usually by trimming whitespace and applying a consistent case policy.
- A password-hash column with enough length for Argon2 output.
- An active/disabled flag so accounts can be revoked without deleting their history.
- Creation and update timestamps.

Do not store a plaintext password, a reversible password, or a password supplied by a client as a user identifier.

#### User model field blueprint

Use the following as the exact design checklist while writing the SQLAlchemy model. The “Why needed” explanation is the reason each field or constraint belongs in the model.

| Field or rule | Recommended design | Why needed |
| --- | --- | --- |
| User table name | A dedicated `users` table | Authentication data needs its own lifecycle and must be referenced by todos through a foreign key. |
| User identifier | A non-null primary key; a UUID is preferred for a public-facing API, while an integer is acceptable if you want to match the current todo identifier style | The identifier links todos to users and identifies the subject of a JWT without using an email address as a permanent database key. |
| Login identifier | A non-null, indexed email or username column | Login needs a fast lookup, and the identifier must be present for every account. |
| Login identifier uniqueness | A database-level unique constraint on the normalized value | Application pre-checks can race; the database must prevent two accounts from claiming the same login identifier. |
| Password hash | A non-null text or sufficiently large string column | Argon2 hashes include parameters and salt, so the column must store the complete encoded hash rather than a truncated value. |
| Active status | A non-null boolean that defaults to active | Disabling an account should invalidate access without deleting its todos or audit history. |
| Created timestamp | A non-null, database-generated timestamp | It supports auditing, support investigations, and account-age policies without trusting client input. |
| Updated timestamp | A non-null timestamp updated whenever user data changes | It provides an audit signal and helps identify stale or unexpectedly modified accounts. |
| Identifier normalization | Normalize before lookup and storage; choose one case policy and apply it consistently | Without normalization, visually identical identifiers can create duplicate accounts or make login behavior surprising. |
| Password exposure | Never include the password hash in public response schemas | A password hash is still sensitive credential material and should not leave the service. |

Do not make the password hash unique, do not use the password as a username, and do not allow clients to submit the primary-key value during registration.

### Todo ownership

Add a `user_id` column to the todo model. It should be non-null after migration and a foreign key to the users table. Add an index on it because every todo query will filter by owner.

Add the ORM relationship in both directions if it helps your service layer: a user has many todos, and a todo belongs to one user. Keep the foreign-key column as the authoritative value used in queries.

The current todo name is globally unique. Decide whether that is intentional. For user-owned todos, the usual rule is that names need only be unique per user, if unique at all. If that is the desired rule, replace the global uniqueness with a composite uniqueness rule over user identifier and name. If names do not need uniqueness, remove the uniqueness constraint.

#### Todo model field and constraint changes

Keep the existing todo fields unless the product requirements say otherwise, but review each one against this checklist:

| Field or rule | Required change | Why needed |
| --- | --- | --- |
| Todo primary key | Keep the existing primary key strategy unless there is a separate reason to change it | Existing clients and routes already address todos by this identifier; changing it would expand the authentication work unnecessarily. |
| `user_id` | Add a non-null foreign-key column referencing the users primary key | This is the database-level ownership link that makes every todo belong to exactly one user. |
| `user_id` index | Add an index, either directly or as part of a composite index | Listing and locating a todo always includes the owner, so the index keeps those queries efficient as data grows. |
| Foreign-key delete behavior | Choose deliberately: restrict user deletion, or explicitly define a controlled cascade | The choice determines whether deleting a user preserves or removes personal data; accidental orphan rows must not be possible. |
| Todo name | Remove the current global uniqueness if names should be reusable by different users | A global constraint would incorrectly prevent two independent users from creating todos with the same name. |
| Per-user name uniqueness | If names must be unique, enforce uniqueness on the combination of `user_id` and `name` | This enforces the intended rule at the database boundary while allowing the same name in different accounts. |
| Description | Keep nullable if a description is optional | Nullability should match the API contract and avoids forcing clients to send meaningless empty text. |
| Completion flag | Keep non-null and choose a database/application default of false | Every todo should have a deterministic completion state even when the client omits it. |
| Created timestamp | Keep database-generated and non-null | Creation time should be authoritative and should not be supplied by an untrusted client. |
| Updated timestamp | Keep automatically updated on modifications | Clients and support tools need to know when a todo was last changed without manually maintaining timestamps. |
| Client ownership fields | Do not add an owner field to create or update request schemas | Ownership must come from the validated JWT, otherwise a user could assign or transfer a todo to another account. |

The ORM relationship between user and todos is useful for navigation and serialization control, but it is not a substitute for filtering queries by `user_id`. The foreign key and owner-scoped query conditions are the security boundary.

### Migration order

For an empty database, create users first and todos with a required owner. For an existing database, use a staged migration:

1. Create the users table.
2. Add `user_id` to todos as nullable.
3. Decide how existing todos are assigned: create a known migration user, map them to real users, or archive/delete them. Do not guess an owner.
4. Backfill every existing todo.
5. Add the foreign key, index, and non-null constraint.
6. Remove any old global name constraint if the new business rule is per-user uniqueness.

Do not rely on `Base.metadata.create_all` to perform this evolution. It does not safely migrate existing tables.

#### Migration acceptance checks

Before considering the model migration complete, verify all of the following:

- The users table exists before the todo foreign key is created.
- Every existing todo has an intentional owner before `user_id` becomes non-null.
- The foreign key rejects an owner identifier that does not exist.
- The owner index exists and is used by owner-filtered queries.
- The old global todo-name uniqueness rule is removed if the product rule is per-user uniqueness.
- The replacement per-user uniqueness rule rejects duplicates for one user but permits the same name for two different users.
- User deletion behavior matches the documented product decision.
- The migration can be applied to a fresh database and to a copy of the current database.
- The migration can be rolled back or has a documented recovery procedure before QA and production use.

## 5. Authentication module boundaries

Keep authentication responsibilities separate from todo business logic.

Suggested modules and responsibilities:

- An auth model module for the user database entity.
- Auth request/response schemas for registration, login, and token responses. Never return the password hash in a response schema.
- A user repository for lookup by identifier, creation, and account-status checks.
- An auth service for normalization, password hashing, password verification, and token creation.
- A token utility for encoding and decoding JWTs and validating claims.
- An authentication dependency that extracts the bearer token, validates it, loads the user, and rejects invalid or inactive accounts.
- Auth routes for registration and login.

The existing todo dependency currently builds a todo service from a database session. Extend that dependency chain so the authenticated user is obtained independently and then passed into the service operation. Avoid making the todo repository decode JWTs; repositories should receive an owner identifier and execute database queries.

## 6. Registration flow

The registration endpoint should:

1. Validate the identifier and password using a request schema.
2. Normalize the identifier in one place.
3. Look up an existing user using the normalized value.
4. Return a conflict response if it is already registered. Do not reveal unrelated account details.
5. Hash the password with Argon2 using the password library's recommended settings.
6. Store the new user and commit the transaction.
7. Return a safe user representation, or issue a token only if that is an explicit product decision.

Use a database uniqueness constraint as well as the pre-check, because two registrations can race. Convert a uniqueness violation into a clean conflict response.

## 7. Login and JWT flow

Use the OAuth2 password form convention for the login endpoint so the API works with FastAPI's standard security tooling. The form's username field can contain the user's email or other chosen identifier.

Login should:

1. Normalize the submitted identifier.
2. Load the user by that identifier.
3. Verify the submitted password against the stored Argon2 hash.
4. Reject unknown users, wrong passwords, and inactive users with the same generic authentication failure. Avoid revealing which part was wrong.
5. Create a signed access token whose subject identifies the user.
6. Include an expiration claim and a token-type claim indicating that it is an access token.
7. Return the token and its bearer type through a token response schema.

At minimum, validate the JWT signature, algorithm, subject, token type, and expiration on every protected request. Validate issuer and audience as well if you configure them. Never trust a decoded token until signature and claim validation succeeds.

Keep access tokens short-lived. If long-lived sessions are required, add refresh tokens as a separate design: store refresh-token identifiers or hashes, rotate them, support revocation, and never treat a long-lived access token as an acceptable substitute.

## 8. The current-user dependency

Create one reusable dependency that represents “the authenticated user.” Its sequence should be:

1. Read the bearer token from the authorization header.
2. Decode and validate the JWT.
3. Extract the subject as the user identifier.
4. Reject tokens with a missing, malformed, or non-sensical subject.
5. Load the user from the database.
6. Reject a missing or inactive user.
7. Return the user or a small authenticated-user object to the route.

Use the correct HTTP semantics: missing or invalid credentials should produce an authentication failure, while a valid user lacking a separate permission should produce a forbidden response. Do not accept a user ID supplied by the client as a substitute for the dependency result.

## 9. Make every todo query owner-scoped

This is the most important authorization rule. Every repository operation must include the authenticated user's identifier in its database condition.

- List queries filter by owner.
- Create operations set the owner from the authenticated user, never from the request body.
- Get-by-ID queries match both todo ID and owner ID.
- Update queries match both todo ID and owner ID before applying changes.
- Delete queries, when added, match both todo ID and owner ID.

If a lookup finds no row under that owner, return not found. This prevents a user from using IDs to distinguish another user's todo from a nonexistent todo. Do not fetch a todo by ID first and perform the ownership check only later unless you understand and deliberately accept the information leak.

Change the service method signatures so they receive the authenticated user context. The service should enforce business rules, while the repository should enforce owner-scoped persistence queries. The route should only connect request data, the authentication dependency, and the service.

Remove ownership fields from todo creation and update request schemas. A client must not be able to assign or transfer a todo by posting a different user ID.

## 10. Route design

Keep registration and login public. Protect all todo routes with the current-user dependency.

The todo route set should conceptually provide:

- List the current user's todos.
- Create a todo for the current user.
- Read a single todo owned by the current user.
- Update a todo owned by the current user.
- Delete a todo owned by the current user.

Add response schemas for todos rather than returning ORM objects implicitly. Include the owner identifier only if the client genuinely needs it; it is usually unnecessary for a personal todo API.

Review the existing create schema: `is_completed` currently has no default, so decide whether new todos should default to false. Review the update path for a missing todo before calling the repository update method; an absent record must become a not-found response rather than an attribute error.

## 11. Error and transaction behavior

Use consistent responses for authentication and authorization failures. Do not return stack traces, database errors, password hashes, or token contents to clients.

Keep registration and todo creation in clear transactions. Roll back after an exception before reusing the session. Handle unique-constraint races at the database boundary. Avoid committing in multiple unrelated layers for one logical operation.

The startup table-creation hook currently runs before the application accepts requests. Once migrations are in place, run migrations as a deployment step and remove schema mutation from application startup, especially when multiple production workers may start simultaneously.

## 12. Testing checklist

Write tests for the following cases before considering the feature complete:

- Registering a valid user succeeds.
- Duplicate identifiers are rejected.
- Passwords are stored only as hashes.
- Login succeeds with the correct password.
- Login fails with an incorrect password, unknown identifier, malformed token, expired token, wrong token type, and inactive user.
- A request without a bearer token is rejected.
- A user sees only their own todos.
- A created todo is assigned to the authenticated user regardless of request payload attempts.
- A user cannot read, update, or delete another user's todo by ID.
- Two users may use the same todo name if the rule is per-user uniqueness.
- Database uniqueness and foreign-key constraints reject invalid ownership.
- Token expiration and secret rotation behave as expected.

Use an isolated test database. Do not use the development or QA database for authentication tests.

## 13. Suggested implementation order

Follow this order to reduce rewrites:

1. Add dependencies and environment settings.
2. Add the user model and authentication schemas.
3. Add migrations for users and the todo ownership column.
4. Add password hashing and user repository operations.
5. Add token creation and validation utilities.
6. Add registration and login routes.
7. Add the current-user dependency.
8. Change todo schemas so ownership cannot be client supplied.
9. Thread the authenticated user through routes, services, and repositories.
10. Add owner filters to every todo operation.
11. Add response schemas and consistent error handling.
12. Add tests for authentication and cross-user isolation.
13. Run migrations and verify QA with a QA-only signing secret and database.
14. Deploy production with secret-manager-backed configuration and a migration step.

## 14. Operational notes

The Docker Compose Postgres service in this repository is suitable for local development. QA and production should use separate databases, credentials, volumes, and JWT secrets. If you do use Compose for QA, give it a separate project name and volume so it cannot accidentally reuse development data.

Use HTTPS in QA and production. Bearer tokens must not travel over plain HTTP outside local development. Add rate limiting and login monitoring before exposing the login endpoint publicly. Consider account lockout or progressive delays only after measuring the risk, because poorly designed lockouts can become a denial-of-service tool.

Finally, document how to rotate JWT secrets, disable a compromised user, revoke refresh tokens if they are introduced, back up the database, and recover from a failed migration. Authentication is complete only when those operational paths are understood, not merely when login returns a token.
