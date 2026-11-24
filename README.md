# alphammotive auto-publisher — setup guide

Posts go out automatically at **5:00 pm, 9:00 pm and 4:30 am UAE time**, from a free GitHub
repository, using Instagram's official publishing API. Your computer does not need to be on.

One-time setup: about 15 minutes. You do every step that involves a password or a token yourself.

---

## Step 1 — Create the GitHub repository (10 min)

1. Sign up or log in at https://github.com.
2. Click **New repository**. Name: `alphammotive-publisher`. Visibility: **Public**
   (Instagram fetches each image from a public link, so the repo must be public).
3. Click **uploading an existing file** and drag in everything in this `05_Publisher` folder
   **except** `publish_workflow.yml`: that's `publish.py`, `schedule.csv`, `posted.json`,
   `README.md` and the `posts` folder.
4. Click **Commit changes**.
5. Add the timer: **Add file → Create new file**. In the name box type exactly
   `.github/workflows/publish.yml` (the slashes create the folders). Open `publish_workflow.yml`
   from this folder in Notepad, copy everything, paste it in, and click **Commit changes**.

## Step 2 — Meta token (done with Claude on 24 Nov)

Already set up: business portfolio **Alphammotive** → @alphammotive added → system user
**alphammotive publisher** with Content + Insights access → token for app **Content Manager**,
permissions `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`,
expiry **Never**.

If you ever need a new token: business.facebook.com → Settings → System users →
alphammotive publisher → **Generate token** (same choices), then update the GitHub secret.

## Step 3 — Give the token to GitHub (2 min)

1. In your repository: **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: `IG_ACCESS_TOKEN`. Value: paste the token. **Add secret**.

## Step 4 — Test before anything goes live (5 min)

In your repository open **Actions → Publish Instagram posts → Run workflow**:

1. Mode **check**: should print `Token OK for @alphammotive`.
2. Mode **dry**: shows which post it *would* publish right now, without posting.

If both look right, you're done. The timer takes over from the next slot.

---

## Day-to-day

| You want to… | Do this in `schedule.csv` on GitHub (pencil icon → edit → Commit) |
|---|---|
| Hold a post back | Change its `approved` value from `yes` to `no` |
| Move a post | Change its `publish_at` time (keep the `+04:00` at the end) |
| Re-post a skipped one | Give it a new future time |

- **Only rows with `approved = yes` are ever posted.** New weekly batches arrive with `approved = no`
  until you've checked them.
- `posted.json` is the record of what went live; the robot updates it. Don't edit it.
- If GitHub runs late (it sometimes does by up to an hour), the post still goes out. If a post is more
  than 3 hours late, it's skipped rather than dumped in with the next one, and the run log says so.

## Token renewal

Not needed: the system-user token never expires. If it's ever leaked, click **Revoke tokens** on
the system user, generate a new one and update the GitHub secret.

## If something fails

Open **Actions**, click the red run, and read the last lines. Common causes:
- `IG_ACCESS_TOKEN is not set` → Step 3 was missed.
- `error 190` → token revoked or wrong: generate a new one (Step 2) and update the secret.
- `Container … failed` → usually the image link: check the repo is Public.
