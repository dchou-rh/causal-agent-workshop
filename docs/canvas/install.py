"""Cross-platform installer for the workshop Cursor Canvas template."""

import shutil
from pathlib import Path


def install_canvas() -> Path:
    repo_root = Path.cwd()
    projects_dir = Path.home() / ".cursor" / "projects"

    # Cursor encodes the workspace path as a slug: /Users/me/repo -> Users-me-repo
    raw_path = str(repo_root).replace("\\", "/").strip("/")
    if len(raw_path) > 1 and raw_path[1] == ":":
        raw_path = raw_path[0] + raw_path[2:]
    slug = raw_path.replace("/", "-")

    target_dir = projects_dir / slug / "canvases"

    # Fallback if the slug does not match (e.g. repo renamed after clone)
    if not target_dir.parent.exists() and projects_dir.exists():
        matches = [p for p in projects_dir.iterdir() if p.name.endswith(repo_root.name)]
        if matches:
            target_dir = matches[0] / "canvases"

    target_dir.mkdir(parents=True, exist_ok=True)
    src = repo_root / "docs" / "canvas" / "agent-comparison.canvas.tsx"
    dest = target_dir / "agent-comparison.canvas.tsx"

    shutil.copy2(src, dest)
    print(f"Canvas installed to:\n  {dest}")
    return dest


if __name__ == "__main__":
    install_canvas()
