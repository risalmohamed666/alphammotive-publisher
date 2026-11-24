# alphammotive auto-publisher — setup guide

Posts go out automatically at **5:00 pm, 9:00 pm and 4:30 am UAE time**, from a free GitHub
repository, using Instagram's official publishing API. Your computer does not need to be on.

One-time setup: about 30–45 minutes. You do every step that involves a password or a token yourself.

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

## Step 2 — Create the Meta app and get your token (20–30 min)

Your Instagram account must stay a **Professional (Creator)** account. It already is.

1. Go to https://developers.facebook.com → log in with Facebook → **My Apps → Create app**.
2. Use case: **Manage messaging & content on Instagram**. App type: Business. Name: `alphammotive publisher`.
3. In the app dashboard open **Instagram → API setup with Instagram login**.
4. Under **Generate access tokens**, click **Add account** and log in as **@alphammotive**.
   Allow the permissions it asks for (basic profile + content publishing).
5. Click **Generate token** next to @alphammotive and copy it.
   This is a long-lived token, valid for **60 days**.
   Treat it like a password: never paste it into chat, email or a file.

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

## Every 50 days — renew the token

The token expires after 60 days. Set a phone reminder for 50 days after setup, then repeat
**Step 2.5** (Generate token) and **Step 3** (update the secret, same name). Takes 3 minutes.

## If something fails

Open **Actions**, click the red run, and read the last lines. Common causes:
- `IG_ACCESS_TOKEN is not set` → Step 3 was missed.
- `error 190` → token expired or revoked: renew it.
- `Container … failed` → usually the image link: check the repo is Public.
