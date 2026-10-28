# Monthly invoice → Telegram

On the 1st of every month this builds the invoice PDF (same layout as your Excel,
issuer name: **ALEFIYA SHABBIR PATRAWALA**) and sends it to you on Telegram.

## One-time setup (about 10 minutes, free)

### 1. Make a Telegram bot
1. In Telegram, open **@BotFather** → send `/newbot` → follow the prompts.
2. Copy the **bot token** it gives you (looks like `123456:ABC-DEF...`).
3. Open your new bot and press **Start** (send it any message). Required, or it can't message you.

### 2. Get your chat ID
Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser.
Find `"chat":{"id": 123456789` – that number is your **chat ID**.

### 3. Put the project on GitHub
1. Create a **private** repository and upload everything in this folder
   (including the hidden `.github` folder).
2. Repo → **Settings → Secrets and variables → Actions → New repository secret**. Add:
   - `TELEGRAM_BOT_TOKEN` = the token from step 1
   - `TELEGRAM_CHAT_ID`   = the number from step 2

### 4. Create the uv lockfile (once)
On your computer, inside this folder:
```
uv lock
```
Commit the generated `uv.lock` to the repo. (It pins exact dependency versions.)

### 5. Test it
Repo → **Actions → Monthly invoice → Run workflow**. The PDF should arrive on Telegram.
After that it runs by itself at 9:30 AM IST on the 1st of each month.

## Changing things
Everything lives in `config.json`:

| Setting | Meaning |
|---|---|
| `basic_amount` | Monthly amount. Change here if the rent changes. |
| `gst_applicable` | `false` = CGST/SGST print as 0 (as in your Excel). `true` = 9% + 9% added. |
| `billing_month` | `"current"` → invoice dated 1 Nov says "Month of November-2026". `"previous"` → says "October-2026". |
| `bill_no_format` | Bill number pattern. Default `{date:%Y%m%d}-{counter:03d}` gives `20261101-001`. Use `{date:%Y%m%d}{counter:03d}` for no hyphen. |
| `counter_start` | Where the counter begins (default 1). Set it higher to continue an existing series. |

## Bill numbers
Format: **date of the invoice + a counter that only ever goes up**
(`20261101-001`, `20261201-002`, `20270101-003`, ...). The counter never resets.

The counter lives in `state.json`. After each successful send, the workflow commits
the updated file back to the repo ("Update bill counter"). Don't delete or edit it by hand.
- A failed run doesn't use up a number.
- Re-running in the same month (e.g. a test) re-uses that month's number instead of making a new one.

## Run it on your own computer instead
```
uv sync                                        # install dependencies
uv run main.py --no-send                       # preview PDF in ./output (counter untouched)
uv run main.py --no-send --date 2026-12-01     # preview another month
TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... uv run main.py   # make and send
```
Running locally and on GitHub both update their own `state.json`, so pick one place
to do the real monthly send.

## Notes
- Scheduled GitHub runs can start a few minutes late. GitHub also pauses schedules on
  public repos after 60 days without activity; keep the repo private, or press
  "Run workflow" occasionally.
- Never commit your bot token to the repo; keep it in Secrets only.
