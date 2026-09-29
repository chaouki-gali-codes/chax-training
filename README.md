# Chax Training

A mobile-first, offline-capable muscle-building plan and workout log by Chaouki Gali. It is plain HTML, CSS, and vanilla JavaScript with no build step.

## Run locally

From this directory, run:

```sh
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000). A local HTTP server is required for the service worker; opening `index.html` directly from disk will not enable offline caching or installability.

## Training plan

The training week starts Saturday and follows the gym schedule: Push Saturday, Pull Sunday, Legs Monday, recovery Tuesday, Upper + Arms Wednesday, Arms + Delts Thursday, and recovery Friday while the gym is closed. Legs stay on one focused weekly day as requested. The extra fifth session adds direct arm and delt work, while the Upper day gives chest and back a second weekly exposure. Supported rows and machine work limit avoidable lower-back loading; the Romanian deadlift stays light and controlled. The app repeats the sharp-pain reminder on pulling and lower-body exercises.

Your four-day draft had a solid Push, Pull, Legs, Upper foundation, but its Upper day was incomplete and legs only appeared once. The earlier app plan added a second leg day, which you asked to remove. This version keeps your preferred once-weekly leg schedule and adds a fifth specialization day. Weekly direct work is 10 sets for triceps and 12 for biceps, with additional work from presses and pulls. This is a general template; adjust volume if recovery or discomfort becomes an issue. ACSM’s 2026 position-stand overview suggests roughly 10 weekly sets per muscle group as a useful hypertrophy target for healthy adults. [ACSM overview](https://acsm.org/effective-resistance-training-program-infographic/)

Exercise selection, sets, rep ranges, rest times, and cues live in `data.js`; the matching list is in `scripts/fetch_images.py`.

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
- English/Arabic language preference with familiar Arabic gym exercise names, the canonical English exercise name alongside each one, Arabic coaching cues, and muscle terminology in a right-to-left layout. It also includes dark/light/system theme, sound/vibration/auto-start controls, warm-up and recovery checklists, and progression reminders.
- All personal data is stored in localStorage with guarded reads and writes. Export a backup before clearing browser data.

## Deploy for free with GitHub Pages

1. Push this folder to a GitHub repository.
2. In the repository, open **Settings → Pages**.
3. Choose **Deploy from a branch**, select the default branch and `/ (root)`, then save.
4. Open the Pages URL on your phone, allow the first load to finish while online, then use **Add to Home Screen** from the browser menu.

Service workers require HTTPS in deployment; GitHub Pages provides it. Any updated app release should use a new cache version in `sw.js`.
