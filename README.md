# Daily Message of Support

This repository sends a daily email — a supportive message, four random self-care activities, and a featured YMHC resource — to a subscriber list. It runs automatically every morning via a scheduled GitHub Actions workflow, with no server or hosting required.

## How it works

1. `.github/workflows/daily_email.yml` runs on a daily cron schedule (and can be triggered manually).
2. The workflow checks out the repo, installs Python dependencies, and runs [`daily_email.py`](daily_email.py).
3. `daily_email.py`:
   - Picks one random message from `data/messages_of_support.txt`, four unique random activities from `data/selfcare_activities.txt`, one random resource from `data/ymhc_resources.json`, and one random background image from `data/backgrounds/`.
   - Renders an HTML email (table-based layout for email-client compatibility) and writes a local copy to `preview.html`.
   - Sends the email via SMTP using `smtplib`.
4. Images referenced in the email (logo, background photos) are **not attached** — they're loaded by email clients from the jsDelivr CDN, which serves the `main` branch of this repo directly (`REPO_RAW_URL` in `daily_email.py`). This means image changes only need to be pushed to `main`; no redeploy step is required.
5. After a successful send, the workflow commits a timestamp file (`.github/data/last_run.txt`) back to the repo. This resets GitHub's 60-day inactivity clock that would otherwise auto-disable the schedule — see [Keeping the schedule alive](#6-keeping-the-schedule-alive).

## Repository layout

| Path | Purpose |
|---|---|
| `daily_email.py` | Main script: loads content, builds the HTML email, sends it |
| `data/messages_of_support.txt` | One supportive message per line |
| `data/selfcare_activities.txt` | One self-care activity per line |
| `data/ymhc_resources.json` | List of `{service_title, description, link}` resource objects |
| `data/img/` | Logo and static images used in the email |
| `data/backgrounds/` | Photos randomly used as the message-block background |
| `tools/batch_overlay.py` | One-off utility to apply a brand-color overlay to a batch of images (see below) |
| `.github/workflows/daily_email.yml` | Scheduled GitHub Action that runs the script |
| `preview.html` | Auto-generated local preview of the most recently built email |

## Running and maintaining this app

### 1. Prerequisites

- Python 3.10+ (matches the version pinned in the workflow)
- An SMTP-capable email account (Gmail with an App Password works well)
- Write access to this GitHub repository (for Actions secrets/settings and for pushing content changes)

### 2. Local setup

```bash
git clone <this-repo-url>
cd selfcare-message-emails
pip install -r requirements.txt
cp .env.example .env   # then fill in real values
```

Edit `.env`:

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
RECIPIENT_EMAIL=recipient_group@example.com
```

If using Gmail, `EMAIL_PASSWORD` must be a 16-character **App Password** (Google Account → Security → 2-Step Verification → App Passwords), not your normal login password — Gmail rejects plain-password SMTP logins.

### 3. Run it locally

```bash
python daily_email.py
```

- On success it prints `Email sent successfully!` and writes `preview.html`, which you can open directly in a browser to check formatting before trusting it in an inbox.
- If required env vars are missing, it prints exactly which ones and exits with status 1 without attempting to send.
- Note: every run sends a *real* email to `RECIPIENT_EMAIL`. Point `RECIPIENT_EMAIL` at a test address while iterating, or comment out the `send_message` call and just inspect `preview.html`.

### 4. Production configuration (GitHub Actions secrets)

The workflow reads five values as repository secrets:

| Secret | Description |
|---|---|
| `EMAIL_HOST` | SMTP server, e.g. `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port, e.g. `587` |
| `EMAIL_USER` | Sending email address |
| `EMAIL_PASSWORD` | SMTP password / app password |
| `RECIPIENT_EMAIL` | Recipient address, or comma-separated list |

To set these: GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **Repository secrets** → **New repository secret**, and add each of the five above.

If you'd rather keep `RECIPIENT_EMAIL` as a non-sensitive **variable** instead of a secret (it's visible in plain text either way if someone can trigger the workflow), add it under the **Variables** tab instead and change `${{ secrets.RECIPIENT_EMAIL }}` to `${{ vars.RECIPIENT_EMAIL }}` in `daily_email.yml`.

### 5. The schedule

`.github/workflows/daily_email.yml`:

```yaml
on:
  schedule:
    - cron: '30 14 * * *'   # 14:30 UTC ≈ 9:30 AM Eastern
  workflow_dispatch:        # manual "Run workflow" button
```

- GitHub cron schedules run in UTC and are **not** DST-aware, so the actual local delivery time drifts by an hour between EST and EDT. Adjust the cron expression twice a year if exact local time matters, or accept the ±1hr drift.
- Cron-triggered runs can be delayed by GitHub during periods of high load — treat "9:30 AM" as approximate, not exact.
- Use **Actions → Daily Message of Support → Run workflow** to trigger a send manually at any time (useful for testing secrets after rotating them, or resending after a fix).

### 6. Keeping the schedule alive

GitHub automatically **disables** scheduled workflows in a repository after **60 days with no commits/pushes** to the repo. Because this workflow only sends email and otherwise doesn't touch the repo, the final steps of the job commit a small marker file back to `main`:

