# Better Auth v1.6.9 to v1.6.24 observable delta

Research for [Catalog the observable Better Auth 1.6.9 to 1.6.24
delta](https://github.com/salasebas/rustauth/issues/211), under
[Wayfinder: Better Auth 1.6.24 observable
parity](https://github.com/salasebas/rustauth/issues/210).

## Result

Better Auth v1.6.24 is not a behavior-neutral patch upgrade from v1.6.9. The
range contains broad security hardening, new adapter primitives, changed default
security gates, new schema columns and indexes, different HTTP statuses and
error codes, stricter request validation, several new public options and hooks,
and client/CLI-only changes. No published package was added or removed, but the
`better-auth` package added the experimental `oauthPopup` plugin and a Yandex
generic-OAuth provider helper.

The highest-impact server/runtime changes are:

- OAuth and SSO identity proof was tightened across local-account linking,
  Google, Facebook, PayPal, Microsoft Entra ID, Reddit, WeChat, SIWE, One Tap,
  generic OAuth, OIDC, SAML, and SCIM.
- Verification values, authorization codes, refresh tokens, OTPs, WebAuthn
  challenges, SAML requests/assertions, device codes, rate-limit counters, and
  API-key counters gained atomic or guarded state transitions.
- Cached sessions stopped authorizing several sensitive operations after
  server-side revocation.
- Request-origin, redirect, callback, proxy-IP, remote-fetch, and SAML response
  validation became materially stricter.
- Two-factor authentication gained both a five-attempt per-challenge cap and an
  enabled-by-default account lockout. The latter requires two new database
  columns.
- The adapter contract gained `consumeOne`, `incrementOne`, and corresponding
  optional secondary-storage operations. Singular updates now fail closed on an
  empty predicate or a miss.
- OAuth Provider added a unique refresh-token constraint and indexes on its
  foreign keys.
- Some changes deliberately alter previously accepted requests, response status
  codes, error codes, callback timing, defaults, and persisted data.

This report inventories those deltas; it does not decide RustAuth dispositions
or implement parity.

## Scope, evidence, and method

The baseline is the exact official tag
[`v1.6.9`](https://github.com/better-auth/better-auth/tree/v1.6.9), commit
[`f484269228b7eb8df0e2325e7d264bb8d7796311`](https://github.com/better-auth/better-auth/commit/f484269228b7eb8df0e2325e7d264bb8d7796311).
The target is
[`v1.6.24`](https://github.com/better-auth/better-auth/tree/v1.6.24), commit
[`9a661c7b7abceaa81123b2c56757ee24f3ad2ed6`](https://github.com/better-auth/better-auth/commit/9a661c7b7abceaa81123b2c56757ee24f3ad2ed6).
The canonical source diff is the official
[`v1.6.9...v1.6.24` compare](https://github.com/better-auth/better-auth/compare/v1.6.9...v1.6.24).

The audit used four primary official source layers:

1. Every GitHub release body from
   [`v1.6.10`](https://github.com/better-auth/better-auth/releases/tag/v1.6.10)
   through
   [`v1.6.24`](https://github.com/better-auth/better-auth/releases/tag/v1.6.24),
   also rendered on Better Auth's official
   [changelog](https://better-auth.com/changelog).
2. Every `1.6.10` through `1.6.24` section in all 20 package changelogs at the
   target tag, starting with
   [`better-auth`](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/CHANGELOG.md)
   and
   [`@better-auth/core`](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/core/CHANGELOG.md).
3. The full source and commit diff: 380 commits and 742 changed files overall;
   261 commits and 489 changed files under `packages/`, including 270
   non-test TypeScript source files.
4. Better Auth's official
   [June 2026 security update](https://better-auth.com/blog/security-update-june-2026)
   and linked GitHub security advisories.

The package changelogs cite 212 distinct commits in this range. Every remaining
commit that changed non-test `packages/*/src` code was inspected separately.
Commits were classified by final behavior at v1.6.24, so an intermediate change
later reverted in the range is not reported as a target behavior.

Labels used below:

- **Security**: changes an authentication, authorization, trust, replay,
  confidentiality, or integrity boundary.
- **Default**: changes behavior when the caller does not set an option.
- **Breaking**: a previously valid request, callback contract, status/error, or
  storage behavior can change even though the npm release is semver-patch.
- **Schema**: changes generated or required persisted schema.
- **Client/type**: browser lifecycle or TypeScript-only; not Rust server
  runtime parity unless the public contract is independently mapped.

## Release and tag ledger

| Release | Tag commit | Commits since prior stable tag | Published behavior highlights |
| --- | --- | ---: | --- |
| [`v1.6.10`](https://github.com/better-auth/better-auth/releases/tag/v1.6.10) | [`698678b`](https://github.com/better-auth/better-auth/commit/698678bcd08e0552661f9ae306b031674e588a2c) | 65 | Email enumeration, cookie/redirect, organization, OAuth, API-key, Stripe, SSO, passkey, and CLI fixes. |
| [`v1.6.11`](https://github.com/better-auth/better-auth/releases/tag/v1.6.11) | [`f41514e`](https://github.com/better-auth/better-auth/commit/f41514ef07cfafc5dbf463bd1500aee6575d88a7) | 29 | Atomic consumption and OAuth rotation; account-linking, invitation, device, legacy OIDC/MCP, SSO, and SCIM security fixes. |
| [`v1.6.12`](https://github.com/better-auth/better-auth/releases/tag/v1.6.12) | [`c0c574e`](https://github.com/better-auth/better-auth/commit/c0c574ea50cfb3b9350f666590ad9747bb39ad6f) | 69 | Cookie/session, OpenAPI, OAuth redirects/errors, passkey replay, adapter, SSO dependency, and organization transaction fixes. |
| [`v1.6.13`](https://github.com/better-auth/better-auth/releases/tag/v1.6.13) | [`a6f38c7`](https://github.com/better-auth/better-auth/commit/a6f38c72ee3423ae80b0595fec3b4a61158c374d) | 17 | One Tap identity, OAuth redirect schemes, SAML logout/XML injection, API-key configuration, and account-state defaults. |
| [`v1.6.14`](https://github.com/better-auth/better-auth/releases/tag/v1.6.14) | [`5038d41`](https://github.com/better-auth/better-auth/commit/5038d41ca2c2a7350efb499c4506ac812afd6ddf) | 7 | Final 1.6.x organization invitation-gate semantics, nullable optional inputs, secure-cookie preference, redirect fragment rejection. |
| [`v1.6.15`](https://github.com/better-auth/better-auth/releases/tag/v1.6.15) | [`03e0e36`](https://github.com/better-auth/better-auth/commit/03e0e36a98a21eaf0ed39e384012f3216c954415) | 18 | Fresh-session checks, OAuth hook continuity, SAML clock skew, UserInfo POST, Kysely compatibility, passkey names. |
| [`v1.6.16`](https://github.com/better-auth/better-auth/releases/tag/v1.6.16) | [`1a3c8c4`](https://github.com/better-auth/better-auth/commit/1a3c8c478a94a7a2ddd1f0b62250b51f4fa0583f) | 10 | Large cross-package security review: admin fields, session authority, provider identity, SIWE, SSO, SCIM, OAuth Provider, and Electron. |
| [`v1.6.17`](https://github.com/better-auth/better-auth/releases/tag/v1.6.17) | [`0d8b238`](https://github.com/better-auth/better-auth/commit/0d8b238acc13da34d6769bb413d407b1356703fc) | 31 | Large atomicity/trust review, strict counters, provider hardening, team/invitation fixes, `oauthPopup`, CLI and client changes. |
| [`v1.6.18`](https://github.com/better-auth/better-auth/releases/tag/v1.6.18) | [`04debbf`](https://github.com/better-auth/better-auth/commit/04debbff04c2091c52b6b694df9081af2be50681) | 5 | OpenAPI request bodies and composite-monorepo client inference. |
| [`v1.6.19`](https://github.com/better-auth/better-auth/releases/tag/v1.6.19) | [`ac4d81d`](https://github.com/better-auth/better-auth/commit/ac4d81df748b8c09e584fdd6c440f8f327490fd1) | 26 | Chunked cache cookies, device-code prebinding, guarded-state adapter portability, callback error propagation, CLI/schema fixes. |
| [`v1.6.20`](https://github.com/better-auth/better-auth/releases/tag/v1.6.20) | [`c342f42`](https://github.com/better-auth/better-auth/commit/c342f42fff46043b5e195f7f757b0f2c1043414c) | 12 | Refresh-cookie maximum age, configured logging, `APIError` types, i18n fallback. |
| [`v1.6.21`](https://github.com/better-auth/better-auth/releases/tag/v1.6.21) | [`414169d`](https://github.com/better-auth/better-auth/commit/414169d95a88a6e1fac41688bc7011e96feb0d2a) | 29 | Proxy-IP/rate-limit, SAML, social identity, session authority, migration gating, adapter update, and two-factor challenge hardening. |
| [`v1.6.22`](https://github.com/better-auth/better-auth/releases/tag/v1.6.22) | [`a90d061`](https://github.com/better-auth/better-auth/commit/a90d061de7cdbd60e796230aadf5d1082add1fe2) | 5 | Credential revocation, account-level 2FA lockout/schema, server-side OAuth redirect refusal, SCIM active/deprovision semantics. |
| [`v1.6.23`](https://github.com/better-auth/better-auth/releases/tag/v1.6.23) | [`9dfceee`](https://github.com/better-auth/better-auth/commit/9dfceee14021fc15a2fb93023f39635f25b0b5ba) | 7 | Yandex helper, Drizzle affected-row counts, CLI escaping. |
| [`v1.6.24`](https://github.com/better-auth/better-auth/releases/tag/v1.6.24) | [`9a661c7`](https://github.com/better-auth/better-auth/commit/9a661c7b7abceaa81123b2c56757ee24f3ad2ed6) | 50 | Origin enforcement, model-name routing, OpenAPI, hooks/context, migration generation, session cache headers, SAML split-origin redirect, runtime races. |

## Cross-cutting public-contract changes

### Defaults and compatibility-sensitive behavior

| Final v1.6.24 behavior | Introduced/finalized | Impact |
| --- | --- | --- |
| `account.accountLinking.requireLocalEmailVerified` defaults to `true`; implicit OAuth/One Tap linking requires the existing local user to have verified email. | [`da7e50b`](https://github.com/better-auth/better-auth/commit/da7e50beee849c59a2ed1ec6b3a38cc6ab9fb563), v1.6.11 | **Security, default, breaking.** `false` retains the risky legacy behavior; the option is deprecated. |
| `organization.requireEmailVerificationOnInvitation` no longer has the simple v1.6.11 default of `true`. When unset at v1.6.24, by-ID accept/reject/get requires verification for externally controlled or predictable IDs, but preserves the emailed flow for built-in opaque/UUID IDs. Client-side `listUserInvitations` always requires verified email. Explicit `true`/`false` controls by-ID actions. | Initial hardening [`23094a6`](https://github.com/better-auth/better-auth/commit/23094a628f007f801be6d26e5b15dc5fc6fc4eb8), v1.6.11; final compatibility follow-up [`2d9781a`](https://github.com/better-auth/better-auth/commit/2d9781a83ddc7b51ecffbd7d24c28e4b917e2323), v1.6.14 | **Security, default, breaking.** Later parity work must model the final conditional gate, not only the v1.6.11 release note. |
| Legacy `oidc-provider` and `mcp` default `allowPlainCodeChallengeMethod` to `false`, reject incomplete PKCE, and stop advertising `"none"` signing. | [`699b09a`](https://github.com/better-auth/better-auth/commit/699b09a2064dcb7d37046b5a90626c0b6f57af90), v1.6.11 | **Security, default, breaking.** Explicit opt-in retains plain PKCE compatibility in 1.6.x. |
| With `secondaryStorage` and no primary database, account `storeStateStrategy` defaults to `"database"` (the secondary store) instead of `"cookie"`. | [`5f282bd`](https://github.com/better-auth/better-auth/commit/5f282bd382d694f6834b1d0f8f694f737f223811), v1.6.13 | **Default.** Avoids oversized OAuth state cookies; the account cookie remains for token access. |
| Plugin schema session fields `activeOrganizationId`, `activeTeamId`, and `impersonatedBy` are not generic input fields. `/update-session` rejects them. | [`5e49c56`](https://github.com/better-auth/better-auth/commit/5e49c56a9e12a9b6b3fd1202bbc7a2fc97aeeafd), v1.6.16 | **Security, breaking.** Dedicated endpoints are required. |
| Have I Been Pwned's default protected paths include email-OTP and phone-number password reset plus admin create/set-password. | [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc), v1.6.17 | **Security, default.** More password-setting requests can now be rejected. |
| Rate limiting is enforced even when no client IP can be resolved, before plugin request handlers, and does not trust the leftmost address in a multi-hop `X-Forwarded-For` chain. `advanced.ipAddress.trustedProxies` and custom trusted IP headers define proxy-aware resolution. | [`1dbf5bb`](https://github.com/better-auth/better-auth/commit/1dbf5bb59de5d628f0d07d5e846eba8287b831d7), v1.6.17; [`b046f9e`](https://github.com/better-auth/better-auth/commit/b046f9ec112b2cf547efea8dc870a4895602c53b) and [`5953157`](https://github.com/better-auth/better-auth/commit/5953157acf619bcb8233c91952b1e4072202f055), v1.6.21 | **Security, default, breaking.** |
| TOTP and backup-code verification has a five-error per-challenge cap. Account-level 2FA lockout is also enabled by default: 10 failures across factors lock for 15 minutes and return `429 ACCOUNT_TEMPORARILY_LOCKED`. | [`ae647b4`](https://github.com/better-auth/better-auth/commit/ae647b4abe5a4d606c326f1ce0ffa2500b5424d1), v1.6.21; [`3a035e9`](https://github.com/better-auth/better-auth/commit/3a035e968e27bfdee1e53ad857e5569090d9f2d1), v1.6.22 | **Security, default, breaking, schema.** Configurable with `twoFactor({ accountLockout: ... })`. |
| Session/account cache cookies are chunked near browser limits; an unchunkable cache is skipped with a warning and database fallback. Refresh `Max-Age` is capped at `expiresIn`/the browser ceiling. | [`de4aa52`](https://github.com/better-auth/better-auth/commit/de4aa52e991f0a56786300af3e0d9ac8331f1996), v1.6.19; [`8ecf238`](https://github.com/better-auth/better-auth/commit/8ecf23817f5e501bdd8ab63ad5fdf2554ff1dff5), v1.6.20 | **Default wire behavior.** Multiple `Set-Cookie` values replace one oversized cookie. |

### Persisted schema and migration delta

| Package/model | Delta | Evidence |
| --- | --- | --- |
| `better-auth` two-factor | Add nullable/private `failedVerificationCount` (default `0`) and `lockedUntil` to the `twoFactor` table. | [`packages/better-auth/src/plugins/two-factor/schema.ts`](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/src/plugins/two-factor/schema.ts), [`3a035e9`](https://github.com/better-auth/better-auth/commit/3a035e968e27bfdee1e53ad857e5569090d9f2d1). |
| `@better-auth/oauth-provider` | `oauthRefreshToken.token` becomes unique. Add indexes to OAuth client, refresh-token, access-token, consent, session, user, and parent-refresh-token reference fields. | [`packages/oauth-provider/src/schema.ts`](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/oauth-provider/src/schema.ts), [`c6918ec`](https://github.com/better-auth/better-auth/commit/c6918ecc9e3a75892169415d7f6c95b591b6a52d), [`f7bc1c7`](https://github.com/better-auth/better-auth/commit/f7bc1c73490d657a8ffa92a58ecfa9d8403d4fda). |
| Plugin migrations | `disableMigration: true` is preserved while assembling plugin tables, so runtime migration and Drizzle/Prisma generation omit those tables. | [`570267c`](https://github.com/better-auth/better-auth/commit/570267cd5e782f018933ce3af4f51dbd250bf7de), v1.6.21. |
| Organization invitations | If ID generation is delegated to the database, invitation creation leaves `id` unset so the database generates it; a hook-provided ID still wins. | [`f59a0ee`](https://github.com/better-auth/better-auth/commit/f59a0ee7895a024ddd4c5c387344173888e17be4), v1.6.24. |
| Generated schema semantics | Optional fields now accept explicit `null`; OpenAPI model IDs are required/read-only; OpenAPI user input includes configured/plugin fields; SQLite `BIGINT` is a valid numeric migration type; duplicate unique+index definitions are suppressed. | [`5a2d642`](https://github.com/better-auth/better-auth/commit/5a2d642bc7d940f4242df9b304818a8653ea2a10), [`3310ebc`](https://github.com/better-auth/better-auth/commit/3310ebc4a0c99d10c7fa13fef269db549a479dcd), [`4e685ee`](https://github.com/better-auth/better-auth/commit/4e685eef420b5576913b9803b58c7e7ee7342203), [`29a373e`](https://github.com/better-auth/better-auth/commit/29a373eaf1778820061a9380c29831c2de2ce704), [`99dbdd7`](https://github.com/better-auth/better-auth/commit/99dbdd7ea98740d11689394220a718dfb9579276), [`7508940`](https://github.com/better-auth/better-auth/commit/750894037639c4158472cc1d4994b0e07bf1f59a). |

No other target-tag model column was added or removed. Adapter and CLI fixes can
still change generated DDL, indexes, types, relations, or whether a table is
generated; those are catalogued below.

## `better-auth` public facade and server runtime

Representative source roots:
[`src/api`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/better-auth/src/api),
[`src/context`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/better-auth/src/context),
[`src/cookies`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/better-auth/src/cookies),
[`src/db`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/better-auth/src/db),
[`src/oauth2`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/better-auth/src/oauth2),
and
[`src/plugins`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/better-auth/src/plugins).

### Base credential, verification, and email behavior

- **v1.6.10:** Email enumeration protection now applies when
  `emailAndPassword.autoSignIn` is `false`. Duplicate and new sign-ups return
  `token: null`; duplicate sign-up returns a synthetic user and calls
  `onExistingUserSignUp`
  ([`9a7b51d`](https://github.com/better-auth/better-auth/commit/9a7b51d0d3dfbc6b2697fe5f9edd0bb480bdf89b)).
  Synthetic-user construction was subsequently made schema-shaped without
  leaking extra fields in v1.6.12
  ([`276d67f`](https://github.com/better-auth/better-auth/commit/276d67fad597ca415a023c10fb5e1165093eebd1)).
- **v1.6.10:** Email comparisons are normalized consistently in One Tap,
  email-OTP, and email verification
  ([`36ef808`](https://github.com/better-auth/better-auth/commit/36ef808c6cedec6eeb9a3a4e6790e0ab46d96ff3)).
  The captcha plugin no longer breaks the email-OTP flow
  ([`1e0f26d`](https://github.com/better-auth/better-auth/commit/1e0f26d4c83608d14a533f33458ade0f8504fd16)).
- **v1.6.11:** Magic links become single-use under concurrency through atomic
  verification consumption. `allowedAttempts` remains accepted but does not
  multiply successful redemptions; the repeat-redeem error changes from
  `ATTEMPTS_EXCEEDED` to `INVALID_TOKEN`
  ([`5f09d56`](https://github.com/better-auth/better-auth/commit/5f09d566a64ac9a0499d9664ce700edbf0630cea)).
- **v1.6.11:** Admin, anonymous, and SCIM user deletion also removes sessions
  ([`a26333b`](https://github.com/better-auth/better-auth/commit/a26333b5fb1a044e76c18385441d3ecc2240ab70)).
  The `change-email-disabled` response gains an identifiable error code
  ([`ee93485`](https://github.com/better-auth/better-auth/commit/ee934854999390ee5ca73592fe205a470a810b83)).
- **v1.6.12:** Email-OTP sign-in is excluded from captcha by default; callers
  can explicitly add `/sign-in/email-otp`
  ([`7a12072`](https://github.com/better-auth/better-auth/commit/7a120724c5c3fdd9d60d59169b32d693e9497fec)).
  `changeEmail` now returns HTTP 400 instead of false success if the required
  verification sender is absent, and encodes `callbackURL`
  ([`09a1d50`](https://github.com/better-auth/better-auth/commit/09a1d50a806f1599707ef4e7c47f8a4b8eb20f96)).
  Verification callbacks receive a cloned request
  ([`ad9ad82`](https://github.com/better-auth/better-auth/commit/ad9ad824965cb8385f6f2a921576f2cc58ac2b47));
  verify-email callback URLs in OAuth-link and username flows are encoded
  ([`c92cd74`](https://github.com/better-auth/better-auth/commit/c92cd74162cd1750404ab1da10d3fc20ed7d5e04)).
- **v1.6.12:** Expired verification values are consumed as absent. Magic-link
  expiry redirects with `INVALID_TOKEN` instead of `EXPIRED_TOKEN`; OAuth token
  endpoints retain `invalid_grant` but change the description to
  `"invalid code"`
  ([`f77060a`](https://github.com/better-auth/better-auth/commit/f77060af3a9d1f19f05a26ccf6e56d79bb9db69d)).
- **v1.6.16:** Cookieless browser email sign-in and sign-up validate
  `Origin`/`Referer` against `trustedOrigins`. Headerless non-browser requests
  remain allowed
  ([`87e7aa5`](https://github.com/better-auth/better-auth/commit/87e7aa5e0fd8f19b326beb5bec409a9ed1f245ca)).
- **v1.6.17:** Delete-account confirmations, password-reset tokens, email OTPs,
  phone OTPs, and one-time tokens become concurrency-safe single-use
  credentials
  ([`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).
  Captcha calls time out after 10 seconds and fail closed; HIBP protects more
  password-setting routes by default in the same commit.
- **v1.6.19:** `sendVerificationEmail` is awaited in the request path and thrown
  `APIError`s propagate instead of being backgrounded/caught and logged
  ([`7d18175`](https://github.com/better-auth/better-auth/commit/7d18175637a0b95a501fde0cf3db080879367a9d)).
  **Breaking timing/error contract:** this is observable to sender callbacks and
  HTTP clients.
- **v1.6.22:** Magic-link and email-OTP sign-in to an existing, never-confirmed
  account removes that account's password and revokes its sessions before
  signing in
  ([`c06a56d`](https://github.com/better-auth/better-auth/commit/c06a56d83a40bbaeac12d3a8b8b67e59f92a9110)).
- **v1.6.24:** Cookieless magic-link and email-OTP send endpoints force
  `Origin` validation, preventing cross-origin email triggering; headerless
  server-to-server calls remain valid
  ([`086ca91`](https://github.com/better-auth/better-auth/commit/086ca91f51dd8158aff6cbf54c4f9c7ce220914d)).
  Failure to clone a request for a verification callback no longer fails the
  auth request
  ([`ef4d273`](https://github.com/better-auth/better-auth/commit/ef4d27360cec8a0bc11a94e135ea4a3dd32b1969)).

### Sessions, cookies, cache, and request dispatch

- **v1.6.10:** Redirecting endpoints stop duplicating each `Set-Cookie`
  ([`09f1327`](https://github.com/better-auth/better-auth/commit/09f1327acb9c6bbfeb272dc62c7013172cf33153)).
  The bearer plugin replaces an existing cookie-name entry rather than
  appending a duplicate
  ([`906b7b3`](https://github.com/better-auth/better-auth/commit/906b7b34a710d49798e166395da2bcd2be13ef46)).
- **v1.6.12:** Cookie parsing tolerates semicolons without a following space
  ([`1b40dac`](https://github.com/better-auth/better-auth/commit/1b40dac22e0cfddbbb27136fe8067aba154ca91a));
  serialization percent-encodes values outside cookie-octet instead of dropping
  them
  ([`dcb2e6d`](https://github.com/better-auth/better-auth/commit/dcb2e6d29cf4c986ff8980dab50bcfcb8110a749));
  session resolution forwards refresh-cookie headers
  ([`5626e1b`](https://github.com/better-auth/better-auth/commit/5626e1b4375aef7735e4f1103035377cbfad755c));
  stateless cache refresh preserves the real session expiry
  ([`3f8f310`](https://github.com/better-auth/better-auth/commit/3f8f310a0f2737f65bb4393eefd6b9372b2cb00e)).
- **v1.6.12:** The 2FA-required response scrubs earlier valid session cookies
  before writing expirations, closing a cookie-cache 2FA bypass.
  `/two-factor/disable` uses sensitive-session middleware
  ([`c01b2f1`](https://github.com/better-auth/better-auth/commit/c01b2f13216463fc0fc0054b5acdb9559d29d825)).
- **v1.6.14:** `getSessionCookie` prefers `__Secure-` when secure and insecure
  variants coexist
  ([`9d3450a`](https://github.com/better-auth/better-auth/commit/9d3450ae23e8387d24adfb7bb1cb24cc6965b6e3)).
- **v1.6.15:** `list-session` requires a session within fresh age
  ([`ad60333`](https://github.com/better-auth/better-auth/commit/ad60333d1517142d688c61b6ccee14b4c30864ae)).
- **v1.6.16:** `/update-session`, `/get-access-token`, `/refresh-token`, and
  `/account-info` check the authoritative backing store when one exists, so a
  server-deleted session is rejected during the cookie-cache window
  ([`893cf6c`](https://github.com/better-auth/better-auth/commit/893cf6cb3f1f2669b39f6ac8d3d49cf830e5732e)).
  `/refresh-token` only trusts an account cookie whose user/provider/account
  identity matches the resolved session
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
- **v1.6.17:** `getCookieCache` returns `null` for an expired session;
  delete-account callbacks reject server-revoked sessions; multi-session
  activate/revoke requires a signed cookie for the named session; OIDC RP
  logout no longer accepts a cross-site cookie-only GET
  ([`0c3856f`](https://github.com/better-auth/better-auth/commit/0c3856f098f4a130abc49e9003ebc285824b0ba7)).
  Stateless account cookies work across server instances and survive session
  refresh
  ([`5c289b5`](https://github.com/better-auth/better-auth/commit/5c289b52bc166be3a36ec3c112b04195dc7621d8)).
- **v1.6.17:** Expected validation failures log at `warn`, not `error`
  ([`96c78c3`](https://github.com/better-auth/better-auth/commit/96c78c3e983ab3a2d914780fcc5d66d90537f9ac)).
- **v1.6.19:** Session/account cache-cookie chunking and fallback behavior
  changes as described above
  ([`de4aa52`](https://github.com/better-auth/better-auth/commit/de4aa52e991f0a56786300af3e0d9ac8331f1996)).
  The cookie-cache fallback lookup is corrected
  ([`c2f718f`](https://github.com/better-auth/better-auth/commit/c2f718fcdeec0c1767bb8acd5fefdd3810863b0a)).
  The attempted headerless `get-session` relaxation was reverted before the
  tag, so there is **no final headerless-session delta**
  ([add](https://github.com/better-auth/better-auth/commit/d009daedc75d0e61eb69e545a6ab40dd75cf541e),
  [revert](https://github.com/better-auth/better-auth/commit/36f345b1bcd5c83eb16d4d967719d101394a99b0)).
- **v1.6.20:** Refresh cookie `Max-Age` is capped at configured `expiresIn`
  ([`8ecf238`](https://github.com/better-auth/better-auth/commit/8ecf23817f5e501bdd8ab63ad5fdf2554ff1dff5)).
- **v1.6.21:** Admin authorization bypasses cookie-cache snapshots so bans and
  permission changes take effect immediately, including stateless signed-cookie
  applications
  ([`882cf9e`](https://github.com/better-auth/better-auth/commit/882cf9e592d1d305b5b78cadbb10aaeee7acd6dc)).
  A root-mounted handler returns 404 if the request path does not begin with
  configured `basePath`
  ([`e0762a1`](https://github.com/better-auth/better-auth/commit/e0762a127ce351a96614e60866b3455e6eddffa1)).
- **v1.6.24:** `get-session` carries `Cache-Control: no-store`
  ([`46d2bf0`](https://github.com/better-auth/better-auth/commit/46d2bf02c98902da7b344753372d48cfe0e5ebb3)).
  Concurrent first requests share one request-state `AsyncLocalStorage`
  initialization, avoiding intermittent serverless cold-start failures
  ([`54fab08`](https://github.com/better-auth/better-auth/commit/54fab084469a27257e66a0814523ebac7145ef5d)).

### OAuth, social providers, redirects, and account linking

- **v1.6.10:** OAuth callbacks reject missing provider account IDs instead of
  storing `"undefined"`
  ([`fc02ced`](https://github.com/better-auth/better-auth/commit/fc02cedb708e2b5987a177539a903cc35155a426)).
  Generic OAuth safely redirects non-ASCII `error_description`
  ([`1b25902`](https://github.com/better-auth/better-auth/commit/1b259024dcd1bbbc08559ee057f22c01929a72a7)).
  Username sign-in honors `callbackURL`, emits `Location`, and returns
  `{ redirect, url }`
  ([`e9c978e`](https://github.com/better-auth/better-auth/commit/e9c978e2af9e61d35f50fd040305cbb8fdda32ba)).
  SIWE client adds `getNonce` as an alias
  ([`9f1ef1f`](https://github.com/better-auth/better-auth/commit/9f1ef1f7e5500e0b3dbe2a18e25e3519847cd7a9))
  (**client/type**).
- **v1.6.11:** Shared OAuth account linking requires a verified local email by
  default, including One Tap; Google string `"false"` is normalized as false
  ([`da7e50b`](https://github.com/better-auth/better-auth/commit/da7e50beee849c59a2ed1ec6b3a38cc6ab9fb563)).
  This is the fix for
  [GHSA-g38m-r43w-p2q7](https://github.com/better-auth/better-auth/security/advisories/GHSA-g38m-r43w-p2q7).
- **v1.6.12:** Apple accepts hashed nonces from native iOS Sign in with Apple
  ([`a3b0c63`](https://github.com/better-auth/better-auth/commit/a3b0c63de908b9f85d6c1d6c06f89bab16a72ba3)).
  Generic OAuth can synthesize expiry with `accessTokenExpiresIn` when the
  provider omits `expires_in`
  ([`c5b9f93`](https://github.com/better-auth/better-auth/commit/c5b9f93498489888f543e1aa1fc07aae26f73a7f)).
  `accountLinking.updateUserInfoOnLink` applies to callback linking
  ([`23d7cbf`](https://github.com/better-auth/better-auth/commit/23d7cbfa793ca69b733f98334bd12962cad61646)).
- **v1.6.12:** OAuth callback failures share a redirect helper, preserve
  specific errors and per-flow `errorCallbackURL`, and encode error/query
  values. OAuth-proxy forwards `handleOAuthUserInfo` errors rather than
  collapsing them
  ([`23dbe1a`](https://github.com/better-auth/better-auth/commit/23dbe1ad0eb79372a674bc0771990c6cc3272a92),
  [`ac96316`](https://github.com/better-auth/better-auth/commit/ac96316af3070ba52c9492464305d3206aadc602),
  [`0a7cb70`](https://github.com/better-auth/better-auth/commit/0a7cb7064723d2096e36f44b86c59f7181a8e0c5),
  [`015f96b`](https://github.com/better-auth/better-auth/commit/015f96bc63a90c06a67fbaf80e286b6f6fe1967d)).
  OAuth-proxy state-cookie handling now supports deployments whose preview and
  production secrets differ
  ([`17cd433`](https://github.com/better-auth/better-auth/commit/17cd433c66a6ed323b9fda7d4e7db5ad98d8099b)).
- **v1.6.13:** Server-side `accountInfo` accepts trusted calls without session
  headers
  ([`d3919dc`](https://github.com/better-auth/better-auth/commit/d3919dc1a560625d8f09161d64701e257452940f)).
  One Tap resolves by the Google subject through the shared OAuth path instead
  of signing in a same-email wrong user. Account helper lookups are scoped to
  correct OAuth identity
  ([`43c08a2`](https://github.com/better-auth/better-auth/commit/43c08a2bc77eb01d59ecac28379d5971af6beddc)).
- **v1.6.13–v1.6.14:** OIDC/MCP redirect URIs reject unsafe schemes, runtimes
  without `URL.canParse` still validate, and URI fragments are rejected
  ([`be32012`](https://github.com/better-auth/better-auth/commit/be32012ca3507a62371d1baa09cdacd5123a99bf),
  [`13abc79`](https://github.com/better-auth/better-auth/commit/13abc7922b47f800da59ca212d364a64feeec91f)).
  This covers stable fixes associated with
  [GHSA-86j7-9j95-vpqj](https://github.com/better-auth/better-auth/security/advisories/GHSA-86j7-9j95-vpqj).
- **v1.6.15:** Global `hooks.before`/`hooks.after` run when OAuth authorization
  resumes after sign-in, account selection, or consent. Hook-set headers/cookies
  and `APIError` headers survive
  ([`b0ddfd3`](https://github.com/better-auth/better-auth/commit/b0ddfd3433cafac312ee99ec5fb7dbb9a240da35)).
- **v1.6.16:** Generic and built-in OAuth reject an empty account ID
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
  Shared provider-profile input filtering ignores fields with `input: false`
  (later released in v1.6.21 as
  [`b5bec19`](https://github.com/better-auth/better-auth/commit/b5bec193a56cec2f7b71c84d71dacb632f0b96a0)).
- **v1.6.16:** SIWE parses ERC-4361 and binds nonce, domain, wallet address,
  chain ID, expiration, and not-before to server state. New 401 errors identify
  mismatch/expiry/not-yet-valid
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
  At v1.6.21, SIWE also refuses to bind an email already used by another account
  ([`1bc370a`](https://github.com/better-auth/better-auth/commit/1bc370aef5c249e82127cb9d35972101087ecde6)).
- **v1.6.16 provider validation:** Facebook opaque tokens are checked with
  `debug_token` against configured app IDs; Google enforces the `hd` claim;
  PayPal ID tokens gain signature/issuer/audience/expiry/nonce verification;
  remote introspection requires configured audience unless
  `remoteVerify.allowMissingAudience: true`; JWKS caches are source-scoped with
  TTL; Reddit no longer treats `oauth_client_id` as a verified email
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15),
  source:
  [`packages/core/src/social-providers`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/core/src/social-providers)
  and
  [`packages/core/src/oauth2`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/core/src/oauth2)).
- **v1.6.17 provider follow-up:** Microsoft Entra ID enforces
  `organizations`/`consumers`; Reddit's placeholder becomes
  `<id>@reddit.invalid`; WeChat gets a stable unverified placeholder; Google One
  Tap requires a configured matching client ID; SSO string `"false"` is not
  verified; provider-specific One Tap/Microsoft/SSO/WeChat/Reddit identity
  validation is tightened
  ([`fdef997`](https://github.com/better-auth/better-auth/commit/fdef997eb944d85254816f7a4b2d76c06e9b8ec7)).
  Generic OAuth falls back correctly when `mapProfileToUser` derives the ID
  ([`7343284`](https://github.com/better-auth/better-auth/commit/73432841493a2d99144786c986ee57c071d816d8)).
- **v1.6.17:** New experimental `oauthPopup`, `oauthPopupClient`, and
  `signIn.popup` support popup completion and bearer handoff for cross-site
  iframe apps
  ([`d9c526b`](https://github.com/better-auth/better-auth/commit/d9c526b2a57afe9e01ff25da400f1d634b4c1ac7),
  [`source`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/better-auth/src/plugins/oauth-popup)).
  At v1.6.19 its `additionalData` strips internal state keys
  ([`8407885`](https://github.com/better-auth/better-auth/commit/840788502a13d6fa4aa4540b930ddb4a99dc1ed6)).
- **v1.6.21:** Google `hd: "*"` permits any Workspace domain but still requires
  an `hd` claim; One Tap applies the same configured restriction
  ([`816d7f9`](https://github.com/better-auth/better-auth/commit/816d7f92522518e90d437c2a366d75db56690f86)).
  PayPal userinfo `sub` must match the verified ID-token subject
  ([`239bcc8`](https://github.com/better-auth/better-auth/commit/239bcc836cf39c4fb409a15333be45134f9e9e65)).
  OAuth-proxy profile callbacks require live issued state
  ([`88409b0`](https://github.com/better-auth/better-auth/commit/88409b0078c2bfddcc6503031fff333bfa045cd2)).
- **v1.6.22:** Server-side OAuth fetches refuse redirect responses rather than
  following them
  ([`8bd43d9`](https://github.com/better-auth/better-auth/commit/8bd43d9d8312fd9ddbfb8fb5c827cf0a0e55132d)).
- **v1.6.23:** Generic OAuth exports a preconfigured Yandex provider helper
  ([`8581f97`](https://github.com/better-auth/better-auth/commit/8581f97ea0000e03edd6aa7911efabf694a9ff95),
  [`source`](https://github.com/better-auth/better-auth/blob/v1.6.24/packages/better-auth/src/plugins/generic-oauth/providers/yandex.ts)).
- **v1.6.24:** Custom social-provider `verifyIdToken` receives endpoint context
  as its third argument
  ([`c4d1dda`](https://github.com/better-auth/better-auth/commit/c4d1ddaa952eab7edfec942fab223f35798518ab)).

### Organization, admin, access, device, two-factor, and other plugins

- **v1.6.10 organization:** Dynamic role types are accepted on invitations
  ([`b2d655c`](https://github.com/better-auth/better-auth/commit/b2d655c77c7c627ada17456d1de106fdce6fa18e));
  `cancelPendingInvitationsOnReInvite` actually cancels then recreates
  ([`a597ee0`](https://github.com/better-auth/better-auth/commit/a597ee01ed4e6d85aba5ee9f15100acc578390d9));
  `setActiveTeam` is scoped to the active organization
  ([`c1336c5`](https://github.com/better-auth/better-auth/commit/c1336c563d45f93ca3fd4da4e6c767fc267d86d0)).
- **v1.6.10 admin/client:** Impersonation starts/stops revalidate the client
  session
  ([`80a655d`](https://github.com/better-auth/better-auth/commit/80a655d271dcae5f785a70f13be60f80fb828cf1));
  sign-out clears the active-member-role browser state
  ([`e71aad3`](https://github.com/better-auth/better-auth/commit/e71aad3b6d67502cfb770fa8890f3ab58c537114))
  (**client-only**).
- **v1.6.11 device authorization:** Visiting `GET /device` claims a pending code
  for the authenticated session; approve/deny must match that owner
  ([`99a254a`](https://github.com/better-auth/better-auth/commit/99a254a79b59d5a3f5ca2123260118cddb5beed7),
  [GHSA-cq3f-vc6p-68fh](https://github.com/better-auth/better-auth/security/advisories/GHSA-cq3f-vc6p-68fh)).
- **v1.6.11 organization:** The invitation verification gate was introduced
  and all recipient reads/actions were covered
  ([`23094a6`](https://github.com/better-auth/better-auth/commit/23094a628f007f801be6d26e5b15dc5fc6fc4eb8),
  [GHSA-fmh4-wcc4-5jm3](https://github.com/better-auth/better-auth/security/advisories/GHSA-fmh4-wcc4-5jm3));
  v1.6.14 changed the unset behavior to the final conditional policy detailed
  above.
- **v1.6.12 access/organization:** `role.authorize` rejects empty action lists
  and evaluates all resources under OR
  ([`9bd53e1`](https://github.com/better-auth/better-auth/commit/9bd53e191cda174c202a07b6d27af73300e6b175)).
  Delete-organization/remove-member cascades are transactional
  ([`f5e29ea`](https://github.com/better-auth/better-auth/commit/f5e29eaf1e57d73a024d12b1bedf4162e5f4a863)).
  Invitation team IDs containing commas are rejected with `INVALID_TEAM_ID`
  ([`1d372bb`](https://github.com/better-auth/better-auth/commit/1d372bbab9117f5a574ecb608b7a5108f1ccbc66)).
  Admin `createUser` applies username validation
  ([`6b44606`](https://github.com/better-auth/better-auth/commit/6b44606b7d596527b59176b7a0cd06ea66df9031)).
- **v1.6.13–v1.6.14 organization:** Logo accepts `null` to clear
  ([`87c1a0c`](https://github.com/better-auth/better-auth/commit/87c1a0cab274b574592922ccc2454b0bd510a81f)).
  The invitation compatibility policy is finalized
  ([`2d9781a`](https://github.com/better-auth/better-auth/commit/2d9781a83ddc7b51ecffbd7d24c28e4b917e2323)).
- **v1.6.15 admin:** `unbanUser`, `setRole`, and `adminUpdateUser` return
  `404 USER_NOT_FOUND` for unknown users instead of adapter 500
  ([`1012b69`](https://github.com/better-auth/better-auth/commit/1012b690466ccd7078441dbfb406eef166fca805)).
- **v1.6.16 admin:** `create-user`/`update-user` protect role, ban, email,
  email-verification, and password fields with dedicated permissions and
  validation; custom access control needs `user:set-email`; bans revoke
  sessions and self-ban is rejected
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
- **v1.6.16 organization:** Invitation team IDs are checked against the
  invitation organization both at creation and acceptance
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
- **v1.6.17 organization:** Team capacity is enforced on direct add, add-team,
  and concurrent invitation acceptance; failed add no longer leaves a member
  ([`ed7b6c9`](https://github.com/better-auth/better-auth/commit/ed7b6c9ac0fa2bb7f246f552b41046302ef8138c),
  [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).
  Deleting a team removes it from pending invitations; missing teams fail
  without consuming an invitation
  ([`7343284`](https://github.com/better-auth/better-auth/commit/73432841493a2d99144786c986ee57c071d816d8)).
  Member-role update tokenizes and validates static/dynamic roles
  ([`b803c61`](https://github.com/better-auth/better-auth/commit/b803c61fdcfc64be4e26bf6fa10953621f0070cc)).
- **v1.6.17 admin:** `setUserPassword` creates a credential account for a
  social-only/passwordless user instead of returning false success
  ([`3e99e6c`](https://github.com/better-auth/better-auth/commit/3e99e6c77ef788377a3ddb7abe790c7dc3df1493)).
- **v1.6.17 two-factor/device:** Approved device codes, email/phone/2FA OTPs,
  backup-code regeneration, SIWE nonces, one-time tokens, and 2FA challenges
  gain guarded single-use semantics
  ([`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).
  An expired 2FA challenge cannot complete a session.
- **v1.6.19 device authorization:** `/device/code` accepts optional `user_id`
  to pre-bind the code; only that user can approve or deny it
  ([`b4b0266`](https://github.com/better-auth/better-auth/commit/b4b02660c760fe4c8889d1311a3dbf3165f88d0b)).
  `deviceAuthorization()` no longer requires a `schema` option under Zod 4 at
  v1.6.21
  ([`f52e1ab`](https://github.com/better-auth/better-auth/commit/f52e1ab50b60d289b64d6b06f1bff5a4358cdfd0)).
- **v1.6.21 username:** Display-username fallback is persisted as username only
  if valid
  ([`461ca6f`](https://github.com/better-auth/better-auth/commit/461ca6fd2453a2e145fa18a1df543e435e884701)).
- **v1.6.21–v1.6.22 two-factor:** Five wrong TOTP/backup-code attempts invalidate
  a sign-in challenge
  ([`ae647b4`](https://github.com/better-auth/better-auth/commit/ae647b4abe5a4d606c326f1ce0ffa2500b5424d1));
  account-wide lockout adds the configuration, error, counter, timer, and
  schema described above
  ([`3a035e9`](https://github.com/better-auth/better-auth/commit/3a035e968e27bfdee1e53ad857e5569090d9f2d1)).
- **v1.6.24 organization:** `listMembers` uses the same configured membership
  limit for its user fetch and no longer fails above roughly 100 members
  ([`bae7198`](https://github.com/better-auth/better-auth/commit/bae71988ab79aeb4f19f245ceabac9eca8706a50)).
  Delete-organization hooks receive endpoint context; Stripe forwards it
  ([`3bf0e49`](https://github.com/better-auth/better-auth/commit/3bf0e4981e025ba9af684013a27b0102a04f7c56)).
  `last-login-method.beforeStoreCookie` can transform/veto cookie storage
  ([`f23ce50`](https://github.com/better-auth/better-auth/commit/f23ce5012ea47fac1a69b1dad203dfdef3830fd0)).

### Adapter/model routing and public internal API

- **v1.6.10:** `internalAdapter.deleteAccount` renames its positional parameter
  from `accountId` to `id`; runtime semantics remain primary-key delete
  ([`15ff28a`](https://github.com/better-auth/better-auth/commit/15ff28a957a18df8ecd2aa08d66b94c91ae9a6a4)).
  `refreshUserSessions` is exposed on the internal adapter
  ([`3a9a2c3`](https://github.com/better-auth/better-auth/commit/3a9a2c37eeab1d0c98845a47642d4dc27fe54ceb)).
- **v1.6.11:** `DBAdapter.consumeOne`, optional
  `SecondaryStorage.getAndDelete`, and
  `internalAdapter.consumeVerificationValue` are added
  ([`0cbddb8`](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a)).
  Database paths are atomic; secondary-only storage without `getAndDelete`
  keeps a compatibility fallback and warns that cross-process single use is
  not guaranteed.
- **v1.6.17:** `DBAdapter.incrementOne`,
  `SecondaryStorage.increment`, rate-limit storage `consume`, and
  `internalAdapter.reserveVerificationValue` are added
  ([`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).
  They provide guarded atomic deltas/counters and replay reservations; fallback
  behavior is documented where an adapter lacks the native operation.
- **v1.6.19:** Active transactions are reused so `consumeOne` does not deadlock
  a single-connection pool
  ([`a787e0b`](https://github.com/better-auth/better-auth/commit/a787e0b66b368a1af0b4ba17c9750c2839668246)).
- **v1.6.21:** Singular `adapter.update` returns `null` for no predicate or no
  matching row. Callers must use `updateMany` for intentional bulk update
  ([`90d509e`](https://github.com/better-auth/better-auth/commit/90d509e0b9f72614170ad7124ae9d3a7a97d7d3a)).
- **v1.6.24:** Exact schema keys win over model-name aliases, eliminating
  foreign-key and adapter-join misrouting when remapped names collide
  ([`03dc5a0`](https://github.com/better-auth/better-auth/commit/03dc5a046f536994950800ea557b8e2e2e0cdfdd),
  [`0f2cc1b`](https://github.com/better-auth/better-auth/commit/0f2cc1b33b77850948dac4d889e5f46bba41e8d5)).

### OpenAPI and public TypeScript/client surface

- **v1.6.10:** `/sign-in/social` required fields are corrected in OpenAPI
  ([`88a7c67`](https://github.com/better-auth/better-auth/commit/88a7c678f4db3f7da580d53071b2595b92354a45)).
  Organization field types are re-exported for portable declarations
  ([`cf59136`](https://github.com/better-auth/better-auth/commit/cf591360e72a8d01741618cd61cdeea84cf8398a)).
- **v1.6.12:** Multi-method endpoints get unique OpenAPI operation IDs
  ([`43cc49c`](https://github.com/better-auth/better-auth/commit/43cc49c640c0d2c27572807a291d318bbcadfd04)).
  Admin/organization client option types are exported
  ([`f5fcc9d`](https://github.com/better-auth/better-auth/commit/f5fcc9d37f2c46d3719a70c18857d9913ce172cf)).
  `parseJSON` decodes quoted escape sequences
  ([`a6f144a`](https://github.com/better-auth/better-auth/commit/a6f144ad0a8ef702969cf49c999ccd073eb1ffa6)).
- **v1.6.14:** Optional input fields accept explicit `null`
  ([`5a2d642`](https://github.com/better-auth/better-auth/commit/5a2d642bc7d940f4242df9b304818a8653ea2a10)).
- **v1.6.17:** Client `updateSession` infers custom session fields
  ([`59e0ccb`](https://github.com/better-auth/better-auth/commit/59e0ccbedc6c336b1e77f71c62484d654fd2fca3)).
  Session queries deduplicate focus-driven fetches, preserve stable data
  references, and clear loading on unmount
  ([`8960f5f`](https://github.com/better-auth/better-auth/commit/8960f5f3bd2f0dccbfb768d69737d8a24d793a9e))
  (**client-only**).
- **v1.6.17 source/release-only:** OpenAPI model `id` fields become required and
  read-only; returned required fields such as `emailVerified` are required in
  component schemas
  ([`3310ebc`](https://github.com/better-auth/better-auth/commit/3310ebc4a0c99d10c7fa13fef269db549a479dcd)).
- **v1.6.18:** Intersected/default-wrapped OpenAPI request bodies serialize
  correctly
  ([`9ef7240`](https://github.com/better-auth/better-auth/commit/9ef7240fec4a9d8469dd5ed24249949d3400e732)).
  Plugin client methods and additional session fields infer in composite
  monorepos
  ([`b21a5f7`](https://github.com/better-auth/better-auth/commit/b21a5f7f6ca1f63c6b69666a498b4227b15e316c))
  (**client/type**).
- **v1.6.19:** Callback/session/passkey schemas become valid for OpenAPI client
  generators
  ([`c1a8a64`](https://github.com/better-auth/better-auth/commit/c1a8a64c146fab20c7ad0076ffdf12eff9adc17a)).
  Wrapper-exported auth clients get nameable declaration types
  ([`635f190`](https://github.com/better-auth/better-auth/commit/635f1908702d0c63cf66b4e5f054e9d527a3c8f7)).
- **v1.6.20:** `APIError` declares inherited properties for TypeScript
  inference
  ([`930f534`](https://github.com/better-auth/better-auth/commit/930f5341d956bf3075f43758392a5c7f50947104)).
- **v1.6.24:** `/sign-up/email` and `/update-user` OpenAPI inputs include
  configured and plugin user fields
  ([`4e685ee`](https://github.com/better-auth/better-auth/commit/4e685eef420b5576913b9803b58c7e7ee7342203)).
  `useSession({ throw: true }).data` retains `null`
  ([`ae78109`](https://github.com/better-auth/better-auth/commit/ae781091186f321b4e4ec9e84f64b6e4d5ea1043));
  auth query listeners recover after remount
  ([`f6d18fa`](https://github.com/better-auth/better-auth/commit/f6d18fa8f79b9323e10b50f72e2b1a088844e4bb))
  (**client/type**).
  `CookieAttributes`' extension values narrow from `any` to
  `string | number | boolean | Date | undefined`
  ([`d3ce782`](https://github.com/better-auth/better-auth/commit/d3ce7823324ba64efd423895b1c122d85c6d7663))
  (**type-level breaking**).

## `@better-auth/core`

Source roots:
[`src/db`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/core/src/db),
[`src/oauth2`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/core/src/oauth2),
[`src/social-providers`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/core/src/social-providers),
and
[`src/utils`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/core/src/utils).

- The adapter/secondary-storage primitives, singular update fail-closed
  semantics, active-transaction reuse, model-name resolution, plugin migration
  flag, proxy-IP resolver, and request-state initialization changes are shared
  contracts described above.
- **v1.6.10:** Cloudflare Workers without OpenTelemetry use the pure no-op
  instrumentation entry
  ([`2220a6d`](https://github.com/better-auth/better-auth/commit/2220a6d6c25ebd24c8568131636389dc0c12f82b)).
- **v1.6.11:** `advanced.ipAddress.ipv6Subnet` accepts every integer prefix from
  0 through 128, not only `32 | 48 | 64 | 128`
  ([`e21d744`](https://github.com/better-auth/better-auth/commit/e21d744987476c20a934c79ef226fe6a5f468e22)).
- **v1.6.12:** `verifyAccessToken` maps invalid token-shape/`kid` failures to
  unauthorized API errors but preserves JWKS infrastructure errors
  ([`7bf5449`](https://github.com/better-auth/better-auth/commit/7bf5449b11866bd82deafee910619660c153d799)).
  Public string helpers `toCamelCase`, `toSnakeCase`, `toPascalCase`, and
  `toKebabCase` are added under `@better-auth/core/utils/string`
  ([`83fa369`](https://github.com/better-auth/better-auth/commit/83fa3695e7cc0083ff8531f3a2b4101a2e56deff)).
  Cloudflare `nodejs_compat` password hashing selects `node:crypto`
  ([`2b7937f`](https://github.com/better-auth/better-auth/commit/2b7937fc2febd048bfc14b8226287b55b7d48e52)).
- **v1.6.13:** `consumeOne` fallback throws a clear error if an adapter's
  `deleteMany` return is non-numeric
  ([`5c3e248`](https://github.com/better-auth/better-auth/commit/5c3e248cbf4f81c2cb540b545baa4a5e69d3b066)).
- **v1.6.16–v1.6.17:** Social-provider token/identity checks, JWKS cache
  scoping/leak fixes, placeholder-email behavior, request-host isolation,
  reserved-IP blocking, and server-fetch redirect rules are the shared core
  contracts detailed in the OAuth section
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15),
  [`7343284`](https://github.com/better-auth/better-auth/commit/73432841493a2d99144786c986ee57c071d816d8),
  [`fdef997`](https://github.com/better-auth/better-auth/commit/fdef997eb944d85254816f7a4b2d76c06e9b8ec7),
  [`1dbf5bb`](https://github.com/better-auth/better-auth/commit/1dbf5bb59de5d628f0d07d5e846eba8287b831d7)).
- **v1.6.22:** The new server-side OAuth request helper rejects redirects
  ([`8bd43d9`](https://github.com/better-auth/better-auth/commit/8bd43d9d8312fd9ddbfb8fb5c827cf0a0e55132d)).
- **v1.6.24:** `verifyIdToken` gains endpoint context and request-state
  initialization is concurrency-safe
  ([`c4d1dda`](https://github.com/better-auth/better-auth/commit/c4d1ddaa952eab7edfec942fab223f35798518ab),
  [`54fab08`](https://github.com/better-auth/better-auth/commit/54fab084469a27257e66a0814523ebac7145ef5d)).

## `@better-auth/api-key`

Source:
[`packages/api-key/src`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/api-key/src).

- **v1.6.10:** `api.verifyApiKey` checks a supplied `configId`
  ([`62c4050`](https://github.com/better-auth/better-auth/commit/62c40508501f5056dacc9c9da94e4ddf9ada1001)).
- **v1.6.11:** Rate-limit rejection returns HTTP 429 instead of 401
  ([`b039985`](https://github.com/better-auth/better-auth/commit/b03998586af6c47b2c9b6cdd556d36416bc71711)).
- **v1.6.12:** `better-call` is a peer dependency so public declaration emit can
  name types
  ([`f6bf451`](https://github.com/better-auth/better-auth/commit/f6bf45123fdd3b045a7cadff779fb41acd17d08c)).
- **v1.6.13:** Omitting `configId` verifies a key against the configuration that
  created the key, including a non-default configuration
  ([`e131d3a`](https://github.com/better-auth/better-auth/commit/e131d3ac5ba476cc9cc306e46422c7d2d21f3929)).
- **v1.6.16:** Create-key uses an authoritative session instead of cookie cache.
  Verification writes only fields it owns and cannot overwrite a concurrent
  disable/permission/expiry update or recreate a deleted secondary-store key
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
- **v1.6.17:** Atomic `incrementOne` prevents remaining uses below zero and
  concurrent rate-limit bypass. Secondary-only storage without database fallback
  remains best effort. Update-key rejects a server-revoked session
  ([`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc),
  [`0c3856f`](https://github.com/better-auth/better-auth/commit/0c3856f098f4a130abc49e9003ebc285824b0ba7)).
- **v1.6.21:** API-key IP rate limiting uses the hardened trusted-proxy
  resolution contract
  ([`5953157`](https://github.com/better-auth/better-auth/commit/5953157acf619bcb8233c91952b1e4072202f055)).

## `@better-auth/oauth-provider`

Source:
[`packages/oauth-provider/src`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/oauth-provider/src).

- **v1.6.10:** Consent continuation binds the post-login skip to the signing
  session and honors `prompt=login`; OAuth foreign keys gain generated indexes;
  helper types are exported; refresh-token `sessionId` becomes optional in the
  public type
  ([`408a307`](https://github.com/better-auth/better-auth/commit/408a3076bdd5b450c96bdad82be797ac8a8d3f83),
  [`f7bc1c7`](https://github.com/better-auth/better-auth/commit/f7bc1c73490d657a8ffa92a58ecfa9d8403d4fda),
  [`d427d1d`](https://github.com/better-auth/better-auth/commit/d427d1dba91db8861d935ca5838f49eb7e617f67),
  [`6b03a45`](https://github.com/better-auth/better-auth/commit/6b03a45a14d905aa070068290adfedfd4c5f4e2d)).
- **v1.6.11:** Authorization-code exchange atomically consumes the code; racers
  receive standard `invalid_grant`, replacing `invalid_verification`
  ([`b4bc65a`](https://github.com/better-auth/better-auth/commit/b4bc65a007784b2eb0efb459e5fa6fd8055d3ec9),
  [GHSA-7w99-5wm4-3g79](https://github.com/better-auth/better-auth/security/advisories/GHSA-7w99-5wm4-3g79)).
  Refresh-token rotation uses compare-and-swap, rejects the losing racer with
  `invalid_grant`, and adds the unique token constraint
  ([`c6918ec`](https://github.com/better-auth/better-auth/commit/c6918ecc9e3a75892169415d7f6c95b591b6a52d),
  [GHSA-392p-2q2v-4372](https://github.com/better-auth/better-auth/security/advisories/GHSA-392p-2q2v-4372)).
- **v1.6.12:** Expired-code errors, direct well-known metadata for path-prefixed
  issuers, dynamic-registration metadata hiding, colon-containing Basic Auth
  secrets, and missing-client consent behavior change
  ([`f77060a`](https://github.com/better-auth/better-auth/commit/f77060af3a9d1f19f05a26ccf6e56d79bb9db69d),
  [`8401d11`](https://github.com/better-auth/better-auth/commit/8401d11f4386be819807f7f241a0aae5cd20edc1),
  [`d64174e`](https://github.com/better-auth/better-auth/commit/d64174ec86434375cb7e010ee4dfcd031e20c821),
  [`938efee`](https://github.com/better-auth/better-auth/commit/938efee305c66cdb73e84321523d5db5658e4ed8),
  [`87f5a8f`](https://github.com/better-auth/better-auth/commit/87f5a8fd27faa8534523348a0671e60466b083c0)).
- **v1.6.13–v1.6.14:** Dynamic client registration enforces
  `clientPrivileges`; redirect URI validation is runtime-safe and rejects
  fragments
  ([`17ab66c`](https://github.com/better-auth/better-auth/commit/17ab66c3a4beef72c3a4ac82ce7aca21650e8462),
  [`13abc79`](https://github.com/better-auth/better-auth/commit/13abc7922b47f800da59ca212d364a64feeec91f)).
- **v1.6.15:** UserInfo also accepts POST with bearer authorization; auth hooks
  run through resumed OAuth flow
  ([`fe9600b`](https://github.com/better-auth/better-auth/commit/fe9600bc0734eeb2e6fbb0c53d3b81888bd4247d),
  [`b0ddfd3`](https://github.com/better-auth/better-auth/commit/b0ddfd3433cafac312ee99ec5fb7dbb9a240da35)).
- **v1.6.16:** `/oauth2/continue` ignores the client-submitted `postLogin` flag
  as proof and uses the server-issued session-bound marker. Introspection
  requires JWT access tokens to carry `azp` for an enabled client. Token grants
  enforce each client's declared `grantTypes`; missing grants default to
  `authorization_code`; pure client-credentials clients no longer receive
  refresh tokens
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
- **v1.6.17:** Introspection/revocation caches signing keys per auth instance for
  five minutes
  ([`7343284`](https://github.com/better-auth/better-auth/commit/73432841493a2d99144786c986ee57c071d816d8)).
- **v1.6.18:** Signed OAuth query verification canonicalizes parameter order, so
  CDN/proxy reordering does not break a signature; pre-deploy signed redirects
  may fail for their short remaining lifetime
  ([`729fd84`](https://github.com/better-auth/better-auth/commit/729fd84034d547f37bb8c1c5b8958280c5bdb487)).
- **v1.6.19:** Guarded token transitions work on Prisma and pre-5.0 MongoDB
  ([`5bd5e1c`](https://github.com/better-auth/better-auth/commit/5bd5e1cc73d2c9c38e69011f03038b61a4312a63)).

## `@better-auth/sso`

Source:
[`packages/sso/src`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/sso/src).

- **v1.6.10:** SAML SP metadata resolves providers configured through
  `defaultSSO`
  ([`006e809`](https://github.com/better-auth/better-auth/commit/006e809b92d4a933e52a4684b74419bc419530dc)).
- **v1.6.11:** Only organization admins/owners can register SSO providers
  ([`86765f1`](https://github.com/better-auth/better-auth/commit/86765f1597378f5c3deed1b80ca91faac0a6bf00),
  [GHSA-gv74-j8m3-fg5f](https://github.com/better-auth/better-auth/security/advisories/GHSA-gv74-j8m3-fg5f)).
  User-supplied OIDC endpoints are validated during registration/update
  ([`37f60cb`](https://github.com/better-auth/better-auth/commit/37f60cb176cb53147da7dfd5ec15afa5b486e81e),
  [GHSA-5rr4-8452-hf4v](https://github.com/better-auth/better-auth/security/advisories/GHSA-5rr4-8452-hf4v)).
- **v1.6.12:** OIDC/SAML hook rejections redirect to encoded error callbacks;
  the OIDC error query is encoded
  ([`23dbe1a`](https://github.com/better-auth/better-auth/commit/23dbe1ad0eb79372a674bc0771990c6cc3272a92),
  [`f47aa4a`](https://github.com/better-auth/better-auth/commit/f47aa4aa96f7be9898ce25ff5ccd583344786573)).
  `fast-xml-parser` is raised from `^5.5.7` to `^5.8.0`
  ([`e637c7d`](https://github.com/better-auth/better-auth/commit/e637c7d8ffc63fec8f7a27e0a0384842058a8ca9)).
- **v1.6.13:** SAML Single Logout deletes the session by token rather than row
  ID
  ([`43c08a2`](https://github.com/better-auth/better-auth/commit/43c08a2bc77eb01d59ecac28379d5971af6beddc)).
  `samlify` is upgraded to 2.13.1 and integration handling is adjusted for
  signed-assertion XML injection
  ([`4c3bbc4`](https://github.com/better-auth/better-auth/commit/4c3bbc4e56e5ae4ec4d780daaa71358d663cee06),
  [GHSA-34r5-q4jw-r36m](https://github.com/better-auth/better-auth/security/advisories/GHSA-34r5-q4jw-r36m)).
- **v1.6.15:** Configured SAML `clockSkew` reaches samlify's
  `ServiceProvider`, preventing false `ERR_SUBJECT_UNCONFIRMED`
  ([`bff65fd`](https://github.com/better-auth/better-auth/commit/bff65fd620ac62d72c24c9ed79badf1e31cf1a39)).
- **v1.6.16:** OIDC token/userinfo/JWKS endpoints are DNS-resolved and must be
  publicly routable at request time; discovery/userinfo redirects are not
  followed without validation; explicit trusted origins can allow internal
  IdPs. SSO provider IDs cannot collide with social, trusted, or built-in
  provider namespaces, and SSO callbacks do not inherit social
  `trustedProviders`
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
- **v1.6.17:** SAML assertions have concurrency-safe replay protection;
  `"false"` email verification is false; an org admin/owner may verify an
  organization-owned provider even if another member registered it
  ([`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc),
  [`fdef997`](https://github.com/better-auth/better-auth/commit/fdef997eb944d85254816f7a4b2d76c06e9b8ec7),
  [`ed7b6c9`](https://github.com/better-auth/better-auth/commit/ed7b6c9ac0fa2bb7f246f552b41046302ef8138c)).
  A source/release-only commit atomically consumes the matching SAML
  AuthnRequest, so two ACS submissions cannot reuse it
  ([`a6b0295`](https://github.com/better-auth/better-auth/commit/a6b0295df3d6ced4beb460ef8082ff941facae2f)).
- **v1.6.21:** Provider deletion removes linked account rows; SAML response
  audience, bearer recipient, and destination must match the SP; SLO form
  actions are HTTP(S) only; every comma-separated domain requires DNS proof
  ([`7a7a7b3`](https://github.com/better-auth/better-auth/commit/7a7a7b311aa8f546bd8d3301e1cbd37a9a5a30f1),
  [`fa1e036`](https://github.com/better-auth/better-auth/commit/fa1e036ae7bd326920e7d797046d966a440f60bd),
  [`1a8b7cc`](https://github.com/better-auth/better-auth/commit/1a8b7ccc8397922ec2fb51b10a92a12d58ea65c6),
  [`fcabaff`](https://github.com/better-auth/better-auth/commit/fcabaaffcbe48adcbdcaf876a4f8404c6bf640d4)).
- **v1.6.24:** IdP-initiated SAML in split-origin deployments redirects success
  and error to global/per-provider `idpInitiatedCallbackUrl`
  ([`c020a9d`](https://github.com/better-auth/better-auth/commit/c020a9d6a2e7782f388363a85fc0748ae8b3b0c9)).

## `@better-auth/scim`

Source:
[`packages/scim/src`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/scim/src).

- **v1.6.11:** User deletion cleans sessions. Token issuance rejects provider
  IDs colliding with built-in/social account providers
  ([`a26333b`](https://github.com/better-auth/better-auth/commit/a26333b5fb1a044e76c18385441d3ecc2240ab70),
  [`2f5d91c`](https://github.com/better-auth/better-auth/commit/2f5d91c5bb7d0e22f07533b40c9905ef97e3a9e9)).
- **v1.6.16:** Provisioning does not email-link an existing user unless new
  `linkExistingUsers` policy explicitly permits it (`true`, trusted domains,
  existing org membership, or callback). Default conflict is HTTP 409.
  Organization-scoped delete deprovisions membership/account link instead of
  deleting the global user. New `canGenerateToken` authorizes SCIM token
  creation
  ([`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15)).
- **v1.6.17:** Organization deprovision uses organization removal so team
  memberships and hooks run. SCIM bearer tokens use constant-time comparison in
  plain, hashed, encrypted, and custom storage
  ([`7343284`](https://github.com/better-auth/better-auth/commit/73432841493a2d99144786c986ee57c071d816d8),
  [`ed7b6c9`](https://github.com/better-auth/better-auth/commit/ed7b6c9ac0fa2bb7f246f552b41046302ef8138c)).
- **v1.6.19:** List-user filters are no longer logged
  ([`f3e1a40`](https://github.com/better-auth/better-auth/commit/f3e1a405cdc3939d2472d6891ddb181aeb1d3959)).
- **v1.6.21:** SSO provider deletion removes SCIM-linked account rows
  ([`7a7a7b3`](https://github.com/better-auth/better-auth/commit/7a7a7b311aa8f546bd8d3301e1cbd37a9a5a30f1)).
- **v1.6.22:** Non-org delete unlinks only the provider account when other
  identities remain and deletes the global user only for the sole identity.
  PUT/PATCH duplicate-email conflict is 409 and an email change clears
  `emailVerified`. `active` becomes read-write: false bans/deactivates and
  revokes sessions, true reactivates; this requires the admin plugin
  ([`7c126dc`](https://github.com/better-auth/better-auth/commit/7c126dcd1aad24468ec37e876545c1d083d8acca)).

## `@better-auth/passkey`

Source:
[`packages/passkey/src`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/passkey/src).

- **v1.6.10:** Autofill startup failure becomes a handled cancellation
  ([`ddae581`](https://github.com/better-auth/better-auth/commit/ddae5817c882ed47961588e795ee194ee64c9e6b))
  (**client-only**).
- **v1.6.12:** WebAuthn challenges are single-use under concurrency. A failed
  registration returns `400 FAILED_TO_VERIFY_REGISTRATION` instead of 500;
  failed authentication returns `401 AUTHENTICATION_FAILED` instead of 400
  ([`8907c7d`](https://github.com/better-auth/better-auth/commit/8907c7df9cf330f36ded6fa3cd588faf6ca8e568)).
  Undefined transports no longer crash
  ([`33a3632`](https://github.com/better-auth/better-auth/commit/33a3632731ab1aa722d82541dc2aff71ba3f2090)).
- **v1.6.15:** Public `getAuthenticatorName(aaguid)` and
  `commonAuthenticatorNames` are added. `registration.afterVerification` may
  provide a default name; names are trimmed on create/update
  ([`d23735b`](https://github.com/better-auth/better-auth/commit/d23735b1deb3ff7d63330430fc1f0cdf639bd734)).
- **v1.6.17:** Challenge purpose is bound: registration cannot use an
  authentication challenge or vice versa; unresolved target users fail
  ([`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).
- **v1.6.19:** Passkey OpenAPI output is valid for client generators
  ([`c1a8a64`](https://github.com/better-auth/better-auth/commit/c1a8a64c146fab20c7ad0076ffdf12eff9adc17a)).

## `@better-auth/stripe`

Source:
[`packages/stripe/src`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/stripe/src).

- **v1.6.10:** `getCheckoutSessionParams` cannot override library-owned
  reconciliation/billing fields; request locale wins. Custom
  `subscription_data` preserves free trial and internal metadata. Subscription
  update/cancel/delete/trial hooks receive the raw Stripe object or post-update
  local row rather than stale snapshots
  ([`51de32e`](https://github.com/better-auth/better-auth/commit/51de32e1e81a45f437e82a5e9d51438f3372f511),
  [`07b52cb`](https://github.com/better-auth/better-auth/commit/07b52cbb795ff74fcd3747036eefd0c780cf8d58),
  [`5d24a74`](https://github.com/better-auth/better-auth/commit/5d24a7478b563b38353681c0f6317d540a4721f1),
  [`3e4fc8c`](https://github.com/better-auth/better-auth/commit/3e4fc8ca74e04f4e675dd69c8d552141c6ef5d9b)).
- **v1.6.12:** URL normalization and Stripe search escaping handle backslashes
  before quotes
  ([`62dabf6`](https://github.com/better-auth/better-auth/commit/62dabf66780a3dc7270e419886a15c43f3c8d879)).
- **v1.6.17:** Existing Stripe customers are email-reused at signup only for a
  verified email. Checkout success syncs the selected subscription. Cancel and
  restore target only the requested subscription. Upgrade `returnUrl` is
  trusted-origin checked. Organization deletion scans all subscriptions
  ([`a11a706`](https://github.com/better-auth/better-auth/commit/a11a706ff29ed0862b080fad27f93b40cbc59b4b)).
- **v1.6.21:** Organization cancel/upgrade/restore/portal actions are scoped to
  the correct organization
  ([`29fbcb5`](https://github.com/better-auth/better-auth/commit/29fbcb573261242d8a05b131a9d39c9ae4352b06)).
- **v1.6.24:** Organization deletion hook wrappers forward endpoint context
  ([`3bf0e49`](https://github.com/better-auth/better-auth/commit/3bf0e4981e025ba9af684013a27b0102a04f7c56)).

## Adapters and secondary storage

The RustAuth parity index directly maps the Kysely adapter contract to its SQL
adapters. Drizzle, Prisma, Mongo, and memory are not independent RustAuth target
packages, but their fixes expose cross-adapter contract expectations and must
not be dismissed as JavaScript-only.

### `@better-auth/kysely-adapter`

- **v1.6.11:** Native `consumeOne` supports atomic verification consumption
  ([`0cbddb8`](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a)).
- **v1.6.12:** Bun/Node SQLite introspection reports tables, not views;
  MySQL insert-return uses a transactional cascade and warns with
  `generateId: false`; Kysely peer support widens to 0.28/0.29
  ([`160d132`](https://github.com/better-auth/better-auth/commit/160d132752b2e540cea8f9c2d2c57307b96867a4),
  [`5190c26`](https://github.com/better-auth/better-auth/commit/5190c2658f0827b533e7006e95587317ea8cb0cc),
  [`04303a9`](https://github.com/better-auth/better-auth/commit/04303a92acd6fd3cf9d5f5ab5901255e67526ad3)).
- **v1.6.15:** SQLite migration-table constants are locally mirrored, avoiding
  Turbopack/strict-ESM failures while supporting Kysely 0.28 and 0.29. The final
  implementation commit is
  [`ef4e131`](https://github.com/better-auth/better-auth/commit/ef4e131b8565817324453c9c1aad8bb4c0641784);
  release prose points at its precursor
  [`0933c05`](https://github.com/better-auth/better-auth/commit/0933c050ff8735466a273347c9aab0fdd8cd38ff).
- **v1.6.17:** Atomic `incrementOne`; Bun/Node SQLite affected-row/insert-ID and
  multi-bind fixes; SQL Server `consumeOne` avoids `LIMIT`
  ([`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).
- **v1.6.21:** Singular update returns `null` for miss/empty predicate
  ([`90d509e`](https://github.com/better-auth/better-auth/commit/90d509e0b9f72614170ad7124ae9d3a7a97d7d3a)).

### Other first-party adapters

- **Drizzle:** Native consume; MySQL safe insert return; mixed AND/OR query
  correctness; atomic counters; `updateMany` affected count; consumed MySQL
  password-reset rows; D1/postgres-js/bun-sql affected-row reporting
  ([`0cbddb8`](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a),
  [`5190c26`](https://github.com/better-auth/better-auth/commit/5190c2658f0827b533e7006e95587317ea8cb0cc),
  [`85ca603`](https://github.com/better-auth/better-auth/commit/85ca603eecaafa21d4950288b4d58d95c1b5b0b4),
  [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc),
  [`0895993`](https://github.com/better-auth/better-auth/commit/08959936d29de8a37d469e42d9077859b643d6b3),
  [`930b260`](https://github.com/better-auth/better-auth/commit/930b260cfd402e9f8886719a3ced503b9ceff7f6)).
- **Prisma:** Native consume/counter; deletion errors other than missing rows
  propagate; singular update fails closed; guarded transitions work portably
  ([`0cbddb8`](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a),
  [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc),
  [`90d509e`](https://github.com/better-auth/better-auth/commit/90d509e0b9f72614170ad7124ae9d3a7a97d7d3a),
  [`5bd5e1c`](https://github.com/better-auth/better-auth/commit/5bd5e1cc73d2c9c38e69011f03038b61a4312a63)).
- **Mongo:** Native consume/counter; guarded transitions work on servers older
  than 5.0
  ([`0cbddb8`](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a),
  [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc),
  [`5bd5e1c`](https://github.com/better-auth/better-auth/commit/5bd5e1cc73d2c9c38e69011f03038b61a4312a63)).
- **Memory:** Native consume/counter; failed transactions no longer erase
  concurrent writes; empty-filter singular update/delete is a no-op;
  `updateMany` returns affected count
  ([`0cbddb8`](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a),
  [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).
- **Redis storage:** Optional atomic `getAndDelete`; atomic `increment`; a
  rate-limit window's TTL is set only at creation rather than extended by every
  request
  ([`0cbddb8`](https://github.com/better-auth/better-auth/commit/0cbddb8fa4eb19fbca75e9822134f89b3604286a),
  [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc)).

## `auth` CLI

Source:
[`packages/cli/src`](https://github.com/better-auth/better-auth/tree/v1.6.24/packages/cli/src).

- **v1.6.10:** `auth init` passes the driver directly in generated
  MySQL/PostgreSQL Kysely configs
  ([`e44427b`](https://github.com/better-auth/better-auth/commit/e44427b37331c6bcf29d553ed2f135a512bcd750)).
- **v1.6.12 source-only:** CLI login/logout delegates to `npx auth@latest`
  instead of the nonexistent/incorrect `@better-auth/cli`
  ([`db4263c`](https://github.com/better-auth/better-auth/commit/db4263cd3d70d2d1830a241c7ce6d12c114e6d4c)).
- **v1.6.17:** Config loading stubs SvelteKit, Vite asset/query, and Cloudflare
  virtual modules; Prisma regeneration updates `BigInt`/`Int` when `bigint`
  changes and skips existing `Unsupported()` fields
  ([`6987c62`](https://github.com/better-auth/better-auth/commit/6987c628f16b7c4bd855d73b16304b04a1fe766d),
  [`108aadd`](https://github.com/better-auth/better-auth/commit/108aadd25171ffd20ee3a79a2650243a796067aa),
  [`ac69e81`](https://github.com/better-auth/better-auth/commit/ac69e81a29eb4d48f45638f651afa9b4af0d5ffc)).
- **v1.6.19:** `generate --output` accepts a directory; array
  `additionalField.defaultValue` is serialized in Drizzle output
  ([`cfbb9a0`](https://github.com/better-auth/better-auth/commit/cfbb9a05243da942d4c5f9fae80077bbccd17f5c),
  [`d6aec12`](https://github.com/better-auth/better-auth/commit/d6aec123d8cf9f50e357e67c2916010f9f09b561)).
- **v1.6.21:** Plugin `disableMigration` is honored. Generated
  `BETTER_AUTH_SECRET` increases from 16 random bytes/32 hex characters to 32
  random bytes/64 hex characters
  ([`570267c`](https://github.com/better-auth/better-auth/commit/570267cd5e782f018933ce3af4f51dbd250bf7de),
  [`452bd03`](https://github.com/better-auth/better-auth/commit/452bd03f747a0a4852daa3902e1671abda2dbc57)).
- **v1.6.23:** Drizzle string defaults escape quotes/backslashes
  ([`3fedfcb`](https://github.com/better-auth/better-auth/commit/3fedfcb01d0f2a3e653a98a0f7f7891949361b7a)).
- **v1.6.24:** Config self-import of a not-yet-created output is temporarily
  stubbed and retried; explicit SvelteKit env modules are stubbed; Drizzle
  relations with multiple FKs to one model get `relationName`; unique+index
  does not generate duplicate unique indexes
  ([`0f2cc1b`](https://github.com/better-auth/better-auth/commit/0f2cc1b33b77850948dac4d889e5f46bba41e8d5),
  [`6f3ba45`](https://github.com/better-auth/better-auth/commit/6f3ba45639579da152b69e8e5342e02f28288670),
  [`097eecd`](https://github.com/better-auth/better-auth/commit/097eecdd16b82c9730ad145e7823be499a76e2fe),
  [`99dbdd7`](https://github.com/better-auth/better-auth/commit/99dbdd7ea98740d11689394220a718dfb9579276)).

## Other published packages

| Package | Classification | Observable delta |
| --- | --- | --- |
| `@better-auth/i18n` | Mapped RustAuth server package | At v1.6.20, if no default locale and no English translation is supplied, fallback remains built-in English rather than the first provided locale ([`3965752`](https://github.com/better-auth/better-auth/commit/3965752b5a2ab4507d071f9d18f88b47da9a3a6f)). |
| `@better-auth/electron` | Unmapped platform integration; classify as client/desktop except its server proxy routes | Cookie reserialization fix at v1.6.12; S256-only transfer PKCE at v1.6.16; authorization-code single use at v1.6.17; correct multi-`Set-Cookie` proxy forwarding at v1.6.24; tested Electron 43 with peer floor unchanged ([`dcb2e6d`](https://github.com/better-auth/better-auth/commit/dcb2e6d29cf4c986ff8980dab50bcfcb8110a749), [`cb1cbfa`](https://github.com/better-auth/better-auth/commit/cb1cbfa4ccba1ce13f7fea419a6fc37dcbdc2f15), [`baeaa00`](https://github.com/better-auth/better-auth/commit/baeaa00bc2a600c04f746c7cc2a07065b7691dcc), [`d7c41ba`](https://github.com/better-auth/better-auth/commit/d7c41baa1fdd2f088a6f09b4aea422174bad0acc), [`67cff3e`](https://github.com/better-auth/better-auth/commit/67cff3edbf0f3f5978ae449323b684eb1b49fa35)). |
| `@better-auth/expo` | Unmapped mobile client integration | Large account cookies are chunked in device storage; ID-token social linking includes the stored session cookie; authorization-proxy callback/redirect targets use the shared trusted-origin hardening ([`e24ddfd`](https://github.com/better-auth/better-auth/commit/e24ddfd13b31e23a0b3c2178077be016de8d7d49), [`d3758fb`](https://github.com/better-auth/better-auth/commit/d3758fb2a35e601a26aa9682d9c9856e45459dda), [`1dbf5bb`](https://github.com/better-auth/better-auth/commit/1dbf5bb59de5d628f0d07d5e846eba8287b831d7)). |
| `@better-auth/telemetry` | Mapped RustAuth package, but dependency-only in this range | No independent changelog entry or source behavior change; releases only track `@better-auth/core` dependency versions. |
| `@better-auth/test-utils` | Unmapped development-only package | Adds/updates shared adapter conformance coverage for singular update and Drizzle consumed rows; no production runtime contract beyond the adapter expectations already catalogued ([`90d509e`](https://github.com/better-auth/better-auth/commit/90d509e0b9f72614170ad7124ae9d3a7a97d7d3a), [`0895993`](https://github.com/better-auth/better-auth/commit/08959936d29de8a37d469e42d9077859b643d6b3)). |

## Security advisory cross-check

Better Auth's official
[security update](https://better-auth.com/blog/security-update-june-2026)
states that release notes are not a sufficient audit source and identifies
package-specific fixed versions. Stable-range advisories relevant to this delta
are:

| Advisory | Area | Stable fix in this range |
| --- | --- | --- |
| [GHSA-g38m-r43w-p2q7](https://github.com/better-auth/better-auth/security/advisories/GHSA-g38m-r43w-p2q7) | OAuth account-link ownership | `better-auth@1.6.11` |
| [GHSA-2vg6-77g8-24mp](https://github.com/better-auth/better-auth/security/advisories/GHSA-2vg6-77g8-24mp) | Session cleanup after user deletion | `better-auth@1.6.11`, `@better-auth/scim@1.6.11` |
| [GHSA-fmh4-wcc4-5jm3](https://github.com/better-auth/better-auth/security/advisories/GHSA-fmh4-wcc4-5jm3) | Organization invitation ownership | `better-auth@1.6.11`, with v1.6.14 compatibility semantics |
| [GHSA-cq3f-vc6p-68fh](https://github.com/better-auth/better-auth/security/advisories/GHSA-cq3f-vc6p-68fh) | Device-flow owner binding | `better-auth@1.6.11` |
| [GHSA-7w99-5wm4-3g79](https://github.com/better-auth/better-auth/security/advisories/GHSA-7w99-5wm4-3g79) | Authorization-code replay | `better-auth@1.6.11`, `@better-auth/oauth-provider@1.6.11` |
| [GHSA-392p-2q2v-4372](https://github.com/better-auth/better-auth/security/advisories/GHSA-392p-2q2v-4372) | Refresh-token rotation | `@better-auth/oauth-provider@1.6.11` |
| [GHSA-5rr4-8452-hf4v](https://github.com/better-auth/better-auth/security/advisories/GHSA-5rr4-8452-hf4v) | SSO endpoint SSRF | `@better-auth/sso@1.6.11` |
| [GHSA-gv74-j8m3-fg5f](https://github.com/better-auth/better-auth/security/advisories/GHSA-gv74-j8m3-fg5f) | SSO registration authorization | `@better-auth/sso@1.6.11` |
| [GHSA-pw9m-5jxm-xr6h](https://github.com/better-auth/better-auth/security/advisories/GHSA-pw9m-5jxm-xr6h) | Legacy OIDC/MCP refresh-token handling | `better-auth@1.6.11` |
| [GHSA-86j7-9j95-vpqj](https://github.com/better-auth/better-auth/security/advisories/GHSA-86j7-9j95-vpqj) | Legacy OIDC/MCP redirect URI validation | `better-auth@1.6.13` |
| [GHSA-9h47-pqcx-hjr4](https://github.com/better-auth/better-auth/security/advisories/GHSA-9h47-pqcx-hjr4) | Legacy OIDC/MCP protocol defaults | `better-auth@1.6.11` |
| [GHSA-34r5-q4jw-r36m](https://github.com/better-auth/better-auth/security/advisories/GHSA-34r5-q4jw-r36m) | Signed SAML assertion XML injection | `@better-auth/sso@1.6.13` |

Later stable commits add further security-sensitive behavior even when no public
advisory is linked from the June index: the v1.6.16 provider/admin/SCIM/SIWE
review, v1.6.17 atomicity/trust review, v1.6.21 SAML and proxy-IP review,
v1.6.22 credential revocation and account lockout, and v1.6.24 email-send origin
checks. Those must remain in the parity matrix even if advisory metadata is not
available.

## Commits not adequately represented by package changelog prose

These were found by comparing every package-source commit with all 20 package
changelog sections. Some appear in GitHub release prose; others only in source.

| Commit | Final observable delta | Changelog status |
| --- | --- | --- |
| [`db4263c`](https://github.com/better-auth/better-auth/commit/db4263cd3d70d2d1830a241c7ce6d12c114e6d4c) | CLI login/logout invokes `npx auth@latest`, not `@better-auth/cli`. | Not in package changelogs or release body. |
| [`ef4e131`](https://github.com/better-auth/better-auth/commit/ef4e131b8565817324453c9c1aad8bb4c0641784) | Final Kysely 0.28/0.29/Turbopack implementation mirrors migration table constants locally. | Release/changelog prose points primarily at precursor `0933c05`; final implementation hash is omitted. |
| [`a6b0295`](https://github.com/better-auth/better-auth/commit/a6b0295df3d6ced4beb460ef8082ff941facae2f) | SAML AuthnRequest is atomically consumed, preventing concurrent ACS reuse. | GitHub release body only; absent from package changelogs. |
| [`7faddd4`](https://github.com/better-auth/better-auth/commit/7faddd4a1d15a7d82c0c8ece7ad65c4a4955d4b6) | Adds explicit `createAuthEndpoint.serverOnly` and marks API-key maintenance/verify, set-password, email-OTP generation/read, JWT sign/verify, organization add-member, backup-code view, and TOTP generation as server-only. They were already pathless; the final HTTP behavior remains non-routable, but the invariant is now explicit and OpenAPI/router-safe. | GitHub release body only; absent from package changelogs. |
| [`3310ebc`](https://github.com/better-auth/better-auth/commit/3310ebc4a0c99d10c7fa13fef269db549a479dcd) | OpenAPI model IDs are required/read-only; returned required fields are required. | GitHub release body only; absent from package changelogs. |
| [`ac69e81`](https://github.com/better-auth/better-auth/commit/ac69e81a29eb4d48f45638f651afa9b4af0d5ffc) | Prisma regeneration skips existing `Unsupported()` fields. | GitHub release body only; absent from CLI changelog. |
| [`452bd03`](https://github.com/better-auth/better-auth/commit/452bd03f747a0a4852daa3902e1671abda2dbc57) | Generated secret entropy doubles from 16 to 32 bytes. | GitHub release body only; absent from CLI changelog. |
| [`d3ce782`](https://github.com/better-auth/better-auth/commit/d3ce7823324ba64efd423895b1c122d85c6d7663) | Public `CookieAttributes` index signature narrows from `any`. | GitHub v1.6.24 release body only; absent from package changelog. |

The following unlisted source commits have no additional final runtime delta:
the `claimOne` precursor was renamed/finalized as changelogged `consumeOne`
([`a2c0c93`](https://github.com/better-auth/better-auth/commit/a2c0c9346e84b3f6fa4db30f4ddc4c9f7401178b));
the cookie regex and Stripe variable changes were behavior-preserving
refactors; the headerless-session change was reverted; TypeScript 6/tsdown
edits were build/type cleanup; documentation-only source comments clarified
existing behavior.

## Package-to-RustAuth classification for later mapping

This is classification, not a disposition:

| Upstream package | RustAuth declared surface | Classification |
| --- | --- | --- |
| `better-auth` | `rustauth-core`, `rustauth`, `rustauth-plugins`, HTTP integrations | Server/runtime, routes, plugins, OpenAPI/wire behavior, and public options are in scope; browser-only hook lifecycle and TypeScript inference are catalogued but normally not applicable. |
| `@better-auth/core` | `rustauth-core`, `rustauth-oauth`, `rustauth-social-providers` | In scope. |
| `@better-auth/api-key` | `rustauth-plugins` | In scope. |
| `@better-auth/oauth-provider` | `rustauth-oauth-provider` | In scope. |
| `@better-auth/sso` | `rustauth-sso`, `rustauth-saml`, `rustauth-oidc` | In scope. |
| `@better-auth/scim` | `rustauth-scim` | In scope. |
| `@better-auth/passkey` | `rustauth-passkey` | Server/WebAuthn contract in scope; browser autofill UX is not. |
| `@better-auth/stripe` | `rustauth-stripe` | In scope. |
| `@better-auth/i18n` | `rustauth-i18n` | In scope. |
| `@better-auth/telemetry` | `rustauth-telemetry` | No independent behavior delta. |
| `auth` CLI | `rustauth-cli` | Command/config/schema behavior in scope. |
| `@better-auth/kysely-adapter` | All RustAuth SQL adapters | Contract in scope across SQLx, Diesel, tokio-postgres, and deadpool-postgres. |
| Drizzle/Prisma/Mongo/memory adapters | No one-to-one package | Not direct ports, but their conformance fixes define shared adapter behavior and failure semantics; map to applicable RustAuth adapters/tests. |
| `@better-auth/redis-storage` | `rustauth-redis`, `rustauth-fred`, secondary-storage consumers | Atomic secondary-storage contract in scope. |
| Electron/Expo | No declared Rust client platform package | Client/platform integrations are out of scope after the server proxy/cookie/trust behavior is checked for shared relevance. |
| `@better-auth/test-utils` | RustAuth shared test utilities | Production package out of scope; conformance expectations feed parity tests. |

## Inputs the next Wayfinder decisions must carry forward

1. Treat the v1.6.16 and v1.6.17 bundled review commits as many independent
   observable deltas, not one changelog item or one implementation task.
2. Use the final v1.6.14 conditional organization-invitation policy, not the
   temporary v1.6.11 unconditional default, when comparing behavior.
3. Decide the RustAuth contract for callback timing before mapping
   `sendVerificationEmail`: upstream v1.6.19 waits and propagates callback
   errors, while RustAuth's repository policy requires outbound sender hooks to
   be dispatched without delaying the HTTP success response.
4. Plan database work for the two-factor lockout columns and OAuth Provider
   unique/index changes across every applicable adapter.
5. Audit every single-use and guarded-counter flow against the new atomic
   adapter/secondary-storage contract, including documented best-effort
   fallbacks.
6. Preserve fail-closed behavior for authoritative sessions, origin/redirect
   validation, provider identity, proxy IPs, remote fetches, SAML validation,
   SCIM linking, and OAuth grants even if exact upstream compatibility needs an
   explicit Rust-specific exception.
7. Keep client/type-only and Electron/Expo deltas visible in the matrix with an
   explicit not-applicable disposition; do not silently omit them.
