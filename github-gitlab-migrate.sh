#!/usr/bin/env bash

echo "Cloning all archived repositories from Github to Gitlab..."

TMP_GITHUB_DIR=/tmp/github-repos

mkdir $TMP_GITHUB_DIR

GITHUB_ARCHIVED_REPOS=$(gh repo list --json nameWithOwner --json isArchived --json isFork --jq ".[] | select(.isFork == false) | select(.isArchived == true) | .nameWithOwner" --limit 100)
#GITHUB_REPOS=$(gh repo list --json nameWithOwner --jq "map(.nameWithOwner) | join(\"\n\")" --limit 100 --no-archived)
GITHUB_REPOS=$GITHUB_ARCHIVED_REPOS

echo "$GITHUB_REPOS"

IFS=$'\n' read -r -d '' -a MY_REPOS <<< "$GITHUB_REPOS"

for repo in "${MY_REPOS[@]}"; do
  gh repo clone $repo $TMP_GITHUB_DIR/${repo##*/}
done

for repo in "${MY_REPOS[@]}"; do
  glab repo delete $repo
  read -p "Press Enter to continue" </dev/tty
  DIR_NAME=${repo##*/}
  cd $TMP_GITHUB_DIR/$DIR_NAME
  git remote remove origin 
  glab repo create --group jack-champagne-gh-archived
  git branch -M main
  git push -u origin main
done

rm -rf $TMP_GITHUB_DIR
