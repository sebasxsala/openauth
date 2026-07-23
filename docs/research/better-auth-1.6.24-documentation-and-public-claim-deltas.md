# Better Auth 1.6.24 documentation and public-claim audit

## Resolution

This report resolves
[Audit Better Auth 1.6.24 documentation and public claim deltas](https://github.com/salasebas/rustauth/issues/215),
a research child of
[Wayfinder: Better Auth 1.6.24 observable parity](https://github.com/salasebas/rustauth/issues/210).

**Decision: changing only `1.6.9` to `1.6.24` would make RustAuth's public
compatibility claims false or materially incomplete.** Better Auth 1.6.24
documents new observable HTTP, security, cookie, storage, migration, provider,
plugin, error, CLI, and example behavior. RustAuth's production documentation
must not claim 1.6.24 parity until the owning implementation tickets accept,
implement, or explicitly reject those behaviors.

This is the requested single research artifact. It deliberately does not change
any production README, `UPSTREAM.md`, reference pin, public guide, example, CLI
help, or changelog.

## Evidence and method

The comparison used the repository's pinned-source workflow and the official
Better Auth tags:

| Baseline | Official tag | Commit |
| --- | --- | --- |
| Current RustAuth reference | [`v1.6.9`](https://github.com/better-auth/better-auth/tree/v1.6.9) | [`f484269228b7eb8df0e2325e7d264bb8d7796311`](https://github.com/better-auth/better-auth/commit/f484269228b7eb8df0e2325e7d264bb8d7796311) |
| Audit target | [`v1.6.24`](https://github.com/better-auth/better-auth/tree/v1.6.24) | [`9a661c7b7abceaa81123b2c56757ee24f3ad2ed6`](https://github.com/better-auth/better-auth/commit/9a661c7b7abceaa81123b2c56757ee24f3ad2ed6) |

The authoritative source delta is
[`v1.6.9...v1.6.24`](https://github.com/better-auth/better-auth/compare/v1.6.9...v1.6.24).
The tagged `docs/content/docs` trees contain 73 changed files, with 2,128
insertions and 416 deletions. The audit also read tagged package changelogs,
public type/configuration sources, relevant demos, and every RustAuth surface
named in the research ticket.

The upstream root README did not change, and no public package README that maps
to a RustAuth crate changed. The only new upstream package README is an internal
OAuth popup implementation note. Therefore the significant upstream public
claim evidence is in the tagged documentation, changelogs, types, and examples,
not in README prose.

The new
[`1.7 upgrade guide`](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/guides/1-7-upgrade-guide.mdx)
describes a future release and is out of scope for a 1.6.24 parity claim.
Community and infrastructure pages, third-party migration guides, and
client-only UI changes are also outside RustAuth's declared server-side parity
surface unless a later implementation ticket adopts them.

## Upstream documentation deltas that affect RustAuth

### Core HTTP, security, cookies, and public options

| Tagged upstream evidence | Observable/public delta | RustAuth claims that must be revalidated |
| --- | --- | --- |
| [Rate limiting](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/concepts/rate-limit.mdx), [core changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/CHANGELOG.md) | Multi-hop `X-Forwarded-For` is not trusted by default; `trustedProxies` is explicit; `ipAddressHeaders` should name a trusted single-IP header; IPv6 grouping defaults to `/64`, with prefixes from 0 through 128. Rate limiting runs before plugin handlers. | `rustauth-core`, framework adapters, Redis/Fred stores, the public rate-limit guide, `examples/full-app`, HTTP conventions, and deployment guidance. Existing “high”/“complete” claims do not account for these contracts. |
| [Security](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/reference/security.mdx) | When `Origin` or `Referer` is present it is validated even for cookieless requests. Only requests lacking Fetch Metadata *and* origin/referrer fall through as non-browser traffic. Form-encoded routes depend on additional safeguards. OAuth token, refresh, introspection, and JWKS fetches do not follow redirects. | `docs-site` currently says origin validation is the fallback only when cookies are present; that statement is stale. Revalidate core CSRF/origin handling, OAuth/OIDC clients, framework bridges, HTTP docs, and security claims. |
| [Core changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/CHANGELOG.md) | Magic-link and email-OTP send endpoints force origin validation even without cookies. `get-session` returns `Cache-Control: no-store`. Requests mounted at the auth root but outside `basePath` return 404. | Core route contracts, response headers, framework adapters, magic-link/email-OTP docs, HTTP conventions, and route tests. |
| [Cookies](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/concepts/cookies.mdx), [session management](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/concepts/session-management.mdx) | The correct option is `advanced.cookies`. Account cookies store encrypted provider tokens. Refreshed `Set-Cookie` must reach the caller. Oversized session/account cookies are chunked; a database remains the durability recommendation. | Core cookie/session docs, framework response bridges, public options, stateless-session claims, and examples. |
| [Options](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/reference/options.mdx) | Documents `storeStateStrategy`, `disableImplicitLinking`, `updateUserInfoOnLink`, `trustedProxies`, revised IP headers, request context for `verifyIdToken`, and account-cookie behavior. State-storage defaults depend on configured storage. | `docs-site` options, core builders/config types, OAuth/social-provider options, and all “mapped configuration” claims. |
| [Error index](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/reference/errors/index.mdx), [`state_invalid`](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/reference/errors/state_invalid.mdx) | Adds `state_invalid` for state-cookie decryption/parsing failures and removes `please_restart_the_process`. | RustAuth's public error index has no `state_invalid` page and says `please_restart_the_process` is a future parity gap. A pin-only bump would make both claims false. |

### Accounts, OAuth, and social providers

| Tagged upstream evidence | Observable/public delta | RustAuth claims that must be revalidated |
| --- | --- | --- |
| [Database fields](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/concepts/database.mdx), [OAuth](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/concepts/oauth.mdx) | Additional-field `input` rules apply to API input and `mapProfileToUser`; `returned` is independent. Provider-mapped values for `input: false` are ignored, making those fields server-owned. | Core additional-field parsing, social profile mapping, public schema/options docs, and the docs-site additional-fields page. |
| [Users and accounts](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/concepts/users-accounts.mdx), [`account_not_linked`](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/reference/errors/account_not_linked.mdx) | `disableImplicitLinking` is public. `updateUserInfoOnLink` never changes email or `emailVerified`. Existing local users must be email-verified for the documented account-linking path; the deprecated compatibility option defaults to the safe behavior. | Core account linking, OAuth, social providers, options, error docs, and security claims. |
| [Email/password](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/authentication/email-password.mdx) | `revokeSessionsOnPasswordReset` is documented and defaults to false. | Password-reset behavior, session docs, config/API docs, and examples. |
| [Google](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/authentication/google.mdx), [One Tap](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/one-tap.mdx) | Hosted-domain (`hd`) enforcement includes wildcard handling and applies to One Tap. | Social-provider configuration, backend-reference example, Google guide, and One Tap plugin docs. |
| [Apple](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/authentication/apple.mdx) | Supports dynamic async provider config/JWT secret generation, multiple audiences, and a context-aware custom `verifyIdToken` that fully replaces built-in verification; the release also hardened Apple nonce verification. | Social-provider config and verification claims, OAuth/OIDC validation, backend-reference example, and Apple guide. |
| [Cognito](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/authentication/cognito.mdx) | Documents refresh-token callback/refresh behavior and forwarding the account cookie. | Social-provider token refresh, session/cookie bridge behavior, and Cognito docs/example. |
| [Microsoft](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/authentication/microsoft.mdx), [core changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/CHANGELOG.md) | Documents the large base64 profile image and includes tenant-restriction hardening. Other tagged provider deltas cover PayPal verification, Google hosted-domain checks, remote audience handling, and safer placeholder-email behavior. | Provider-specific public config and behavior, social-provider parity inventory, profile normalization, backend-reference example, and security notes. |
| [Generic OAuth](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/generic-oauth.mdx) | Adds the Yandex helper and `accessTokenExpiresIn`. | Generic OAuth plugin types, reference docs, and the plugin parity matrix. |

### Plugins

| Tagged upstream evidence | Observable/public delta | RustAuth claims that must be revalidated |
| --- | --- | --- |
| [Two-factor authentication](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/2fa.mdx), [core changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/CHANGELOG.md) | Credential-only enforcement is scoped; intermediate session lookup may be null. Account-level lockout defaults to 10 failures across factors for 15 minutes and returns 429 `ACCOUNT_TEMPORARILY_LOCKED`; challenge lockout occurs after 5 failures with `TOO_MANY_ATTEMPTS_REQUEST_NEW_CODE`. New `failedVerificationCount` and `lockedUntil` fields require migration. | Plugin behavior/errors, core rate limiting/session flow, schema snapshots, migration docs, CLI schema output, `examples/cli-migrate-playground`, and plugin docs. |
| [Device authorization](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/device-authorization.mdx) | Optional server-only `user_id` prebinding is documented. Fetching a device request claims it for the current session, which must also approve or deny it. | Device authorization routes, authorization checks, types, errors, and public plugin guide. |
| [Email OTP](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/email-otp.mdx), [magic link](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/magic-link.mdx) | Verifying an existing unverified-email account can clear its password and revoke sessions. Magic-link `allowedAttempts` is deprecated/ignored; links are atomically one-use and retry with `INVALID_TOKEN`. Multi-instance secondary storage requires atomic get-and-delete. | Email OTP/magic-link behavior, core session/password behavior, error/status docs, Redis/Fred contracts, and plugin guides. |
| [API key advanced usage](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/api-key/advanced.mdx), [API key changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/api-key/CHANGELOG.md) | Verification resolves the key's own `configId`; organization-owned key creation requires authorized user context. Tagged fixes add 429 rate-limit behavior, atomic concurrency counters, and authoritative session checks. | API-key route authorization, storage atomics, HTTP errors, options, and advanced guide. |
| [Last login method](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/last-login-method.mdx) | Adds the `beforeStoreCookie` consent hook and requires the client domain for cross-subdomain use. | Hook signatures, cookie policy, client/server docs boundary, and plugin guide. |
| [OAuth proxy](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/oauth-proxy.mdx) | Recommends a shared dedicated secret and expands state-mismatch troubleshooting. | OAuth proxy configuration, state errors, secrets guidance, and deployment docs. |
| [OAuth provider](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/oauth-provider.mdx), [package changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/oauth-provider/CHANGELOG.md) | Well-known routes are served automatically with direct/path-prefixed issuer aliases; signed query behavior is specified. Tagged fixes cover POST userinfo, per-client grants, signed-query ordering, Basic secrets containing colons, and redirect validation. | `rustauth-oauth-provider` route inventory, issuer/metadata behavior, client authentication, grants, errors, and public guide. |
| [Organization](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/organization.mdx), [package changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/organization/CHANGELOG.md) | Organization logo is nullable; deletion hooks receive endpoint context; invitation verification and current-state rules changed; active team must belong to the active organization. | Organization types/schema, hooks, authorization, invitation errors, active-team behavior, and plugin docs. |
| [Passkey](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/passkey.mdx), [package changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/passkey/CHANGELOG.md) | Adds AAGUID labeling and documents the verification callback name; tagged behavior changes make challenges one-time and revise failure statuses. | `rustauth-passkey` challenge consumption, callback API, response statuses, metadata, and public guide. |
| [SCIM](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/scim.mdx), [package changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/scim/CHANGELOG.md) | Command examples use the current CLI. Organization deletion deprovisions rather than globally deleting; `active` maps to disabled/ban state and session revocation; email changes reset verification. Tagged options include existing-user linking and deprovision rules. | `rustauth-scim` intentionally extends/deviates from upstream, so its behavior and `deprovision_mode` must be dispositioned explicitly rather than copied. Revalidate CLI snippets, session revocation, email verification, and SCIM guide. |
| [SIWE](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/siwe.mdx) | Documents strict ERC-4361 field/time binding and clarifies that email does not prove wallet ownership. | SIWE parser/validation, account-linking policy, security guide, and plugin docs. |
| [SSO](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/sso.mdx), [SSO changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/sso/CHANGELOG.md) | Rejects provider-ID namespace collisions; tightens organization role/domain registration; documents multiple domain verification, SAML Audience/Recipient/Destination, and IdP-initiated callback configuration. Tagged fixes cover redirect/private-host hardening, replay, and SLO. | `rustauth-sso`, `rustauth-saml`, `rustauth-oidc`, route/schema inventories, security/errors, and SSO/SAML guides. |
| [Stripe](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/stripe.mdx), [Stripe changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/stripe/CHANGELOG.md) | Subscription callbacks expose `stripeSubscription`; user deletion handling is documented. Tagged fixes validate `returnUrl` and target the correct subscription row. | `rustauth-stripe` callback types, deletion hooks, redirect validation, storage behavior, and guide. |
| [Admin](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/admin.mdx) | Setting a password creates a credential account; the documented permission inventory expanded. | Admin route semantics, credential-account storage, permissions, and guide. |

The new
[`commet` page](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/plugins/commet.mdx)
describes a community plugin, not an official mapped Better Auth server package. It
must not silently expand RustAuth's declared official-plugin parity surface.

### Storage adapters, migrations, and CLI

| Tagged upstream evidence | Observable/public delta | RustAuth claims that must be revalidated |
| --- | --- | --- |
| [Create an adapter](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/guides/create-a-db-adapter.mdx), [core changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/CHANGELOG.md) | Corrects adapter method signatures/returns; documents optional atomic `consumeOne`, `findMany.select`, `supportsUUIDs`, and `supportsArrays`; removes the old `supportsJoin` description. Tagged public storage work also adds atomic counters/increment operations and get-and-delete capabilities. | Core adapter traits, SQL and secondary-storage crates, plugin atomics, adapter test suites, UPSTREAM inventories, and public adapter docs. |
| [Drizzle adapter](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/adapters/drizzle.mdx) | Package import moved to `@better-auth/drizzle-adapter`; multiple foreign keys to the same table require matching `relationName` values with plural relation naming. | TypeScript package/import details are out of Rust scope, but relation naming, schema generation, and migration representation require a CLI/schema disposition. |
| [MySQL adapter](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/adapters/mysql.mdx), [Kysely changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/kysely-adapter/CHANGELOG.md) | Kysely depends on MySQL “rows matched”/`CLIENT_FOUND_ROWS`; disabling it breaks idempotent update, update-many, and increment semantics. Tagged changes also define no-match update results, mutation row counts, atomic counters, and native consumption. | `rustauth-sqlx`, `rustauth-diesel`, SQL adapter contracts/tests, MySQL deployment guidance, and migration behavior. |
| [CLI](https://github.com/better-auth/better-auth/blob/v1.6.24/docs/content/docs/concepts/cli.mdx), [CLI changelog](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/cli/CHANGELOG.md) | Upstream CLI now resolves tsconfig aliases and framework virtual modules. Tagged schema/migration changes include missing generated imports, Svelte stubs, Drizzle relation/unique/index metadata, quoted defaults, `disableMigration`, directory output, array defaults, and init configuration fixes. | RustAuth intentionally uses static TOML, so TypeScript loader behavior remains not applicable. `rustauth-cli` still must re-audit its “High” and “Complete” server SQL workflow claims, generated schema/migration behavior, README, docs-site CLI guide, and migration example. |
| [Core and adapter changelogs](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/CHANGELOG.md) | Two-factor fields require migration; plugin tables honor `disableMigration`; SQLite BIGINT diffing and unique/index generation changed. | Database migration guide, all SQL adapters, CLI generator, migration snapshots, and `examples/cli-migrate-playground`. |

The RustAuth binary's generated help currently says only “Command-line tools
for RustAuth” and contains no Better Auth version promise. No help-text edit is
required solely for the pin. Help output should change only if an implementation
ticket adds or changes flags; the stale compatibility claims are in the CLI
README, `UPSTREAM.md`, and docs-site guide.

### Official examples

Most upstream demo changes are dependency or client churn and create no
RustAuth server-documentation obligation. One relevant security example did
change:

- The tagged Next.js and Expo demos replaced a production
  `trustedOrigins: ["exp://"]` entry with the app-specific
  `better-auth://` scheme. The Expo example explains that the plugin adds the
  broad development scheme only in development because trusting it in
  production could leak a session cookie to an uncontrolled deep link.
- The stateless demo changes are dependency-version updates only.

RustAuth should carry the narrow-origin lesson into any native/deep-link
example it later publishes, but this does not justify changing unrelated
server examples now.

## RustAuth public-claim audit

### Pin, parity index, READMEs, and changelogs

| RustAuth surface | Current claim | Impact of changing only the version |
| --- | --- | --- |
| `reference/upstream-better-auth/VERSION.md` | Identifies tag, exact commit, checkout path, and capture date for 1.6.9. | Every provenance field would be incomplete or false unless updated together after the behavior audit. |
| `reference/upstream-better-auth/NOTICE.md` | Attributes the bundled reference to 1.6.9. | Must move with the pin/provenance update, not through a global string replacement. |
| `docs/parity/README.md` | Says the workspace tracks 1.6.9, enumerates the mapped crates, and hardcodes the 1.6.9 source path. | The version/path can change only after each owner document records the 1.6.24 disposition. The crate list itself must also be rechecked against the map's final scope. |
| 22 crate READMEs | Claim their crate is “aligned with” or “mapped against” Better Auth 1.6.9. | Replacing the version would assert compatibility before the documented deltas are implemented or rejected. `crates/rustauth-diesel/README.md` is the lone crate README without that blurb, although its `UPSTREAM.md` is pinned. |
| Root README | Links to the parity pin but does not state an exact Better Auth version. | The link remains correct; no version edit is needed. Its broad feature claims should change only if implementation behavior changes. |
| Root `CHANGELOG.md` and `crates/rustauth-cli/CHANGELOG.md` | Historical 0.2.0 entries say that release targeted 1.6.9. | These are immutable release history and **must remain 1.6.9**. A later production pin needs a new Unreleased/release entry, not historical rewriting. |

The 22 README compatibility blurbs are in:

`rustauth-actix-web`, `rustauth-axum`, `rustauth-cli`, `rustauth-core`,
`rustauth-deadpool-postgres`, `rustauth-fred`, `rustauth-i18n`,
`rustauth-oauth-provider`, `rustauth-oauth`, `rustauth-oidc`,
`rustauth-passkey`, `rustauth-plugins`, `rustauth-redis`, `rustauth-saml`,
`rustauth-scim`, `rustauth-social-providers`, `rustauth-sqlx`, `rustauth-sso`,
`rustauth-stripe`, `rustauth-telemetry`, `rustauth-tokio-postgres`, and the
`rustauth` facade.

### Every crate `UPSTREAM.md`

All 23 crate mapping documents hardcode 1.6.9. Their version, source path,
inventory counts, status, and gap statements must be re-audited together:

| Owner documents | 1.6.24 evidence they must absorb |
| --- | --- |
| `rustauth-core`, `rustauth`, `rustauth-axum`, `rustauth-actix-web` | Origin/Fetch Metadata rules, forced-origin send routes, `no-store`, root/basePath 404 behavior, rate-limit ordering and IP trust, cookie chunking/forwarding, account fields/linking, new options, and error catalog. Core's “G1-G15 closed” and “Complete” claims cannot survive a pin-only edit. |
| `rustauth-cli` | Schema/migration deltas, two-factor fields, `disableMigration`, relation/index/default handling, output semantics, and an explicit explanation that TypeScript config-loader work is not applicable. Its “High” and “Complete” claims need new evidence. |
| `rustauth-sqlx`, `rustauth-diesel`, `rustauth-deadpool-postgres`, `rustauth-tokio-postgres` | Adapter signatures/returns/capabilities, mutation counts, atomic operations, MySQL matched-row semantics, SQLite BIGINT diffs, indexes, and migrations. |
| `rustauth-redis`, `rustauth-fred` | Atomic get-and-delete/consume, increments, magic-link one-use behavior, API-key concurrency, and rate-limit atomicity. |
| `rustauth-oauth`, `rustauth-social-providers` | No-follow outbound HTTP, account linking/additional fields, context-aware token verification, provider-specific verification/configuration, token refresh, and account cookies. Social providers' “all in-scope gaps resolved” statement needs a new inventory. |
| `rustauth-oidc`, `rustauth-sso`, `rustauth-saml` | Issuer/audience/recipient/destination rules, namespaces, domain verification, organization authorization, IdP-initiated callbacks, replay, private-host/redirect hardening, and SLO. |
| `rustauth-oauth-provider` | Metadata aliases/path prefixes, userinfo method, client grants/authentication, signed query ordering, and redirect validation. |
| `rustauth-plugins` | Two-factor lockout/schema, device ownership, email/magic-link behavior, API keys, organization, SIWE, admin, last-login method, and other mapped plugin changes. A broad “High” label is not evidence for the new contracts. |
| `rustauth-passkey` | One-time challenges, verification callback/API, AAGUID metadata, and error statuses. |
| `rustauth-scim` | Existing-user linking, organization deprovisioning, active/disabled state, email verification, and session revocation, while preserving documented RustAuth extensions as explicit divergences. |
| `rustauth-stripe` | Callback payload, user deletion, return URL validation, and correct subscription-row targeting. |
| `rustauth-i18n` | The tagged i18n documentation/changelog delta and fallback behavior must be classified before retaining “Complete.” |
| `rustauth-telemetry` | No mapped 1.6.24 semantic documentation delta was found beyond dependency/changelog churn, but the pinned file paths, inventory, and high-parity claim still require an explicit no-change disposition. |

The test mapping document
`crates/rustauth-oauth-provider/tests/upstream_mapping.md` also hardcodes 1.6.9.
It is test evidence rather than production documentation, but it must move with
the owning crate's audited mapping.

### Public docs site

The following existing pages are directly affected; production updates must
describe RustAuth's eventual behavior rather than copy Better Auth prose:

- Core concepts: `cli`, `cookies`, `database`, `hooks`, `oauth`, `rate-limit`,
  `session-management`, and `users-accounts`.
- Reference: `options`, `security`, and the error index/pages.
- Authentication: Apple, Cognito, email/password, Google, and Microsoft.
- Plugins: 2FA, admin, API key, device authorization, email OTP, generic OAuth,
  last-login method, magic link, OAuth provider, OAuth proxy, One Tap,
  organization, passkey, SCIM, SIWE, SSO, and Stripe.
- Cross-cutting: database migrations, HTTP/error conventions, comparison
  claims, and the Unreleased changelog.

Two current statements become plainly false on a pin-only update:

1. The security page says clients without Fetch Metadata fall back to origin
   validation only when cookies exist. Tagged 1.6.24 validates a supplied
   Origin/Referer regardless of cookies.
2. The error reference presents `please_restart_the_process` as a future parity
   gap and omits `state_invalid`. Tagged 1.6.24 removed the former and added the
   latter.

Other pages are incomplete rather than necessarily false. For example, the 2FA
page omits the new persisted lockout state and 429 errors; options omit newly
documented controls; OAuth provider omits the metadata/issuer aliases; and
provider guides omit new verification/configuration rules. The SCIM page
already documents RustAuth-specific deprovision behavior, so it requires a
careful divergence comparison rather than replacement.

The comparison page's broad “Security handled” and “Production ready” marketing
statements are not pin-specific. They should be reconsidered only if an owning
implementation audit finds an unresolved security behavior; this research does
not independently rewrite them.

### HTTP, error, migration, examples, and CLI claims

| Surface | Required later disposition |
| --- | --- |
| `docs/http-json-conventions.md` | Replace its pin only after revalidating the new statuses/errors, `Cache-Control: no-store`, route 404 behavior, origin rejection, and cookie/header forwarding. |
| Error docs | Remove the obsolete future-gap claim only when the 1.6.24 error inventory is implemented/dispositioned; add `state_invalid` and new plugin errors/statuses where RustAuth exposes them. |
| Database migration docs | Add accepted schema changes (notably 2FA lockout fields), `disableMigration` behavior, adapter capability/atomicity rules, and SQL dialect corrections after implementation. |
| `examples/backend-reference` | Its claim to demonstrate all official plugins and social public APIs becomes incomplete unless new provider/plugin options and observable behavior are shown or explicitly marked unsupported. |
| `examples/cli-migrate-playground` | Its plugin-schema workflow must exercise the accepted 2FA fields and any other schema/migration deltas. |
| `examples/full-app` | Its rate-limit deployment modes need an explicit trusted-proxy/header/IPv6 disposition. |
| `examples/actix-web-minimal` | No version claim or directly affected behavior was found; update only if the framework HTTP contract changes. |
| CLI generated help | No Better Auth version claim exists. Change help only for accepted flag/command changes; update the README, `UPSTREAM.md`, docs-site CLI page, and migration examples for parity claims. |

## Claims that a mechanical pin bump would break

A global `1.6.9` → `1.6.24` replacement would:

1. Falsely say 22 crate READMEs are aligned with a target whose documented
   observable deltas have not yet been dispositioned.
2. Falsely preserve core's “all G1-G15 gaps closed” and complete-inventory
   conclusion despite new HTTP, security, cookie, option, and error contracts.
3. Falsely preserve high/complete/no-known-gap language in plugin, provider,
   OAuth-provider, CLI, storage, and adapter mapping documents.
4. Leave the error docs internally contradictory by promising an upstream error
   that 1.6.24 removed while omitting its replacement.
5. Leave the parity index, notice, commit SHA, checkout path, capture date,
   inventory counts, and source links inconsistent.
6. Make examples that claim complete plugin/provider coverage materially
   incomplete.
7. Corrupt historical changelog truth by relabeling the 0.2.0 release as a
   1.6.24-targeted release.

## Production-documentation update gate

After the map's behavior tickets are resolved, production documentation should
be updated in this order:

1. Record each 1.6.24 behavior as implemented, intentionally different, not
   applicable, or still unsupported in the owning crate's `UPSTREAM.md`.
2. Update affected public guides, error/status references, HTTP conventions,
   migration docs, and examples to describe the actual RustAuth behavior.
3. Refresh mapping inventories/counts and narrow any high/complete claim that
   the evidence no longer supports.
4. Update the reference tag, commit, path, date, notice, and parity index as one
   provenance change.
5. Change README compatibility blurbs only for crates whose disposition supports
   the claim; otherwise state the exact target and explicit gaps.
6. Add a new Unreleased changelog entry. Preserve every historical 1.6.9 entry.

Until that gate is satisfied, 1.6.9 remains the only supportable published
reference pin.
