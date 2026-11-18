rm -rf tmp/
echo "reset hard origin/main"
git reset --hard origin/main
echo "starting fix issue #2"
uv run --project ~/projects/erik.romson/norn/main python -m norn run fix_issue_v1  auto erik-romson/lunsjmeny#2 --arg auto=on
