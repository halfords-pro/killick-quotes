# Preserved Killick — His Daily Grievance

A static website that serves a fresh daily monologue from Preserved Killick, the perpetually aggrieved steward aboard HMS Surprise, in the tradition of Patrick O'Brian's Aubrey-Maturin novels.

Live at **[mybesttablecloth.com](https://mybesttablecloth.com)**

## How it works

A GitHub Actions workflow runs daily at 6am UTC. It calls the Anthropic API (Claude Haiku) with one of 15 rotating scenario prompts to generate a short Killick monologue, renders it into `index.html` using the HTML template, appends it to `quotes.jsonl`, regenerates the archive page, and commits the changes back to the repository. GitHub Pages serves the result.

## Setup

### 1. Repository secret

Add your Anthropic API key as a repository secret:

**Settings > Secrets and variables > Actions > New repository secret**

- Name: `ANTHROPIC_API_KEY`
- Value: your key

### 2. GitHub Pages

Enable GitHub Pages:

**Settings > Pages**

- Source: **Deploy from a branch**
- Branch: `main`, folder: `/ (root)`

### 3. Custom domain DNS

Add these DNS records for `mybesttablecloth.com`:

| Type  | Name | Value            |
|-------|------|------------------|
| A     | @    | 185.199.108.153  |
| A     | @    | 185.199.109.153  |
| A     | @    | 185.199.110.153  |
| A     | @    | 185.199.111.153  |
| CNAME | www  | nick-heppleston.github.io |

Then set the custom domain in **Settings > Pages > Custom domain** to `mybesttablecloth.com` and enable **Enforce HTTPS**.

### 4. Local development

```bash
cp .env.example .env
# Edit .env with your Anthropic API key

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate a quote locally
python generate.py

# View the result
open index.html
```

## Project structure

```
.
├── .github/workflows/killick.yml   # Daily cron workflow
├── archive_template.html           # HTML template for archive page
├── template.html                   # HTML template for daily quote
├── generate.py                     # Quote generation script
├── index.html                      # Generated daily quote page
├── archive.html                    # Generated archive page
├── quotes.jsonl                    # Append-only quote archive
├── CNAME                           # Custom domain for GitHub Pages
├── requirements.txt                # Python dependencies
└── .env.example                    # Environment variable template
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
