---
name: auth-model-decisions
description: "AWH decided 2026-07-26 to keep auth as-is — no share-link self-registration, no self-service password change; the reasoning behind both"
metadata: 
  node_type: memory
  type: project
  originSessionId: d413c558-a55b-4a05-a102-51ffa429f928
  modified: 2026-07-26T13:24:20.797Z
---

Two auth changes were proposed and **declined by AWH on 2026-07-26**. Don't
re-propose them as improvements; if they come up again, this is the context.

**1. Share-link guests creating their own username/password — NO.**
The property that makes share links safe is that the token is the *entire*
credential and revocation is instant and total: `load_user()` re-reads
`share_tokens.json` on every request, so deleting a token kills live sessions
mid-browse. Links are meant to be forwarded, so self-registration would turn a
revocable, disposable credential into a permanent-account factory whose
accounts outlive the link — and you wouldn't know who holds them. The friction
it would remove is also small: `login_user(remember=True)` with a 365-day
cookie means a guest re-authenticates only on a *new device*, a few times a
year for a family this size, against ~30 seconds for an admin on
`/admin/users`. Safer shapes were offered (admin-side "convert to account", or
token-tied claiming that dies with the token) and also declined.

**2. Self-service password change — NOT NOW.**
Password changes stay admin-only via `PUT /api/users/<username>`. If this is
revisited, the design was: an `/account` page requiring the current password,
share guests (`share:` ids, empty `password_hash`) excluded, plus a shared
minimum-length rule — there is currently **no length validation anywhere**,
only a non-empty check in `api_user_create`.

**Known limitation either way:** Flask-Login's remember cookie is keyed on
`user.id` alone, so changing a password would NOT sign out other devices.
Making it do so needs a versioned identity (e.g. a `pw_changed_at` stamp
checked in `load_user`).

Related: [[app-is-private-family-only]], [[ux-review-2026-07]].
