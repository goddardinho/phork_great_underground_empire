#!/usr/bin/env python3
"""
check_version_sync.py

Checks that the latest version in CHANGELOG.md matches the latest git tag.
Exits with code 0 if they match, 1 if not.
"""
import re
import subprocess
import sys

CHANGELOG = "CHANGELOG.md"

# Extract latest version from changelog
def get_changelog_version():
    with open(CHANGELOG) as f:
        for line in f:
            m = re.match(r"## v(\d+\.\d+\.\d+)", line)
            if m:
                return f"v{m.group(1)}"
    return None

# Get latest git tag (sorted by version)
def get_latest_git_tag():
    try:
        tags = subprocess.check_output([
            "git", "tag", "--list", "v*", "--sort=-v:refname"
        ], encoding="utf-8").split()
        return tags[0] if tags else None
    except Exception as e:
        print(f"Error getting git tags: {e}")
        return None

def main():
    changelog_version = get_changelog_version()
    git_tag = get_latest_git_tag()
    print(f"Changelog version: {changelog_version}")
    print(f"Latest git tag:    {git_tag}")
    if changelog_version == git_tag:
        print("✔ Versions match.")
        sys.exit(0)
    else:
        print("✘ Versions do NOT match!")
        answer = input(f"Create git tag {changelog_version}? [y/N]: ").strip().lower()
        if answer == "y":
            try:
                subprocess.run(["git", "tag", changelog_version], check=True)
                subprocess.run(["git", "push", "origin", changelog_version], check=True)
                print(f"Tag {changelog_version} created and pushed.")
                sys.exit(0)
            except subprocess.CalledProcessError as e:
                print(f"Error creating or pushing tag: {e}")
                sys.exit(2)
        else:
            print("No tag created.")
            sys.exit(1)

if __name__ == "__main__":
    main()
