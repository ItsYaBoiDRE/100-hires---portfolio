# Laptop setup (5 minutes)

## Prerequisites
- Git installed (git-scm.com)
- Python 3.10+ installed

## Steps
1. Extract this zip anywhere (e.g. Documents/projects/).
2. Open a terminal inside the extracted `cold-outreach-research` folder.
3. Run the setup script:
   - **Windows:** double-click `setup.bat` (or run it in cmd)
   - **Mac/Linux:** `bash setup.sh`
   This creates the git repo with 4 clean starter commits and installs the
   Python dependencies.
4. Create an empty repo on github.com (no README, no .gitignore), then:
   ```
   git remote add origin https://github.com/YOUR_USERNAME/cold-outreach-research.git
   git branch -M main
   git push -u origin main
   ```

## First collection test
```
python scripts/fetch_youtube_transcripts.py "https://www.youtube.com/watch?v=VIDEO_ID" --author jason-bay
git add research/youtube-transcripts/jason-bay/
git commit -m "data: add first Jason Bay transcript"
git push
```

## Daily workflow
Follow `docs/collection-workflow.md` — 2 authors per day, commit per session.
