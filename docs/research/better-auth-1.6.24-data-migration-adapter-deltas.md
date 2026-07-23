# Better Auth 1.6.24 data, migration, and adapter delta audit

Date: 2026-07-23

Tracker:

- Child: [Audit Better Auth 1.6.24 data, migration, and adapter deltas](https://github.com/salasebas/rustauth/issues/213)
- Map: [Wayfinder: Better Auth 1.6.24 observable parity](https://github.com/salasebas/rustauth/issues/210)
- Next synthesis: [Reconcile the 1.6.24 delta with RustAuth implementation coverage](https://github.com/salasebas/rustauth/issues/216)

## Conclusion

Better Auth 1.6.10 through 1.6.24 contains material data-layer changes that RustAuth
cannot treat as release-note-only deltas. RustAuth already has strong storage
primitives and a shared SQL planner, so several upstream fixes are covered without a
line-for-line port. The remaining gaps are nevertheless observable:

1. OAuth authorization codes, magic links, password reset tokens, delete-account
   tokens, SIWE nonces, and database-backed SAML replay markers can still win more
   than once under the concurrency conditions fixed upstream.
2. OAuth refresh-token rotation is an unguarded read-then-update in RustAuth and can
   fork a token family. The refresh-token column is not unique, and three upstream
   foreign-key indexes are absent.
3. RustAuth's single-row `update` and `delete` mutate a row when no predicate is
   supplied. In SQLx MySQL and Diesel MySQL, a guarded update can also return a
   fabricated success after the write affected zero rows.
4. Better Auth's two-factor account lockout adds two persisted fields and explicitly
   requires a migration. RustAuth has neither the fields nor schema metadata capable
   of expressing the `0` default.
5. RustAuth's memory rate-limit store is unbounded and its SQL rate-limit tables are
   never pruned. Redis and Fred rate-limit scripts extend TTL on every request,
   unlike Better Auth's fixed-expiry Redis counter.
6. Redis and Fred secondary-storage `take` use `GETDEL` directly. Better Auth uses an
   atomic Lua fallback so single-use storage works on Redis versions before 6.2.
7. RustAuth plugin schemas cannot express Better Auth's `disableMigration` flag, and
   organization invitations cannot inherit database-generated or caller-supplied ID
   behavior.

These are specification inputs, not implementation in this artifact. The existing
reconciliation, divergence, migration-policy, and rollout tickets are sufficient
owners; no duplicate implementation tickets are needed.

## Scope and method

The audit compares the repository's declared Better Auth range:

- Better Auth 1.6.9 at commit
  [`f484269228b7eb8df0e2325e7d264bb8d7796311`](https://github.com/better-auth/better-auth/commit/f484269228b7eb8df0e2325e7d264bb8d7796311)
- Better Auth 1.6.24 at commit
  [`9a661c7b7abceaa81123b2c56757ee24f3ad2ed6`](https://github.com/better-auth/better-auth/commit/9a661c7b7abceaa81123b2c56757ee24f3ad2ed6)
- [Immutable upstream comparison](https://github.com/better-auth/better-auth/compare/f484269228b7eb8df0e2325e7d264bb8d7796311...9a661c7b7abceaa81123b2c56757ee24f3ad2ed6)

Both pinned repositories were fetched with
`./scripts/fetch-upstream-better-auth.sh` and inspected locally. Upstream changelogs,
implementation, tests, and migration snapshots were treated as primary sources.
RustAuth ownership was established from current source and tests, not crate names
alone.

The sibling
[Audit Better Auth 1.6.24 security and HTTP contract deltas](https://github.com/salasebas/rustauth/issues/214)
owns route shapes, error/status changes, and application-level SSO/SAML/SCIM,
password, OTP, OAuth/OIDC, and session behavior. This report repeats a flow only
when its observable difference is caused by a persisted-state race, adapter
contract, query shape, or migration requirement. For example, SCIM `active`,
deprovisioning, and account-linking rules use existing fields and belong to the
sibling audit; SAML assertion reservation appears here because its database and
secondary-storage atomicity differ.

Disposition vocabulary:

- **Covered**: current RustAuth behavior meets or exceeds the upstream observable
  contract.
- **Gap**: current behavior differs observably and must be implemented or accepted
  explicitly.
- **Partial**: the main behavior is present but an adapter, compatibility range, or
  failure mode remains.
- **Not applicable**: the upstream change is specific to a storage or generator
  surface RustAuth does not expose.

## Upstream delta ledger

### Atomic consume, guarded increment, and transactions

| Upstream delta | RustAuth evidence and disposition | Observable risk / owner |
| --- | --- | --- |
| Better Auth added `DBAdapter.consumeOne`, `internalAdapter.consumeVerificationValue`, and optional `SecondaryStorage.getAndDelete`; the first racer wins. Redis uses Lua for pre-6.2 compatibility. See [atomic verification consumption](https://github.com/better-auth/better-auth/pull/9568) and its [implementation commit](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a). | **Covered at the primitive level.** RustAuth's generic [`DbAdapter`](../../crates/rustauth-core/src/db/adapter/traits.rs) does not expose `consumeOne`, but [`VerificationStore::consume_verification_including_expired`](../../crates/rustauth-core/src/verification.rs) deletes by identifier and row ID and accepts only a positive affected-row count. [`SecondaryStorage::take`](../../crates/rustauth-core/src/options/storage.rs) is mandatory and atomic. | Call sites can obtain exact single-winner behavior without widening `DbAdapter`. Whether a generic consume method is desirable is an interface-design decision, not a parity prerequisite. Owner: `rustauth-core::verification`. |
| Magic links became single-use regardless of `allowedAttempts`; concurrent redemption can mint only one session. See [single-use magic links](https://github.com/better-auth/better-auth/pull/9572). | **Gap.** [`reserve_magic_link_attempt`](../../crates/rustauth-plugins/src/magic_link/endpoints.rs) increments an attempt value with compare-and-swap, then returns the payload. Unlimited attempts do not mutate storage; finite attempts deliberately permit more than one successful reservation. | Two requests can mint two sessions, and `allowedAttempts` still multiplies successful redemptions. All primary adapters and Redis/Fred secondary storage are affected. Owner: `rustauth-plugins::magic_link`. |
| OAuth authorization-code exchange atomically consumes the code and concurrent losers receive `invalid_grant`. See [atomic authorization-code redemption](https://github.com/better-auth/better-auth/commit/b4bc65a007784b2eb0efb459e5fa6fd8055d3ec9). | **Gap.** RustAuth's [token endpoint](../../crates/rustauth-oauth-provider/src/endpoints/token.rs) calls `find_verification` and then `delete_verification`. | Parallel exchanges can both mint tokens. This is security-sensitive and affects every primary adapter plus Redis/Fred. Owner: `rustauth-oauth-provider`. |
| Better Auth made password-reset, delete-account, one-time-token, phone/email OTP, device-code, two-factor challenge, SIWE nonce, and related verification flows single-winner in the [atomic counter and replay hardening change](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc). | **Mixed.** Device authorization uses guarded [`delete_many`](../../crates/rustauth-plugins/src/device_authorization/store.rs); one-time token, phone, and email OTP use verification consume/take; passkey and the final two-factor challenge use `take_verification`. **Gaps remain** in [password reset](../../crates/rustauth-core/src/api/services/password.rs), [delete account](../../crates/rustauth-core/src/api/services/user.rs), and [SIWE](../../crates/rustauth-plugins/src/siwe/endpoints.rs), which read and later delete. | The covered flows need cross-adapter regression retention. The three gaps can duplicate their protected side effect or session. Owners: `rustauth-core::api::services`, `rustauth-plugins::siwe`. |
| Concurrent SAML assertion replay is rejected. See the upstream [SAML replay protection release note](https://github.com/better-auth/better-auth/blob/9a661c7b7abceaa81123b2c56757ee24f3ad2ed6/packages/sso/CHANGELOG.md). | **Partial.** [`SsoStateStore::try_create`](../../crates/rustauth-sso/src/state.rs) uses atomic `set_if_not_exists` with secondary storage. Its database path serializes only through an in-process lock, then performs find-plus-create; the verification identifier is not unique. | Secondary Redis/Fred paths are covered. Two application processes sharing SQL can both accept the same assertion. All named primary adapters are affected. Owner: `rustauth-sso`. |
| A transaction-backed single-use flow no longer reacquires the pool and deadlocks with a one-connection pool. See [single-connection transaction fix](https://github.com/better-auth/better-auth/pull/10070). | **Covered.** [`DbVerificationStore::take_verification`](../../crates/rustauth-core/src/verification.rs) constructs the inner store from the transaction adapter passed to its callback, not the outer pool adapter. | Retain a one-connection regression test for the adapter matrix. This is especially relevant to `rustauth-deadpool-postgres` and SQLx pools. |
| Better Auth added `incrementOne` for guarded counters and state transitions across Kysely, Drizzle, Prisma, MongoDB, and memory. See [atomic counter implementation](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc). | **Partial by use case.** RustAuth has no generic increment primitive. Its `RateLimitStore::consume` contract is already atomic and each first-party store implements it. API-key database counters use an `updated_at` compare-and-swap. The MySQL runner can falsely report that guarded CAS as successful; pure secondary-storage API-key mode remains best-effort, which matches the upstream documented limitation. | Do not mechanically add `incrementOne`. Fix the guarded operations that need exact affected-row semantics, then decide in [Decide which RustAuth divergences may survive at Better Auth 1.6.24](https://github.com/salasebas/rustauth/issues/218) whether a generic primitive is worth the public adapter expansion. |

### Adapter query and mutation semantics

| Upstream delta | RustAuth evidence and disposition | Observable risk / owner |
| --- | --- | --- |
| `adapter.update` returns `null` when the predicate matches no row or when no predicate is supplied. Intentional bulk updates use `updateMany`. See [the shared update-contract fix](https://github.com/better-auth/better-auth/pull/10180). | **Gap.** [`Update::new`](../../crates/rustauth-core/src/db/adapter/query.rs) starts with an empty predicate. The shared [`SqlAdapterRunner::update`](../../crates/rustauth-core/src/db/sql/executor.rs) rejects empty data but not empty predicates. The memory adapter treats an empty predicate as matching every record and updates the first. | A mistakenly unguarded singular update mutates arbitrary data in every named SQL adapter and memory. Add a shared adapter-contract test and fail closed with `None`. Owner: `rustauth-core::db::adapter` and shared SQL executor. |
| Memory singular `delete` with an empty filter became a no-op; failed memory transactions no longer discard unrelated concurrent writes; `updateMany` reports its count. See [memory adapter hardening](https://github.com/better-auth/better-auth/blob/9a661c7b7abceaa81123b2c56757ee24f3ad2ed6/packages/memory-adapter/CHANGELOG.md). | **Gap / covered / gap.** RustAuth memory singular update/delete match the first row when predicates are empty; `update_many` already returns a count; transactions use `run_transaction_without_native_support` and therefore have no rollback snapshot semantics. | Test behavior differs from production SQL and can hide or invent failures. Owner: `rustauth-core::db::memory`. |
| Drizzle corrected mixed `AND`/`OR` grouping. See [mixed predicate grouping](https://github.com/better-auth/better-auth/pull/9756). | **Covered for SQL, partial for memory.** [`SqlDialect::where_clause`](../../crates/rustauth-core/src/db/sql/dialect.rs) emits all `AND` predicates plus one parenthesized `OR` group and has a focused test. [`MemoryAdapter::matches_where`](../../crates/rustauth-core/src/db/memory.rs) folds connectors sequentially and can disagree for mixed-order input. | Named SQL adapters have one shared, deterministic meaning. Memory parity needs either the same grouping or a deliberately documented query model. |
| Prisma guarded updates no longer surface `P2025`; MongoDB avoids an empty update document on older servers; native Mongo operations return the deleted/updated document. See [guarded adapter compatibility](https://github.com/better-auth/better-auth/pull/10086). | **Not applicable as ORM mechanics.** RustAuth exposes neither a Prisma nor MongoDB adapter. The equivalent observable contract is the `None`-on-miss requirement above. | Do not port ORM error handling. Validate shared RustAuth adapter results instead. |
| Kysely MySQL now checks matched rows for guarded updates, handles an `id` predicate in any position, and documents mysql2 `FOUND_ROWS` behavior. | **Gap in SQLx MySQL and Diesel MySQL.** The shared MySQL branch preselects a row, executes the guarded update, ignores the returned affected-row count, merges the proposed data into the preselected record, and returns `Some`. Both MySQL drivers already expose affected rows to the shared executor. | A concurrent guard change produces a false success. This breaks API-key CAS and any future refresh-token CAS. SQLx PostgreSQL/SQLite, Diesel PostgreSQL, Tokio PostgreSQL, and Deadpool PostgreSQL use `RETURNING` and correctly return `None`. Owner: shared SQL executor with MySQL contract tests in both MySQL crates. |
| Kysely and Drizzle made MySQL insert-return lookup robust when the database owns ID generation. See [MySQL insert-return hardening](https://github.com/better-auth/better-auth/pull/9665). | **Partial / mostly not applicable.** RustAuth returns PostgreSQL/SQLite generated IDs with `RETURNING`, MySQL serial IDs with `LAST_INSERT_ID`, and otherwise returns application-supplied input. It has no unsafe “last row” fallback. A MySQL plugin table configured for a non-serial database-generated ID would still return input without the generated ID. | Preserve the supported ID modes explicitly. If plugin tables gain database-owned UUID IDs, MySQL needs a defined return strategy or a fail-closed configuration error. Owner: shared SQL executor and schema ID policy. |
| Bundled Bun/Node SQLite introspectors stopped reporting tables as views and now report mutation metadata correctly. See [SQLite introspection](https://github.com/better-auth/better-auth/pull/9615) and the [atomic adapter change](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc). | **Not applicable.** RustAuth introspects through SQLx, Diesel, or PostgreSQL drivers and does not expose Kysely's Bun/Node dialects or SQL Server. | No RustAuth work. |

### Persisted schema and migration generation

| Upstream delta | RustAuth evidence and disposition | Observable risk / owner |
| --- | --- | --- |
| Two-factor account lockout is enabled by default and adds `failedVerificationCount` and `lockedUntil`; upstream explicitly instructs users to migrate. See [account-level two-factor lockout](https://github.com/better-auth/better-auth/pull/10240). | **Gap.** RustAuth's [two-factor schema](../../crates/rustauth-plugins/src/two_factor/schema.rs) contains only `id`, `secret`, `backup_codes`, `user_id`, and `verified`. [`DbField`](../../crates/rustauth-core/src/db/schema.rs) has no default-value metadata. | Every named SQL adapter needs an additive migration. Behavioral lockout also requires an atomic account-wide counter across TOTP, email OTP, and backup codes; that implementation belongs to the reconciliation and security work, not this report. |
| OAuth provider schema adds indexes to foreign-key fields and makes refresh-token `token` unique. See [foreign-key indexes](https://github.com/better-auth/better-auth/pull/9389) and [refresh-token rotation/schema hardening](https://github.com/better-auth/better-auth/commit/c6918ecc9e3a75892169415d7f6c95b591b6a52d). | **Partial.** RustAuth already indexes OAuth client `user_id`; refresh-token `client_id`/`user_id`; access-token `client_id`/`user_id`; and consent `client_id`/`user_id`. It is missing refresh-token `token` uniqueness, refresh-token `session_id`, access-token `session_id`, and access-token `refresh_id`. See [current OAuth schema](../../crates/rustauth-core/src/db/oauth_provider.rs). | Missing uniqueness weakens collision detection; missing indexes make session/family cleanup and joins degrade with table size. All named SQL migration generators are affected. |
| A field marked both `unique: true` and `index: true` no longer generates duplicate uniqueness/index declarations for new tables; indexes are emitted after tables. See [Kysely migration fix](https://github.com/better-auth/better-auth/pull/10357) and [Drizzle generator fix](https://github.com/better-auth/better-auth/pull/10333). | **Covered, and stronger for existing tables.** [`plan_schema_migration`](../../crates/rustauth-core/src/db/sql/migrations.rs) creates tables first, skips a second unique index for a newly created table, and creates an absent unique index on an existing table. | Changing OAuth refresh `token` to unique will enforce the constraint on existing RustAuth installs, unlike upstream's documented manual-migration caveat. The existing non-unique index may remain redundant because the planner is additive and does not drop it; the rollout must account for that. |
| SQLite `BIGINT` is recognized as numeric during migration diff. See [SQLite BIGINT migration compatibility](https://github.com/better-auth/better-auth/pull/10316). | **Covered.** [`SqlDialect::type_matches`](../../crates/rustauth-core/src/db/sql/dialect.rs) accepts SQLite `bigint` for number and boolean fields. | Retain the migration snapshot test; no adapter-specific work. |
| `disableMigration` is preserved for plugin tables in runtime migrations and Drizzle/Prisma generation. See [plugin migration suppression](https://github.com/better-auth/better-auth/pull/10198). | **Gap in extensibility, no current built-in data loss.** RustAuth's `DbTable` and `PluginSchemaContribution` have no suppression flag, so every contributed table is always considered by SQL planning. No upstream production schema in this range sets the flag; upstream coverage is currently synthetic/custom-plugin coverage. | A custom RustAuth plugin cannot own its table externally while still contributing runtime schema metadata. Decide whether parity requires this plugin contract before expanding public schema types. Owner: `rustauth-core::plugin`, schema, SQL planner, and CLI. |
| Upstream Drizzle generation fixes string escaping, array defaults, relation-name disambiguation, and fields that are both unique and indexed; Prisma generation fixes numeric type updates and output handling. | **Not applicable to RustAuth's SQL-only CLI output.** RustAuth does not emit Drizzle or Prisma source. Default metadata is independently relevant because the new two-factor count requires `0`, but the TypeScript emitter mechanics are not. | Do not add ORM code generators for parity. If schema defaults are added, test SQL DDL and migration output for all RustAuth dialects. |

### Model names, field input, organization queries, and IDs

| Upstream delta | RustAuth evidence and disposition | Observable risk / owner |
| --- | --- | --- |
| Exact schema keys now win over physical `modelName` aliases, and foreign-key/join resolution uses canonical user ownership. See [foreign-key and join collision fix](https://github.com/better-auth/better-auth/pull/10235) and [exact schema-key resolution](https://github.com/better-auth/better-auth/pull/10302). | **Covered by a different representation.** [`DbSchema::resolve_table`](../../crates/rustauth-core/src/db/schema.rs) checks the logical key before scanning physical names; plugin insertion rejects conflicting physical fields. Foreign keys are resolved from explicit schema metadata. | Add/retain collision regression tests, but no port is required. |
| OAuth profile mapping no longer persists values for additional user fields marked `input: false`; schema defaults still apply. See [provider profile input filtering](https://github.com/better-auth/better-auth/pull/10196). | **Not applicable to the same surface.** RustAuth's provider user-info contract exposes fixed core profile fields rather than a free-form `mapProfileToUser` additional-field map. API additional fields are already filtered through RustAuth's input schema. | If a free-form provider profile map is added later, it must pass through the same input policy. Current SQL adapters have no delta. |
| `/update-session` rejects plugin-owned `activeOrganizationId`, `activeTeamId`, and `impersonatedBy` input. See [plugin-owned session input hardening](https://github.com/better-auth/better-auth/pull/9965). | **Covered for organization, partial for admin.** The organization plugin registers both active fields as generated [`SessionAdditionalField`](../../crates/rustauth-plugins/src/organization/mod.rs), so [`update_session_fields`](../../crates/rustauth-core/src/api/services/session.rs) rejects them. Admin's [`impersonated_by` schema field](../../crates/rustauth-plugins/src/admin/schema.rs) remains input-enabled metadata and is not registered in the runtime session field map. A request containing only that field still gets a 400 because no update remains, but a request combining it with a valid field succeeds while silently ignoring it instead of rejecting the entire request. | No unauthorized admin value is currently persisted, but the HTTP/input contract is observably weaker and the schema metadata is unsafe for future generic consumers. Owner: admin plugin runtime-field registration plus the HTTP-contract sibling audit. |
| Organization `listMembers` applies the member limit to the joined user query so organizations over roughly 100 members do not fail. See [large organization member listing](https://github.com/better-auth/better-auth/pull/10342). | **Not applicable to the current query shape.** RustAuth's organization listing returns member records and does not perform the separate, capped user lookup that failed upstream. | No adapter work. A future joined-user response needs a cardinality test above 100. |
| Organization invitation IDs honor a caller value and can be generated by the database when global ID policy delegates generation. See [organization invitation ID policy](https://github.com/better-auth/better-auth/pull/10040). | **Gap.** RustAuth [creates invitation IDs in application code](../../crates/rustauth-plugins/src/organization/store/mod.rs), and plugin table IDs do not inherit the global `IdPolicy`. Hook input has no caller-supplied ID field. | Observable record IDs diverge under serial/database UUID policy. This affects all named SQL adapters if parity is chosen. Owner: organization plugin schema/store and core plugin ID policy. |
| OAuth-created and updated email addresses are normalized before persistence. | **Covered.** RustAuth normalizes OAuth account-linking email and normalizes user create/update paths. | Retain persistence tests through one representative SQL adapter; no migration. |

## Exact schema and migration ledger

The execution plan must treat the following as the complete persisted schema delta
found in this audit.

| Model | Logical field | Required target | Current RustAuth | Migration consequence |
| --- | --- | --- | --- | --- |
| `two_factor` | `failed_verification_count` | Optional number, default `0`, input false, returned false | Missing; defaults cannot be represented | Add a nullable integer/BIGINT-compatible column with database default `0`, or add it nullable and make all reads treat `NULL` as `0` while backfilling. The chosen path must be consistent across PostgreSQL, MySQL, and SQLite. |
| `two_factor` | `locked_until` | Optional timestamp, input false, returned false | Missing | Add nullable timestamp. |
| `oauth_refresh_token` | `token` | Unique, hidden | Hidden ordinary index | Add uniqueness after a preflight duplicate check. The additive planner can create the unique index on existing tables but will not remove the redundant ordinary index. |
| `oauth_refresh_token` | `session_id` | Indexed nullable foreign key | Foreign key, not indexed | Add ordinary index. |
| `oauth_access_token` | `session_id` | Indexed nullable foreign key | Foreign key, not indexed | Add ordinary index. |
| `oauth_access_token` | `refresh_id` | Indexed nullable foreign key | Foreign key, not indexed | Add ordinary index. |

No table or column rename was found in this range. The model-name changes are lookup
semantics, not physical renames. No destructive migration is required by upstream,
but adding refresh-token uniqueness can fail on existing duplicate data and therefore
needs release-policy treatment in
[Choose release and migration policy for parity-breaking changes](https://github.com/salasebas/rustauth/issues/219).

## Adapter-by-adapter audit

### `rustauth-sqlx`

All three SQLx dialects use the shared `SqlAdapterRunner` and additive migration
planner.

- **PostgreSQL:** atomic SQL rate-limit consumption and `UPDATE ... RETURNING`
  miss detection are covered. It still inherits unguarded single-row operations,
  missing flow-level consumes, missing schema fields/indexes, and rate-limit row
  retention.
- **SQLite:** same shared gaps. SQLite `BIGINT` migration matching and returned-row
  writes are already covered.
- **MySQL:** same shared gaps plus the false-success guarded-update failure. Its
  driver exposes `rows_affected`, so the shared runner can distinguish a lost CAS
  without an ORM workaround. Serial insert IDs are covered by `LAST_INSERT_ID`.

Required adapter tests: empty-predicate update/delete, guarded update lost race,
refresh-token CAS lost race, API-key CAS lost race, schema generation for the six
ledger entries, and SQL rate-limit cleanup.

### `rustauth-diesel`

Diesel PostgreSQL and MySQL also delegate CRUD and migration planning to the shared
runner.

- **PostgreSQL:** the same shared gaps as SQLx PostgreSQL.
- **MySQL:** the same false-success guarded-update failure as SQLx MySQL; Diesel
  already returns the execute count to `SqlExecutor`.

Required adapter tests mirror SQLx for both dialects. The MySQL test must be live or
transactionally orchestrated so a predicate changes after preselect and before
update; an in-memory harness cannot expose the bug.

### `rustauth-tokio-postgres`

The adapter delegates CRUD to the shared PostgreSQL runner and has a dedicated
transactional rate-limit store. `RETURNING` miss behavior is covered. It inherits all
shared call-site, schema, migration-suppression, empty-predicate, and SQL cleanup
gaps. Its single-connection transaction path should be part of the verification
regression suite.

### `rustauth-deadpool-postgres`

Deadpool wraps the same Tokio PostgreSQL driver semantics with pooled transaction
ownership. It inherits the PostgreSQL gaps above. It is the highest-value adapter for
the one-connection no-deadlock regression because the upstream failure was pool
reacquisition inside a transaction.

### `rustauth-redis`

- The dedicated rate-limit store is atomic Lua, so concurrent requests cannot pass
  the counter through a read/write race.
- Its script refreshes `PEXPIRE` on every denied or allowed request. Better Auth's
  Redis `increment` sets expiry only when the counter is created; RustAuth therefore
  has a different window lifetime and retry behavior under sustained traffic.
- `SecondaryStorage::take` sends `GETDEL` directly. Redis before 6.2 returns an
  unknown-command error rather than performing Better Auth's atomic Lua fallback.
- `set_if_not_exists`, compare-and-set, and conditional delete are atomic Lua/native
  operations and meet the stronger RustAuth secondary-storage contract.
- API-key secondary-only counters are best-effort, matching Better Auth's explicit
  limitation. With database fallback they inherit the selected primary adapter,
  including the MySQL false-success gap.

### `rustauth-fred`

Fred has the same observable results as `rustauth-redis`: atomic Lua rate-limit
decisions, sliding TTL extension instead of upstream fixed expiry, direct `GETDEL`
without a pre-6.2 fallback, atomic secondary CAS operations, and best-effort
secondary-only API-key counters.

### Memory adapter

Although not named as a production SQL/secondary adapter in the ticket, memory is
part of the adapter contract and is used heavily in parity tests. It is unbounded,
has sequential mixed-connector evaluation that can differ from SQL grouping,
changes the first row for empty-predicate singular update/delete, and lacks rollback
isolation. `update_many` counts rows correctly and individual operations are
serialized by its mutex.

## Rate-limit storage reconciliation

The Better Auth atomic counter change has four independent requirements; treating it
as one “rate limiting is atomic” checkbox would miss three RustAuth deltas.

| Requirement | RustAuth status |
| --- | --- |
| Check-and-increment is one atomic decision | **Covered** by required `RateLimitStore::consume` in memory, every SQL store, Redis, and Fred. The legacy `RateLimitStorage` compatibility adapter remains non-atomic and documents that limitation, analogous to upstream's best-effort custom-storage fallback, but RustAuth does not emit upstream's one-time runtime warning. |
| No bypass when trusted client IP is absent | **Covered / stronger option set.** `MissingIpPolicy` defaults to deny and also offers an explicit shared bucket or legacy allow policy. |
| In-memory storage is bounded | **Gap.** Better Auth caps at 100,000 entries and evicts expired/old entries. RustAuth only performs periodic expiry cleanup and has no hard ceiling. |
| Database storage removes expired entries | **Gap.** RustAuth reuses a row when the same key returns, but never deletes dormant keys. All SQL rate-limit stores grow with distinct keys. |
| Redis secondary counter expiry is fixed from window creation | **Gap.** Redis and Fred refresh TTL on every request. |

The rollout must specify whether Redis/Fred adopt Better Auth's fixed window exactly
or whether their current rolling window is an accepted divergence. That decision
belongs to
[Decide which RustAuth divergences may survive at Better Auth 1.6.24](https://github.com/salasebas/rustauth/issues/218).

## Execution-ready handoff

[Reconcile the 1.6.24 delta with RustAuth implementation coverage](https://github.com/salasebas/rustauth/issues/216)
should convert this evidence into the following coherent work packages:

1. **Atomic single-use consumers.** Replace read-then-delete in OAuth authorization
   code, magic link, password reset, delete account, and SIWE. Make SQL-backed SAML
   assertion reservation cross-process atomic. Acceptance: two synchronized requests
   produce exactly one protected side effect for memory, each named primary adapter,
   and Redis/Fred where secondary storage applies.
2. **OAuth refresh rotation and schema.** Guard parent revocation on row ID plus
   `revoked IS NULL`, require a positive affected-row result before minting, add
   refresh-token uniqueness and the three missing indexes, and test collision,
   rotation, revocation, and family invalidation. Acceptance: exactly one concurrent
   rotation wins on every primary adapter.
3. **Shared adapter mutation contract.** Make singular update/delete with an empty
   predicate a no-op and make MySQL return `None` on a guarded miss. Align memory
   mixed predicate grouping and transaction semantics or record an explicit
   divergence. Acceptance: one shared contract suite plus live SQLx/Diesel MySQL
   regressions.
4. **Two-factor lockout persistence.** Add the two fields, default/null semantics,
   additive migration output, existing-row behavior, and atomic counter behavior.
   Acceptance: generated and executed migrations for PostgreSQL, MySQL, and SQLite,
   including an existing row with `NULL` count.
5. **Rate-limit lifecycle.** Cap memory storage, prune SQL rows, choose and implement
   Redis/Fred window semantics, and decide whether legacy custom storage needs a
   runtime warning. Acceptance: concurrency, sustained-traffic expiry, and distinct-key
   growth tests for every store.
6. **Secondary-storage compatibility.** Either add an atomic Lua fallback for
   `take` or declare and enforce Redis 6.2+ as the minimum for both Redis and Fred.
   Acceptance: exactly-one `take` on the declared oldest supported Redis/Valkey.
7. **Plugin schema policy.** Decide `disableMigration`, schema defaults, and plugin
   ID inheritance/caller ID support before changing public types. Acceptance: custom
   plugin migration suppression and organization invitation ID tests if parity is
   selected.

Migration sequencing, duplicate refresh-token preflight, index naming, and release
communication belong to
[Choose release and migration policy for parity-breaking changes](https://github.com/salasebas/rustauth/issues/219).
The final cross-crate order and test matrix belong to
[Design the executable Better Auth 1.6.24 parity rollout](https://github.com/salasebas/rustauth/issues/220).

## Verification checklist for the eventual parity claim

- Run the shared CRUD contract against memory and every dialect in
  `rustauth-sqlx`, `rustauth-diesel`, `rustauth-tokio-postgres`, and
  `rustauth-deadpool-postgres`.
- Run synchronized two-request tests for each single-use flow and OAuth refresh
  rotation; a serial “second use fails” test is insufficient.
- Generate migrations from a 1.6.9-compatible schema snapshot and execute them
  against non-empty PostgreSQL, MySQL, and SQLite databases.
- Seed a duplicate OAuth refresh-token value and prove the migration fails with an
  actionable preflight rather than partially applying.
- Exercise Redis and Fred against the oldest declared Redis/Valkey version, including
  `take`, fixed-window expiration, API-key secondary-only behavior, and rate-limit
  concurrency.
- Prove rate-limit memory and SQL stores remain bounded under many distinct keys.
- Keep ORM-specific Better Auth changes marked not applicable; do not claim Drizzle,
  Prisma, MongoDB, Bun SQLite, Node SQLite, MSSQL, or ORM source-generation support
  through the RustAuth SQL adapter evidence.

No RustAuth parity behavior was implemented as part of this audit.