```yaml
permissions:
  contents: write   # top of the workflow file

- name: Record last successful run
  run: |
    mkdir -p .github/data
    date -u +"%Y-%m-%dT%H:%M:%SZ" > .github/data/last_run.txt

- name: Commit last run marker
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add .github/data/last_run.txt
    git diff --staged --quiet && exit 0
    git commit -m "chore: record last successful daily email run [skip ci]"
    git push
```

This requires the repo's **Settings → Actions → General → "Workflow permissions"** to be set to **"Read and write permissions"**. If it's set to "Read repository contents permission" (GitHub's default for new repos), the commit/push step fails with a 403 — check this first if `.github/data/last_run.txt` stops updating.

**Maintenance checklist if the email ever stops arriving:**

1. Check the **Actions** tab — has the workflow run recently? No recent runs usually means the schedule was disabled.
2. Go to **Settings → Actions → General**; if Actions or the schedule are shown as disabled, re-enable them (this can happen independently of the 60-day rule too, e.g. after long personal-repo inactivity).
3. Check whether `.github/data/last_run.txt` was updated after the most recent expected run — if not, the commit-back step is failing (see the permissions note above), meaning the 60-day clock isn't actually being reset even though emails may still be sending.
4. Confirm none of the five secrets have expired or been rotated (e.g. a Gmail App Password revoked during a security review).

### 7. Updating email content

All content lives in plain data files — no code changes needed for routine updates:

- **Add a supportive message**: append a new line to `data/messages_of_support.txt`.
- **Add a self-care activity**: append a new line to `data/selfcare_activities.txt`.
- **Add/edit a featured resource**: add an object to the `data/ymhc_resources.json` array:
  ```json
  {
    "service_title": "Name of the program",
    "description": "One or two sentence description.",
    "link": "https://example.org/program"
  }
  ```
- **Add a background photo**: drop a `.jpg`/`.jpeg`/`.png` file into `data/backgrounds/`. It's picked up automatically (no filename convention required) and served via the jsDelivr CDN once pushed to `main`.

Commit and push any of the above to `main` — no redeploy or workflow change is required, since content is read fresh from the repo on every run and images are served live from the CDN.

> **jsDelivr caching note**: jsDelivr caches files served from the `main` branch for up to ~24 hours (also purges automatically on new commits in many cases, but don't rely on that). If a newly added background image doesn't show up immediately in a test send, wait a bit or manually purge it at `https://purge.jsdelivr.net/gh/YMHC-Charitable-Foundation/selfcare-message-emails@main/<path>`.

### 8. Image tooling (`tools/batch_overlay.py`)

A helper script for applying the brand color as a semi-transparent overlay to a batch of source photos before adding them to `data/backgrounds/`:

```bash
pip install Pillow   # not in requirements.txt — install ad hoc for this one-off tool
```

1. Place source images in `tools/image_input/`.
2. Run `python tools/batch_overlay.py`.
3. Overlaid results are written to `tools/image_output/` (color/opacity are hardcoded in the script — `COLOR_MAIN = "#0f777c"`, `OPACITY = 0.4` — edit the script directly to change them).
4. Move the finished files from `tools/image_output/` into `data/backgrounds/` and commit.

This tool is not run automatically as part of the daily workflow — it's a manual pre-processing step for whoever is curating background images.

### 9. Managing recipients

`RECIPIENT_EMAIL` accepts a single address or a comma-separated list. For a larger or self-serve subscriber list, consider pointing it at a mailing list address (e.g. a Google Group) rather than editing the secret every time someone joins or leaves. The unsubscribe instructions in the email footer direct recipients to email `daily-message-support+unsubscribe@ymhc.ngo` — make sure that mailbox/alias is actually monitored and subscribers are removed from `RECIPIENT_EMAIL` accordingly, since the script has no automated unsubscribe handling.

### 10. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `Error: Missing environment variables: ...` in Action logs | One of the five secrets isn't set, or its name doesn't exactly match `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_USER` / `EMAIL_PASSWORD` / `RECIPIENT_EMAIL` |
| Workflow succeeds (green check) but no email arrives | The script only *prints* on send failure (`except Exception as e: print(...)`) rather than failing the job — check the "Send Daily Email" step logs for a `Failed to send email: ...` line even on an apparently successful run |
| `smtplib.SMTPAuthenticationError` | Wrong password, or (Gmail) using your normal password instead of an App Password; confirm 2-Step Verification is enabled if required |
| Workflow no longer runs on schedule | See [Keeping the schedule alive](#6-keeping-the-schedule-alive) |
| Email renders oddly in a specific client (e.g. Outlook) | Run locally and open `preview.html` first to isolate a content bug from a client-rendering quirk; the template already includes several Outlook-specific CSS resets |
| Background image or logo missing in the email | Confirm the file was actually pushed to the `main` branch (the CDN serves `main`, not local or feature-branch state), and allow time for the jsDelivr cache to catch up |

## License

See [LICENSE](LICENSE).
