#!/usr/bin/env python3
"""
version_manager.py

- Checks if the latest version in CHANGELOG.md matches the latest git tag.
- If not, offers to create and push the tag, handling duplicate branch/tag conflicts.
- Can increment the minor version, prepend to changelog, and create/push the tag.

Usage:
  python3 version_manager.py check
  python3 version_manager.py bump-minor
"""
import re
import sys
import subprocess
from datetime import date

CHANGELOG = "CHANGELOG.md"

def get_latest_changelog_version():
    with open(CHANGELOG) as f:
        for line in f:
            m = re.match(r"## v(\d+)\.(\d+)\.(\d+)", line)
            if m:
                return tuple(map(int, m.groups()))
    return None

def get_latest_git_tag():
    try:
        tags = subprocess.check_output([
            "git", "tag", "--list", "v*", "--sort=-v:refname"
        ], encoding="utf-8").split()
        if tags:
            m = re.match(r"v(\d+)\.(\d+)\.(\d+)", tags[0])
            if m:
                return tuple(map(int, m.groups()))
        return None
    except Exception as e:
        print(f"Error getting git tags: {e}")
        return None

def version_tuple_to_str(version):
    return f"v{version[0]}.{version[1]}.{version[2]}"

def check_duplicate_refs(tag):
    refs = subprocess.check_output(["git", "show-ref", tag], encoding="utf-8").splitlines()
    branch = tag in subprocess.check_output(["git", "branch"], encoding="utf-8").split()
    tag_exists = tag in subprocess.check_output(["git", "tag"], encoding="utf-8").split()
    return branch, tag_exists, refs

def resolve_duplicate_refs(tag):
    branch, tag_exists, refs = check_duplicate_refs(tag)
    if branch and tag_exists:
        print(f"Both a branch and a tag named {tag} exist (locally or remotely). This will cause push errors.")
        answer = input(f"Delete branch {tag} (recommended for releases)? [y/N]: ").strip().lower()
        if answer == "y":
            try:
                subprocess.run(["git", "branch", "-d", tag], check=True)
            except subprocess.CalledProcessError:
                # If not local, try remote only
                pass
            subprocess.run(["git", "push", "origin", "--delete", tag], check=False)
            print(f"Branch {tag} deleted (local and/or remote).")
        else:
            answer = input(f"Delete tag {tag} instead? [y/N]: ").strip().lower()
            if answer == "y":
                try:
                    subprocess.run(["git", "tag", "-d", tag], check=True)
                except subprocess.CalledProcessError:
                    pass
                subprocess.run(["git", "push", "origin", f":refs/tags/{tag}"], check=False)
                print(f"Tag {tag} deleted (local and/or remote).")
            else:
                print("No action taken. Resolve manually.")
                sys.exit(2)

def create_and_push_tag(tag):
    # Check for duplicate refs and resolve if needed
    resolve_duplicate_refs(tag)
    try:
        subprocess.run(["git", "tag", tag], check=True)
        subprocess.run(["git", "push", "origin", tag], check=True)
        print(f"Tag {tag} created and pushed.")
    except subprocess.CalledProcessError as e:
        print(f"Push failed, attempting to resolve conflicts and retry...")
        resolve_duplicate_refs(tag)
        subprocess.run(["git", "tag", tag], check=True)
        subprocess.run(["git", "push", "origin", tag], check=True)
        print(f"Tag {tag} created and pushed after resolving conflicts.")

def check():
    changelog_version = get_latest_changelog_version()
    git_tag_version = get_latest_git_tag()
    changelog_str = version_tuple_to_str(changelog_version) if changelog_version else None
    git_tag_str = version_tuple_to_str(git_tag_version) if git_tag_version else None
    print(f"Changelog version: {changelog_str}")
    print(f"Latest git tag:    {git_tag_str}")
    if changelog_version == git_tag_version:
        print("✔ Versions match.")
        sys.exit(0)
    else:
        print("✘ Versions do NOT match!")
        answer = input(f"Create git tag {changelog_str}? [y/N]: ").strip().lower()
        if answer == "y":
            try:
                create_and_push_tag(changelog_str)
                sys.exit(0)
            except subprocess.CalledProcessError as e:
                print(f"Error creating or pushing tag: {e}")
                sys.exit(2)
        else:
            print("No tag created.")
            sys.exit(1)

def increment_minor(version):
    major, minor, patch = version
    return (major, minor + 1, 0)

def increment_major(version):
    major, minor, patch = version
    return (major + 1, 0, 0)

def increment_patch(version):
    major, minor, patch = version
    return (major, minor, patch + 1)

def prepend_changelog(new_version):
    today = date.today().isoformat()
    new_header = f"## v{new_version[0]}.{new_version[1]}.{new_version[2]} ({today})\n\n- _Describe changes for this release here._\n\n"
    with open(CHANGELOG) as f:
        content = f.read()
    with open(CHANGELOG, "w") as f:
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

def bump_minor():
    version = get_latest_changelog_version()
    if not version:
        print("Could not find a version in the changelog.")
        sys.exit(1)
    new_version = increment_minor(version)
    prepend_changelog(new_version)
    answer = input(f"Create and push git tag v{new_version[0]}.{new_version[1]}.{new_version[2]}? [y/N]: ").strip().lower()
    if answer == "y":
        try:
            create_and_push_tag(version_tuple_to_str(new_version))
        except subprocess.CalledProcessError as e:
            print(f"Error creating or pushing tag: {e}")
            sys.exit(2)
    else:
        print("No tag created.")

def bump_major():
    version = get_latest_changelog_version()
    if not version:
        print("Could not find a version in the changelog.")
        sys.exit(1)
    new_version = increment_major(version)
    prepend_changelog(new_version)
    answer = input(f"Create and push git tag v{new_version[0]}.{new_version[1]}.{new_version[2]}? [y/N]: ").strip().lower()
    if answer == "y":
        try:
            create_and_push_tag(version_tuple_to_str(new_version))
        except subprocess.CalledProcessError as e:
            print(f"Error creating or pushing tag: {e}")
            sys.exit(2)
    else:
        print("No tag created.")

def bump_patch():
    version = get_latest_changelog_version()
    if not version:
        print("Could not find a version in the changelog.")
        sys.exit(1)
    new_version = increment_patch(version)
    prepend_changelog(new_version)
    answer = input(f"Create and push git tag v{new_version[0]}.{new_version[1]}.{new_version[2]}? [y/N]: ").strip().lower()
    if answer == "y":
        try:
            create_and_push_tag(version_tuple_to_str(new_version))
        except subprocess.CalledProcessError as e:
            print(f"Error creating or pushing tag: {e}")
            sys.exit(2)
    else:
        print("No tag created.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 version_manager.py [check|bump-minor]")
        sys.exit(1)
    if sys.argv[1] == "check":
        check()
    elif sys.argv[1] == "bump-minor":
        bump_minor()
    elif sys.argv[1] == "bump-major":
        bump_major()
    elif sys.argv[1] == "bump-patch":
        bump_patch()
    else:
        print("Unknown command.")
        sys.exit(1)

if __name__ == "__main__":
    main()
