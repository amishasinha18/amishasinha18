# Setup: Amisha's profile README

Folder layout (upload everything inside this folder to the repo root):

```
amishasinha18/
├── README.md
├── SETUP.md
├── .gitignore
├── .github/workflows/metrics.yml
├── assets/
│   ├── portrait.png        (already generated)
│   └── pipeline.svg        (already generated)
└── scripts/
    ├── make_portrait.py
    └── make_pipeline.py
```

## 1. Create the repo
1. GitHub -> **New repository**.
2. Name: exactly `amishasinha18`. Set it to **Public**. Tick "Add a README".
3. Upload all files from this folder (drag and drop on the repo page works, or use git).
   Keep the `.github/workflows` folder structure exactly as shown.

## 2. Make the token (for calendar, stats, achievements)
1. GitHub -> Settings -> Developer settings -> Personal access tokens -> **Tokens (classic)** -> Generate new token (classic).
2. Scopes: `repo`, `read:org`, `read:user`. Expiration: your choice (note the date, you will need to renew it).
3. Copy the token.
4. In the repo: Settings -> Secrets and variables -> Actions -> **New repository secret**.
   Name: `METRICS_TOKEN`, Value: the token.
   Never paste the token into a file or a chat.

## 3. Run the workflow once
Repo -> **Actions** tab -> **Metrics** -> **Run workflow**.
It takes a few minutes. It creates:
- `assets/metrics.isocalendar.svg`
- `assets/metrics.stats.svg`
- `assets/metrics.achievements.svg`

Until it finishes, those three images show as broken in the README. That is normal.
If a step fails, open the run log and read the error. The most common causes are a wrong token scope or a missing secret.

## 4. Regenerate the portrait or pipeline (optional)
```bash
pip install pillow
python scripts/make_portrait.py path/to/photo.png   # -> assets/portrait.png
python scripts/make_pipeline.py                      # -> assets/pipeline.svg
```
Do not commit your original photo (`.gitignore` already skips files named `photo.*`).

## 5. Check
Open github.com/amishasinha18. The README shows on your profile.
Contribution-based visuals look sparse at first. They fill up as you commit more.

## Notes
- I could not run the GitHub Actions workflow from here, so I have not tested it end to end. If the lowlighter/metrics options have changed, its docs are at github.com/lowlighter/metrics.
- Profile views counter starts at 0 and grows over time.
- IPC_FRAMEWORK has no live link. Add one in the table if you deploy it.
