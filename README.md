# Chax Training

A mobile-first, offline-capable muscle-building plan and workout log by Chaouki Gali. It is plain HTML, CSS, and vanilla JavaScript with no build step.

## Run locally

From this directory, run:

```sh
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000). A local HTTP server is required for the service worker; opening `index.html` directly from disk will not enable offline caching or installability.

## Training plan

The five training days fit the gym's opening schedule: Push Monday, Pull Tuesday, Lower A Wednesday, Upper Thursday, rest Friday, Lower B + Core Saturday, and rest Sunday. Push and Upper spread chest and shoulder work through the week; Pull uses a chest-supported row; the two lower sessions split quad and posterior-chain work. The exact exercises, sets, rep ranges, rest times, and cues live in `data.js`.

The RDL stays light and controlled. The app shows your back-discomfort reminder on every pulling and lower-body exercise. Stop if discomfort becomes sharp, and use a comfortable range of motion.

This is a general muscle-building template, not a personalized clinical plan. ACSM’s 2026 position-stand overview describes roughly 10 weekly sets per muscle group as a useful hypertrophy target for healthy adults; the program spreads work across sessions for manageable workouts. [ACSM overview](https://acsm.org/wp-content/uploads/2026/03/Resistance-Training-Position-Stand-infographic.pdf)

## Exercise images and attribution

The bundled exercise photos and instruction steps come from [yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db), an open public-domain exercise dataset. Images are stored locally in `images/<exercise-slug>/0.jpg` and `1.jpg`, so workouts do not hotlink images and can be used offline. Exercise names, muscle groups, and instruction steps are in `data.js`.

The fetch script writes a `MATCHED`, `EQUIVALENT`, or `NOT FOUND` report. Equivalent entries are the closest visual/form guide available in the dataset and are flagged in the app. They do not change your prescribed exercise name, sets, rep target, rest time, or key cue.

To refresh the matches and images:

```sh
python3 scripts/fetch_images.py
```

Edit `OVERRIDES` near the top of `scripts/fetch_images.py` to map a requested exercise to an exact dataset exercise name, then re-run the script. For example:

```python
OVERRIDES = {
    'Leg press (quad stance)': 'Leg Press',
}
```

The downloaded JSON index and images are served from the repository's raw GitHub URLs by the script. The entire app and images are cached on first load by `sw.js`.

## App features

- Guided exercise screens with two bundled start/end images, instructions, cues, set logging, last-session values, rest timer, and form search.
- Workout overview, exercise swaps, swipe navigation, Wake Lock where supported, and timestamp-based countdowns.
- Local session history, per-exercise top-set chart, bodyweight log, JSON export/import, and reset.
- English/Arabic language preference with right-to-left Arabic layout, dark/light/system theme, sound/vibration/auto-start controls, warm-up checklist, recovery day checklist, and progression reminder.
- All personal data is stored in localStorage with guarded reads and writes. Export a backup before clearing browser data.

## Deploy for free with GitHub Pages

1. Push this folder to a GitHub repository.
2. In the repository, open **Settings → Pages**.
3. Choose **Deploy from a branch**, select the default branch and `/ (root)`, then save.
4. Open the Pages URL on your phone, allow the first load to finish while online, then use **Add to Home Screen** from the browser menu.

Service workers require HTTPS in deployment; GitHub Pages provides it. Any updated app release should use a new cache version in `sw.js`.
