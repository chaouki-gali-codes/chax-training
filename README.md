# Chax Training

A mobile-first, offline-capable workout log for the included seven-day schedule. It is plain HTML, CSS, and vanilla JavaScript with no build step.

## Run locally

From this directory, run:

```sh
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000). A local HTTP server is required for the service worker; opening `index.html` directly from disk will not enable offline caching or installability.

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
    'Hack squat': 'Leg Press',
}
```

The downloaded JSON index and images are served from the repository's raw GitHub URLs by the script. The entire app and images are cached on first load by `sw.js`.

## App features

- Guided exercise screens with two bundled start/end images, instructions, cues, set logging, last-session values, rest timer, and form search.
- Workout overview, exercise swaps, swipe navigation, Wake Lock where supported, and timestamp-based countdowns.
- Local session history, per-exercise top-set chart, bodyweight log, JSON export/import, and reset.
- English/French preference, dark/light/system theme, sound/vibration/auto-start controls, warm-up checklist, recovery day checklist, and progression reminder.
- All personal data is stored in localStorage with guarded reads and writes. Export a backup before clearing browser data.

## Deploy for free with GitHub Pages

1. Push this folder to a GitHub repository.
2. In the repository, open **Settings → Pages**.
3. Choose **Deploy from a branch**, select the default branch and `/ (root)`, then save.
4. Open the Pages URL on your phone, allow the first load to finish while online, then use **Add to Home Screen** from the browser menu.

Service workers require HTTPS in deployment; GitHub Pages provides it. Any updated app release should use a new cache version in `sw.js`.
