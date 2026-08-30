# Contribution-maker

A small Python CLI that creates **backdated** synthetic commits to fill a GitHub
contribution graph. It appends a line to a file and creates a commit whose
author and committer timestamps are set to a chosen date (or random dates in a
range).

> **Disclaimer:** This tool fabricates activity and does not reflect real work.
> GitHub discourages and may **remove or exclude** synthetic/backdated commits
> from contribution graphs, and abusive use can flag your account. Use it only
> on repositories you own, at your own risk.

## Requirements

- Python 3.8+
- `git` installed, configured (`user.name` / `user.email`), with a remote to push to

## Usage

### Interactive

```bash
python main.py
```

You'll be prompted for the number of commits, repository path, filename, commit
message, and date range.

### Command line

```bash
python main.py --count 30 --repo /path/to/repo --file data.txt \
    --message "Graph activity" --start 2025-01-01 --end 2025-12-31 \
    --workdays-only --dry-run
```

| Option | Description |
| ------ | ----------- |
| `--count N` | Number of commits to make (default 20) |
| `--repo PATH` | Path to the git repository (default `.`) |
| `--file NAME` | File to append to (default `data.txt`) |
| `--message TEXT` | Commit message (default `graph-greener!`) |
| `--start YYYY-MM-DD` | Earliest allowed commit date (default: 1 year ago) |
| `--end YYYY-MM-DD` | Most recent allowed commit date (default: today) |
| `--workdays-only` | Only place commits Mon–Fri |
| `--dry-run` | Print the dates that would be used without committing/pushing |

## Development

```bash
python -m py_compile main.py   # syntax check
python main.py --dry-run --count 5   # preview without side effects
```

## License

MIT — see [LICENSE](LICENSE).
