"""Contribution-maker: backdate synthetic commits to fill a GitHub contribution graph."""

import argparse
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta, timezone

DEFAULT_MESSAGE = "graph-greener!"


def git(cwd, *args, env=None):
    """Run a git subcommand, raising a clear error on failure."""
    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)
    result = subprocess.run(
        ["git", *args], cwd=cwd, env=cmd_env, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed (exit {result.returncode}):\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def check_repo(repo_path):
    """Verify repo_path is a git repository with a configured user identity."""
    if not os.path.isdir(repo_path):
        raise SystemExit(f"Directory does not exist: {repo_path}")
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise SystemExit(f"Not a git repository: {repo_path}")
    for key in ("user.name", "user.email"):
        if not git(repo_path, "config", key):
            raise SystemExit(
                f"Git {key} is not set. Configure it (e.g. git config --global {key} ...) first."
            )


def generate_dates(count, start, end, workdays_only=False):
    """Generate `count` random dates in UTC within [start, end).

    Ensures dates are unique (each covers a distinct second) for realism.
    """
    total_seconds = int((end - start).total_seconds())
    if total_seconds <= 0:
        raise ValueError("End date must be after start date.")
    if total_seconds < count:
        raise ValueError(
            f"Date range only spans {total_seconds} seconds but {count} commits requested."
        )

    picks = set()
    while len(picks) < count:
        candidate = start + timedelta(seconds=random.randrange(total_seconds + 1))
        if workdays_only and candidate.weekday() >= 5:
            continue
        picks.add(int(candidate.timestamp()))
    return [datetime.fromtimestamp(ts, tz=timezone.utc) for ts in picks]


def make_commit(date, repo_path, filename, message, dry_run):
    """Append a line to filename and create a commit dated `date` (UTC ISO 8601)."""
    filepath = os.path.join(repo_path, filename)
    env = {
        "GIT_AUTHOR_DATE": date.isoformat(),
        "GIT_COMMITTER_DATE": date.isoformat(),
    }
    if dry_run:
        print(f"[dry-run] would append and commit at {date.isoformat()}")
        return

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"Commit at {date.isoformat()}\n")
    git(repo_path, "add", filename)
    git(repo_path, "commit", "-m", message, env=env)


def parse_dates(start_text, end_text):
    """Parse YYYY-MM-DD date strings to timezone-aware UTC midnights."""
    def to_midnight(text):
        return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    start = to_midnight(start_text)
    end = to_midnight(end_text)
    # Make end exclusive: 00:00:00 of end day means "through end-1".
    return start, end


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Backdate synthetic commits to a git repo to fill a GitHub "
            "contribution graph. Runs interactively if no options are given."
        )
    )
    parser.add_argument("--count", type=int, help="number of commits to make (default 20)")
    parser.add_argument("--repo", default=".", help="path to the git repository (default: .)")
    parser.add_argument("--file", default="data.txt", help="file to append to (default: data.txt)")
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="commit message")
    parser.add_argument(
        "--start", help="earliest commit date as YYYY-MM-DD (default: 1 year ago)"
    )
    parser.add_argument(
        "--end", help="most recent commit date as YYYY-MM-DD (default: today)"
    )
    parser.add_argument(
        "--workdays-only", action="store_true", help="only place commits on Mon-Fri"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print dates without committing"
    )
    return parser


def collect_inputs(args):
    """Merge CLI args with interactive prompts; return config tuple.

    Prompts run only when stdin is a terminal (not piped/redirected), so the
    tool is safe to drive non-interactively via flags alone.
    """
    interactive = sys.stdin.isatty()
    today = datetime.now(timezone.utc).date()
    default_start = (today - timedelta(days=365)).isoformat()
    default_end = today.isoformat()

    def ask(prompt, default, cast=str, valid=None):
        if not interactive:
            return default
        while True:
            try:
                raw = input(f"{prompt} (default {default}): ").strip()
            except EOFError:
                print()
                return default
            if not raw:
                return default
            try:
                value = cast(raw)
            except ValueError:
                print("Invalid input, try again.")
                continue
            if valid and not valid(value):
                print("Out of range, try again.")
                continue
            return value

    count = args.count
    if count is None:
        count = ask("How many commits do you want to make", 20, int, lambda v: v > 0)

    repo = ask("Enter the path to your local git repository", args.repo or ".")
    filename = ask("Enter the filename to modify for commits", args.file or "data.txt")
    message = ask("Enter the commit message", args.message or DEFAULT_MESSAGE)
    start_text = ask("Earliest commit date", args.start or default_start)
    end_text = ask("Most recent commit date", args.end or default_end)
    workdays_only = args.workdays_only
    dry_run = args.dry_run

    return count, repo, filename, message, start_text, end_text, workdays_only, dry_run


def main():
    args = build_parser().parse_args()

    count, repo, filename, message, start_text, end_text, workdays_only, dry_run = (
        collect_inputs(args)
    )

    start, end = parse_dates(start_text, end_text)

    check_repo(repo)

    try:
        dates = generate_dates(count, start, end, workdays_only=workdays_only)
    except ValueError as e:
        raise SystemExit(str(e))

    dates.sort()
    print(f"\nMaking {count} commits in repo: {repo}")
    print(f"Modifying file: {filename}")
    if dry_run:
        print("DRY RUN - nothing will be written or committed.\n")

    for i, date in enumerate(dates):
        print(f"[{i+1}/{count}] Committing at {date.isoformat()}")
        make_commit(date, repo, filename, message, dry_run)

    if dry_run:
        print("\nDry run complete.")
        return

    print("\nPushing commits to your remote repository...")
    git(repo, "push")
    print("All done! Check your GitHub contribution graph in a few minutes.")
    print("Tip: Use a dedicated repository for best results. Happy coding!")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
