<div align="center">

# 🌱 Contribution-maker

**Backdate synthetic commits to fill your GitHub contribution graph.**

A small, dependency-free Python CLI that appends a line to a file and creates a
commit whose author and committer timestamps are set to a chosen date (or random
dates in a range) — so your contribution graph stays green, even on days you
didn't code.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](#requirements)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](#contributing)

</div>

> ⚠️ **Disclaimer**
>
> This tool fabricates activity and does not reflect real work. GitHub
> discourages and may **remove or exclude** synthetic and backdated commits from
> contribution graphs, and abusive use can flag your account. Use it only on
> repositories you own, at your own risk.

---

## ✨ Features

- 🕒 **Backdated commits** — set both author and committer dates
- 📅 **Custom date ranges** — target specific weeks/months
- 🧮 **Unique timestamps** — every commit is a distinct second (no collisions)
- 🌐 **Timezone-safe (UTC)** — commits land on the correct day on GitHub
- 💼 **Workdays-only mode** — keep weekend commits off the graph
- 👀 **Dry-run preview** — see what would be committed, without touching anything
- ⚙️ **Fully scriptable** — every option is a CLI flag
- 🛡️ **Guards** — validates the repo, git identity, and date ranges with clear errors

---

## 📋 Requirements

- **Python 3.8+** (stdlib only — no third-party dependencies)
- **git** installed and configured:
  - `user.name` and `user.email` must be set
  - a remote must exist if you plan to push

---

## 🚀 Installation

You can run it directly from the repo, or install it as a package:

```bash
# Option A — run from source
git clone https://github.com/ALFRED-OP/Contribution-maker.git
cd Contribution-maker
python main.py --help

# Option B — install with pip
pip install .
contribution-maker --help
```

---

## 🧑‍💻 Usage

### Interactive

```bash
python main.py
```

You'll be prompted for the number of commits, repository path, filename, commit
message, and date range. Prompts only appear when running interactively.

### Command line

All options are available as flags for scripting and automation:

```bash
python main.py \
    --count 30 \
    --repo /path/to/repo \
    --file data.txt \
    --message "Graph activity" \
    --start 2025-01-01 \
    --end 2025-12-31 \
    --workdays-only \
    --dry-run
```

### Options

| Option | Description |
| ------ | ----------- |
| `--count N` | Number of commits to make (default `20`) |
| `--repo PATH` | Path to the git repository (default `.`) |
| `--file NAME` | File to append to (default `data.txt`) |
| `--message TEXT` | Commit message (default `graph-greener!`) |
| `--start YYYY-MM-DD` | Earliest allowed commit date (default: 1 year ago) |
| `--end YYYY-MM-DD` | Most recent allowed commit date (default: today) |
| `--workdays-only` | Only place commits Mon–Fri |
| `--dry-run` | Print the dates that would be used, without committing/pushing |

---

## 💡 Examples

**Preview a month of activity (no changes made):**

```bash
python main.py --count 30 --start 2025-06-01 --end 2025-06-30 --dry-run
```

**Fill the last 3 months, weekdays only:**

```bash
python main.py --count 60 --start 2025-05-01 --end 2025-07-31 --workdays-only
```

**Each commit uses a custom message on a specific repo:**

```bash
python main.py --count 10 --repo ~/projects/notes --file journal.md --message "daily notes"
```

---

## 🔧 How it works

1. Random (or given-range) UTC timestamps are generated — one per commit, all
   unique.
2. For each commit, a line is appended to the target file:
   ```
   Commit at 2025-06-15T14:22:08+00:00
   ```
3. The file is staged, and a commit is created with both
   `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` set to the backdated timestamp.
4. Once all commits are made, the tool pushes to the remote
   (`git push`). Commit batching ensures all dates appear in the contribution
   history.

---

## 🛠️ Development

```bash
python -m py_compile main.py              # syntax check
python main.py --dry-run --count 5        # preview without side effects
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an
[issue](https://github.com/ALFRED-OP/Contribution-maker/issues) or submit a
[pull request](https://github.com/ALFRED-OP/Contribution-maker/pulls).

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
