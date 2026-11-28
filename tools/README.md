# Chess Gym: how this repo is built

The repo root **is** the app served at https://elliottpurdue.github.io/chess-gym/ (home-screen app, offline cache, gist sync).
The same app also runs as a claude.ai artifact (slug 63dc72c9-d42c-4987-a7d3-e348e87514fd), which syncs through the artifact database instead of the gist.

## Updating the app
1. Edit `tools/claude-artifact-index.html`: this is the single source of the page. Its first line is the wrapper claude.ai adds; keep it.
2. Publish that file as `index.html` to the claude.ai artifact (patch mode, base_version from get_artifact).
3. Rebuild the root for GitHub Pages: `build_pwa.py` strips the wrapper line, adds the manifest, iPhone meta tags and the service-worker registration, copies the data files and icons, and writes `sw.js` with a cache version hashed from the files. Paths in it point at the original working folders; set `W` to a folder holding the artifact files (index.html + json + chess.js + pieces.css + favicon.png) and `OUT` to the repo root.
4. Commit and push. Phones pick the update up the next time the app opens with internet.
5. The offline PC copy lives at `C:\Users\Elliott\tools\ChessGym\app` (served at localhost:8642): the same page without the wrapper line, plus the data files.

## Never break
- localStorage key `gym-v1` and its format (cards, days, xp, prate, lseen, coordsBest, lines, endgames, gamelog, wood, session, routine).
- The sync code: claude.ai db doc `data/users/<id>/gym` and, outside claude.ai, the private gist "Chess Gym progress (private)" with file `chess-gym.json`. Both store `{json, t}` and merge with `mergeStates`.

## Data generators (Python, python-chess + Stockfish)
- `drills_generate.py`, `drills_curate.py` → `drills.json` (Their threat / Is it safe, from his own games).
- `study_mates_kpk.py`, `study_rook_lines.py` → `study.json` (mate patterns, king-and-pawn positions, Lucena/Philidor).
- `themes2_pick.py` → `themes2.json` (22 extra themes from the Lichess open puzzle database, CC0).
- Openings (`openings.json`) and punish positions (`deviations.json`) were engine-checked by earlier scripts; add new lines by hand and verify every move with python-chess and Stockfish.
