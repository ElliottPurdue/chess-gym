# Chess Gym as a real app (iPhone + PC, synced)

This folder is the whole Chess Gym as a standalone web app. It installs on your iPhone home screen, opens full screen with no browser bars, works offline, and syncs your progress between phone and PC through one private GitHub gist.

It takes about 10 minutes, once. It's free and needs only a GitHub account.

## 1. Put it online (GitHub Pages)
1. Sign in at github.com (or create an account).
2. Create a new repository called `chess-gym`. Public is fine; nothing private is in these files, and your progress is not in them.
3. On the repository page, choose **Add file > Upload files**. Drag in everything inside this folder (not the folder itself): `index.html`, `sw.js`, `manifest.webmanifest`, the `.json` files, `chess.js`, `pieces.css`, `favicon.png`, `.nojekyll` and the `icons` folder. Then commit.
4. Go to **Settings > Pages**. Under "Build and deployment", pick **Deploy from a branch**, branch `main`, folder `/ (root)`, and save.
5. After a minute your app is live at `https://<your-username>.github.io/chess-gym/`.

## 2. Install it on your iPhone
1. Open that address in **Safari**.
2. Tap **Share**, then **Add to Home Screen**, then **Add**.
3. Open it from the new icon. It runs full screen and works without internet. On PC, just bookmark the same address, or keep using your offline copy.

## 3. Turn on sync (phone and PC share one progress)
1. On github.com go to **Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token**.
2. Name it "Chess Gym" and set an expiration (a year is fine). Under **Account permissions**, set **Gists** to **Read and write**. Leave everything else at no access. Generate it, then copy it.
3. In the app, go to **Home > Sync, offline copy and help > Sync this copy**. Paste the token and tap **Connect**.
4. Do the same on your PC with the same token (in the browser at your app's address, and/or in your offline copy). Each copy finds the same private gist and merges into it.

The token is stored only on that device and only sent to GitHub. It can only touch gists. If a device is lost, delete the token on GitHub and make a new one.

## 4. Bring your current progress over
In the claude.ai Chess Gym: **Home > Sync, offline copy and help > Copy my progress**. In the new app: paste it into the box, then tap **Add pasted progress**. Nothing is lost: it merges.

From then on, use the app (phone) and the same address or the offline copy (PC). The claude.ai version keeps its own progress. You can keep it as a backup or stop using it.

## Updating
When Claude adds content, upload the changed files to the same repository again (same names, overwrite). The app picks up the update the next time it opens with internet.
