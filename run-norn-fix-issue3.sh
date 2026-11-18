rm -rf tmp
echo "reset hard origin/main"
git reset --hard origin/main
echo "starting fix issue #3"
uv run --project ~/projects/erik.romson/norn/main python -m norn run fix_issue_v1  auto erik-romson/lunsjmeny#3 --arg auto=on
