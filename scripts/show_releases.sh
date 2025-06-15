#!/bin/bash

git log -p --pretty=format:'%H|%an|%ad|%s' --date=short -- pyproject.toml | \
awk -F'|' '
  /^[0-9a-f]{40}/ {
    commit = $1;
    author = $2;
    date = $3;
    msg = $4;
    next
  }
  /^\+version[[:space:]]*=/ {
    gsub(/^\+/, "", $0);
    authordate = author " (" date ")"
    printf "%-30s\t%s\t%-40s\t%s\n", authordate, commit, msg, $0
  }
'
