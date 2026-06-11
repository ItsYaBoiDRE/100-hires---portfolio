@echo off
REM One-time setup for Windows. Run from inside the extracted folder.
git init
git add .gitignore README.md
git commit -m "chore: scaffold repo structure"
git add research/sources.md
git commit -m "docs: add annotated sources list (10 experts)"
git add scripts/
git commit -m "feat: add YouTube transcript fetcher (yt-transcript-api + Supadata fallback)"
git add research/ docs/
git commit -m "docs: add collection workflow, templates, and author folders"
pip install -r scripts/requirements.txt
echo.
echo Done. Now create an empty repo on GitHub, then run:
echo   git remote add origin https://github.com/YOUR_USERNAME/cold-outreach-research.git
echo   git branch -M main
echo   git push -u origin main
pause
