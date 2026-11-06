#!/usr/bin/env sh
# Install life-pattern-reading into a DSH skills directory.
#
# Usage:
#   sh scripts/install.sh                 # user scope: ${DSH_HOME:-$HOME/.dsh}/skills
#   sh scripts/install.sh --project       # <current dir>/.dsh/skills
#   sh scripts/install.sh --force         # replace an existing copy
#   sh scripts/install.sh --target DIR    # custom skills root
#
# This script only copies files. It does not run them or modify the registry.

set -eu

scope="user"
project_dir="$(pwd)"
target_root=""
force="0"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --project)
            scope="project"
            shift
            ;;
        --user)
            scope="user"
            shift
            ;;
        --target)
            if [ "$#" -lt 2 ]; then
                echo "ERROR: --target requires a directory" >&2
                exit 2
            fi
            target_root="$2"
            shift 2
            ;;
        --force)
            force="1"
            shift
            ;;
        -h|--help)
            sed -n '2,18p' "$0"
            exit 0
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)

if [ ! -f "$source_dir/SKILL.md" ]; then
    echo "ERROR: SKILL.md not found under $source_dir" >&2
    exit 1
fi

if [ -n "$target_root" ]; then
    dest_root="$target_root"
elif [ "$scope" = "project" ]; then
    dest_root="$project_dir/.dsh/skills"
else
    dest_root="${DSH_HOME:-$HOME/.dsh}/skills"
fi

dest="$dest_root/life-pattern-reading"

if [ -e "$dest" ]; then
    if [ "$force" != "1" ]; then
        echo "ERROR: destination already exists: $dest" >&2
        echo "Re-run with --force to replace it." >&2
        exit 1
    fi
    rm -rf "$dest"
fi

mkdir -p "$dest"

for item in SKILL.md README.md README.en.md LICENSE CHANGELOG.md references assets scripts examples; do
    if [ -e "$source_dir/$item" ]; then
        cp -R "$source_dir/$item" "$dest/"
    fi
done

echo "Installed: $dest"
echo "Next: start a new DSH session (or wait for the skill watcher to refresh) and invoke /life-pattern-reading."
