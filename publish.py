"""
alphammotive auto-publisher.

Reads schedule.csv, publishes every approved post whose time has come
(and is not older than CATCHUP_HOURS) to Instagram via the official
Instagram Graph API (system-user token from the Alphammotive business
portfolio), then records it in posted.json.

Env vars:
  IG_ACCESS_TOKEN   system-user access token (GitHub secret)
  IG_USER_ID        Instagram account ID (default: @alphammotive)
  GITHUB_REPOSITORY owner/repo (set automatically by GitHub Actions)
  GITHUB_REF_NAME   branch (set automatically)
  DRY_RUN=1         show what would be posted, call nothing
  CHECK=1           only verify the token and print the account name
  CATCHUP_HOURS     how late a post may still go out (default 3)
  NOW               ISO time override, for testing only
"""
import csv, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

API = "https://graph.facebook.com/v21.0"
IG_USER_ID = os.environ.get("IG_USER_ID", "17841453286180522")  # @alphammotive
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEDULE = os.path.join(HERE, "schedule.csv")
POSTED = os.path.join(HERE, "posted.json")
DRY = os.environ.get("DRY_RUN") == "1"
CATCHUP = timedelta(hours=float(os.environ.get("CATCHUP_HOURS", "3")))
MAX_PER_RUN = 2


def call(method, path, params):
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not token:
        sys.exit("IG_ACCESS_TOKEN is not set.")
    q = urllib.parse.urlencode(dict(params, access_token=token))
    if method == "GET":
        req = urllib.request.Request(f"{API}/{path}?{q}")
    else:
        req = urllib.request.Request(f"{API}/{path}", data=q.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # never print the URL: it holds the token
        sys.exit(f"Instagram API error {e.code} on {method} /{path}: {e.read().decode()[:600]}")


def now_utc():
    if os.environ.get("NOW"):
        return datetime.fromisoformat(os.environ["NOW"]).astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def image_url(file):
    repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/posts/{urllib.parse.quote(file)}"


def load_posted():
    if os.path.exists(POSTED):
        with open(POSTED, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_posted(data):
    with open(POSTED, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def publish(ig_id, row):
    with open(os.path.join(HERE, "posts", row["caption_file"]), encoding="utf-8") as f:
        caption = f.read().strip()
    url = image_url(row["file"])
    c = call("POST", f"{ig_id}/media", {"image_url": url, "caption": caption})
    cid = c["id"]
    for _ in range(20):  # wait until Instagram has fetched the image
        st = call("GET", cid, {"fields": "status_code"}).get("status_code")
        if st == "FINISHED":
            break
        if st in ("ERROR", "EXPIRED"):
            sys.exit(f"Container for post {row['post_no']} failed with status {st}.")
        time.sleep(5)
    else:
        sys.exit(f"Container for post {row['post_no']} not ready after 100 s.")
    return call("POST", f"{ig_id}/media_publish", {"creation_id": cid})["id"]


def main():
    if os.environ.get("CHECK") == "1":
        me = call("GET", IG_USER_ID, {"fields": "username,media_count"})
        lim = call("GET", f"{IG_USER_ID}/content_publishing_limit", {"fields": "quota_usage,config"})
        print(f"Token OK for @{me.get('username')} ({me.get('media_count')} posts). Publishing quota: {lim}")
        return

    posted = load_posted()
    now = now_utc()
    due, missed = [], []
    with open(SCHEDULE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["approved"].strip().lower() != "yes" or row["post_no"] in posted:
                continue
            at = datetime.fromisoformat(row["publish_at"]).astimezone(timezone.utc)
            if at > now:
                continue
            (due if now - at <= CATCHUP else missed).append(row)

    for row in missed:
        print(f"SKIPPED post {row['post_no']}: scheduled {row['publish_at']}, more than "
              f"{CATCHUP} ago. Give it a new time in schedule.csv to post it.")
    if not due:
        print(f"Nothing due at {now.isoformat(timespec='minutes')}.")
        return

    ig_id = IG_USER_ID
    for row in due[:MAX_PER_RUN]:
        if DRY:
            print(f"DRY RUN: would publish post {row['post_no']} ({row['file']}) from {image_url(row['file'])}")
            continue
        media_id = publish(ig_id, row)
        posted[row["post_no"]] = {"media_id": media_id, "published_at": now.isoformat(timespec="seconds")}
        save_posted(posted)
        print(f"Published post {row['post_no']} as media {media_id}")


if __name__ == "__main__":
    main()
