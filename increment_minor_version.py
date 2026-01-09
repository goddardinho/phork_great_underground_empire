#!/usr/bin/env python3
"""
increment_minor_version.py

Increments the minor version in CHANGELOG.md (semantic versioning), adds a new section, and optionally creates a git tag.
"""
import re
import sys
import subprocess
from datetime import date

CHANGELOG = "CHANGELOG.md"

def get_latest_version():
    with open(CHANGELOG) as f:
        for line in f:
            m = re.match(r"## v(\d+)\.(\d+)\.(\d+)", line)
            if m:
                return tuple(map(int, m.groups()))
    return None

def increment_minor(version):
    major, minor, patch = version
    return (major, minor + 1, 0)

def prepend_changelog(new_version):
    today = date.today().isoformat()
    new_header = f"## v{new_version[0]}.{new_version[1]}.{new_version[2]} ({today})\n\n- _Describe changes for this release here._\n\n"
    with open(CHANGELOG) as f:
        content = f.read()
    with open(CHANGELOG, "w") as f:
        # Insert after the first line (usually # Changelog)
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith("# Changelog"):
            f.write(lines[0])
            f.write("\n" if not lines[1].strip() else "")
            f.write(new_header)
            f.writelines(lines[1:])
        else:
            f.write(new_header)
            f.write(content)
    print(f"Prepended new version section: v{new_version[0]}.{new_version[1]}.{new_version[2]}")

def create_git_tag(new_version):
    tag = f"v{new_version[0]}.{new_version[1]}.{new_version[2]}"
    subprocess.run(["git", "add", CHANGELOG], check=True)
    subprocess.run(["git", "commit", "-m", f"Bump version to {tag} in changelog"], check=True)
    subprocess.run(["git", "tag", tag], check=True)
    subprocess.run(["git", "push", "origin", tag], check=True)
    print(f"Tag {tag} created and pushed.")

def main():
    version = get_latest_version()
    if not version:
        print("Could not find a version in the changelog.")
        sys.exit(1)
    new_version = increment_minor(version)
    prepend_changelog(new_version)
    answer = input(f"Create and push git tag v{new_version[0]}.{new_version[1]}.{new_version[2]}? [y/N]: ").strip().lower()
    if answer == "y":
        try:
            create_git_tag(new_version)
        except subprocess.CalledProcessError as e:
            print(f"Error creating or pushing tag: {e}")
            sys.exit(2)
    else:
        print("No tag created.")

if __name__ == "__main__":
    main()
