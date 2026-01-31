# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Daily News Bot** - An automated financial news aggregation system that scrapes, translates, and generates daily HTML news reports using Claude AI.

- **Owner**: Vincent (product manager, non-programmer)
- **Language**: Python 3.x
- **Deployment**: Vercel (static site hosting)
- **Repository**: https://github.com/vshen009/daily-news-bot
- **Live Site**: https://news.ai.0814.host

---

## Development Commands

### Running the Application

```bash
# Main entry point - fetches news, translates, generates HTML
cd news_bot
python main.py

# Simple runner (alternative entry point)
python run_simple.py

# View database statistics
python show_database_info.py

# Show all articles in database
python show_all_articles.py

# Process raw articles from database
python process_raw_articles.py

# Clean and regenerate all HTML
python clean_and_regenerate.py
```

### Environment Setup

```bash
# Install dependencies
pip install -r news_bot/requirements.txt

# Copy environment template and configure
cp news_bot/.env.example news_bot/.env
# Edit news_bot/.env to add ANTHROPIC_API_KEY

# The API base URL uses a proxy: https://open.bigmodel.cn/api/anthropic
# Model: claude-3-5-sonnet-20241022
```

### Git Workflow

**CRITICAL**: Main branch is protected. All changes must go through PRs.

```bash
# Create feature branch
git checkout -b feature/description

# Make changes and commit
git add .
git commit -m "✨ Description"

# Push and create PR
git push origin feature/description
gh pr create --title "Title" --body "Description"

# Merge PR (squash merge, delete branch)
gh pr merge --squash --delete-branch
```

**Never**:

- Direct commit to main
- Force-push to main
- Use same name for branch and tag
- Use rebase when pulling (use `git pull origin main --no-rebase`)

---

## Architecture

### Core Data Flow

```
Scraper → Deduplicator → Database → Translator → AI Comment → HTML Generator → Public/
          ↓                            ↓
      Check cache                Only process NEW articles
```

**Key Optimization**: The system uses SQLite database to avoid reprocessing articles.

- Articles are deduplicated by `title` (Chinese) and `title_original` (English)
- Cached articles reuse existing translations and AI comments
- Only NEW articles trigger API calls (70-85% cost reduction)

### Module Structure

**news_bot/src/** - Core modules:

| Module              | Purpose                                         | Key Functions                                                  |
| ------------------- | ----------------------------------------------- | -------------------------------------------------------------- |
| `scraper.py`        | Fetch news from configured sources              | `fetch_all_sources()`                                          |
| `deduplicator.py`   | Remove duplicates within batch                  | `deduplicate_articles()`                                       |
| `database.py`       | SQLite CRUD operations                          | `article_exists()`, `save_article()`, `get_article_by_title()` |
| `translator.py`     | Translate English articles to Chinese           | `translate_articles()`                                         |
| `ai_comment.py`     | Generate professional insights                  | `generate_comment()`, `generate_comments()`                    |
| `scorer.py`         | Calculate news importance scores                | `calculate_score()`                                            |
| `html_generator.py` | Generate daily HTML reports                     | `HTMLGenerator.generate()`                                     |
| `index_updater.py`  | Update homepage with recent news                | `IndexUpdater.update_index()`                                  |
| `models.py`         | Data models (NewsArticle, Category, NewsSource) | -                                                              |
| `config.py`         | Global configuration                            | `Config` class                                                 |

**news_bot/main.py** - Main orchestrator with 9-step process:

1. Config validation
2. Database initialization
3. Fetch all sources
4. **Deduplication** - Separate new vs cached articles
5. **Translate** only new articles
6. **Generate AI comments** only for new articles
7. **Select TOP 15** news (scoring algorithm)
8. Generate HTML (daily report)
9. Update homepage

### Directory Layout

```
daily-news-bot/
├── public/                    # ALL HTML files (Vercel output)
│   ├── index.html            # Homepage (news list)
│   └── YYYY-MM-DD.html       # Daily reports
├── news_bot/
│   ├── src/                  # Core modules
│   ├── config/
│   │   └── sources.yaml      # News source configuration
│   ├── data/
│   │   └── news.db           # SQLite database (committed to repo)
│   ├── templates/
│   │   └── daily_news.html   # Jinja2 template for daily reports
│   ├── main.py              # Entry point
│   └── .env                 # API keys (NOT committed)
└── vercel.json              # Vercel routing config
```

### Configuration Files

**`news_bot/config/sources.yaml`** - News sources configuration:

- Define sources with URL, RSS feed, category, priority
- Toggle sources on/off with `enabled: true/false`

**`.gitignore`** - Important rules:

- `news_bot/data/news.db` is **EXPLICITLY INCLUDED** (committed to repo)
- `*.db-shm`, `*.db-wal`, `backup_*.db` are ignored
- `.env` is ignored (API secrets)
- `Claude.md` and `memory.md` are ignored (internal docs)

**`vercel.json`** - Routing rules:

- `/` → `/public/index.html`
- `/*.html` → `/public/*.html`
- Static file caching headers



---

## Important Implementation Details

### Database Deduplication

**Unique constraint**: `UNIQUE(title, title_original)` on articles table

- Chinese articles use `title` field
- English articles use `title_original` field
- Check existence with `db_manager.article_exists(title, title_original)`

### AI API Usage

**Provider**: Zhipu AI proxy (https://open.bigmodel.cn/api/anthropic)

- Base URL is proxied through Zhipu
- Model: `claude-3-5-sonnet-20241022`
- Environment variable: `ANTHROPIC_API_KEY` in `news_bot/.env`

**Rate limiting**: Zhipu API has concurrency limits (429 errors). Consider adding delays between requests if processing many new articles.

### HTML Generation

**Jinja2 template**: `news_bot/templates/daily_news.html`

- Renders 3 news sections
- Featured article (first in section) gets special styling

**Output paths**:

- Daily report: `public/{date}.html` (e.g., `public/2026-01-27.html`)
- Homepage: `public/index.html` (auto-updated with recent 30 days)

### Date Handling

- **Date format**: `%Y-%m-%d` (defined in `Config.DATE_FORMAT`)
- **Timezone**: System local time (no explicit timezone handling)
- **Max article age**: 48 hours (`Config.MAX_AGE_HOURS`)

---

## Testing

No formal test suite currently exists. Manual testing:

1. Run `python news_bot/main.py`
2. Check output in `public/` directory
3. Verify database with `python news_bot/show_database_info.py`

---

## Deployment

**Vercel**:

- Static site hosting from `public/` directory
- No build process required
- GitHub Actions trigger: `.github/workflows/daily-news.yml` (auto-runs daily)
- Environment variables must be configured in Vercel dashboard: `ANTHROPIC_API_KEY`

**Note**: The project was recently separated from a monorepo (`claude-code-projects`). Vercel project must be connected to the new repository.



---

## Browser Automation

Use `agent-browser` for web automation. Run `agent-browser --help` for all commands.

Core workflow:

1. `agent-browser open <url>` - Navigate to page
2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
3. `agent-browser click @e1` / `fill @e2 "text"` - Interact using refs
4. Re-snapshot after page changes

---

## Special Notes for This Project

1. **User is a non-programmer** - Provide clear explanations, avoid jargon when possible
2. **Chinese language preferred** - Vincent prefers communication in Chinese
3. **Database is version-controlled** - Unlike typical projects, `news_bot/data/news.db` is committed to Git
4. **Git history matters** - All commits should follow emoji prefix convention (✨, 🔧, 📝, etc.)
5. **Main branch protection** - Always work on feature branches, use PRs for main
