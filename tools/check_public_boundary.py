#!/usr/bin/env python3
"""Check tracked files against this repository's public release boundary."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_PATH_PARTS = (
    "data/",
    "raw/",
    "derived/",
    "results/",
    "outputs/",
    "figures/",
    "plots/",
    "downloads/",
    "archives/",
    "archive/",
    "notebooks/",
    "external/",
    "external_data/",
    "source_materials/",
    "metadata/",
    "access_logs/",
    ".cache/",
)
PROHIBITED_SUFFIXES = (
    ".csv", ".tsv", ".jsonl", ".parquet", ".feather", ".h5", ".hdf5",
    ".mat", ".npy", ".npz", ".pkl", ".pickle", ".nwb", ".zip", ".tar",
    ".tgz", ".7z", ".rar", ".png", ".jpg", ".jpeg", ".tif", ".tiff",
    ".svg", ".pdf", ".ipynb",
)
# Fragmented strings prevent this checker from matching its own marker catalog.
UNSUPPORTED_MARKERS = ("international" + " brain" + " lab",)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RESULT_PATTERN = re.compile(r"\b(?:r|p)\s*(?:=|<|>)\s*[+-]?\d")


def _run_git(arguments: list[str]) -> bytes:
    """Run Git from the repository root and return its standard output.

    Args:
        arguments: Arguments following the `git` executable.

    Returns:
        Standard output produced by Git.

    Raises:
        RuntimeError: If Git reports an error.
    """
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Git command failed: {message}")
    return completed.stdout


def tracked_paths() -> list[Path]:
    """Return repository-relative paths currently tracked by Git.

    Returns:
        Tracked paths in the current Git index.
    """
    output = _run_git(["ls-files", "-z"])
    return [Path(value.decode("utf-8")) for value in output.split(b"\0") if value]


def tracked_text(path: Path) -> str | None:
    """Read a tracked blob from Git without touching local untracked files.

    Args:
        path: Repository-relative path already reported by `tracked_paths`.

    Returns:
        UTF-8 text for the indexed blob, or `None` when it is binary.

    Raises:
        RuntimeError: If Git cannot read the indexed blob.
    """
    content = _run_git(["show", f":{path.as_posix()}"])
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan() -> list[str]:
    """Inspect indexed paths and indexed UTF-8 text for boundary violations.

    The scanner reads Git's tracked blobs rather than working-tree files. It does
    not traverse local directories, open untracked paths, or access local data.

    Returns:
        Human-readable violation descriptions. An empty list means no violation
        was found by the checker.
    """
    violations: list[str] = []
    for path in tracked_paths():
        normalized = path.as_posix().lower()
        if any(part in normalized for part in PROHIBITED_PATH_PARTS):
            violations.append(f"prohibited tracked path: {path}")
            continue
        if normalized.endswith(PROHIBITED_SUFFIXES):
            violations.append(f"prohibited tracked file type: {path}")
            continue
        text = tracked_text(path)
        if text is None:
            violations.append(f"binary tracked file requires boundary review: {path}")
            continue
        if path == Path("docs/INTRODUCTION.md"):
            continue
        lowered = text.lower()
        for marker in UNSUPPORTED_MARKERS:
            if marker in lowered:
                violations.append(f"unsupported public marker in {path}: {marker}")
        if DOI_PATTERN.search(text):
            violations.append(f"unsupported public marker in {path}: DOI-like identifier")
        if EMAIL_PATTERN.search(text):
            violations.append(f"email-like identifier in {path}")
        if RESULT_PATTERN.search(text):
            violations.append(f"result-like numerical claim in {path}")
    return violations


def main() -> int:
    """Run the indexed-file boundary scan and print a concise outcome.

    Returns:
        Zero when no violations are found; one otherwise.
    """
    violations = scan()
    if violations:
        print("Public boundary check failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("Public boundary check passed for indexed paths and text.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
