# Chax Training

A mobile-first, offline-capable muscle-building plan and workout log by Chaouki Gali. It is plain HTML, CSS, and vanilla JavaScript with no build step.

## Run locally

From this directory, run:

```sh
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000). A local HTTP server is required for the service worker; opening `index.html` directly from disk will not enable offline caching or installability.

## Training plan

The plan follows your Push, Pull, Legs, Upper routine, with one focused leg day and a fifth Arms + Delts session. The default week starts Saturday: Push Saturday, Pull Sunday, Legs Monday, Arms + Delts Tuesday, recovery Wednesday, Upper Thursday, and recovery Friday while the gym is closed. You can move workouts to any open day in Settings. Your upper-day exercise list stays as you sent it. The Romanian deadlift stays light and controlled; the app repeats your sharp-pain reminder on pulling and lower-body exercises.

Your plan keeps direct arm work on Push and Pull and adds another short Arms + Delts workout. Adjust training volume if your recovery or back discomfort worsens; the app is a tracking tool, not medical advice.

Exercise names, sets, rep ranges, rest times, cues, and photo matches live in `data.js` and `scripts/fetch_images.py`. You can edit or replace movements from Settings → Edit workouts; those changes stay in local storage and are included in exported backups.

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
    'Hack squat or barbell squat': 'Hack Squat',
}
```

The script also downloads the 36 exact-variant entries used by the movement picker, so replacement photos are bundled locally too.

The downloaded JSON index and images are served from the repository's raw GitHub URLs by the script. The entire app and images are cached on first load by `sw.js`.

## App features

- Guided exercise screens with two bundled start/end images, instructions, cues, set logging, last-session values, rest timer, and form search.
- Workout overview, exercise swaps, swipe navigation, Wake Lock where supported, and timestamp-based countdowns.
- Training insights: weekly session count, completed-set total, recent session duration, personal records, top-set charts, muscle-volume estimate, and bodyweight trend.
- Edit, add, remove, and replace workout movements in Settings; edit sets, reps, rest, and cues.
- Local session history, session review, JSON backup/restore, reminder, and reset.
- English/Arabic language preference with familiar Arabic gym exercise names, the canonical English exercise name alongside each one, Arabic coaching cues, and muscle terminology in a right-to-left layout. It also includes dark/light/system theme, sound/vibration/auto-start controls, warm-up and recovery checklists, and progression reminders.
- All personal data is stored in localStorage with guarded reads and writes. Export a backup before clearing browser data.

## Deploy for free with GitHub Pages

1. Push this folder to a GitHub repository.
2. In the repository, open **Settings → Pages**.
3. Choose **Deploy from a branch**, select the default branch and `/ (root)`, then save.
4. Open the Pages URL on your phone, allow the first load to finish while online, then use **Add to Home Screen** from the browser menu.

Service workers require HTTPS in deployment; GitHub Pages provides it. Any updated app release should use a new cache version in `sw.js`. Exercise alternatives and photo guides are bundled locally; where the public-domain dataset does not contain the exact machine or grip variant, the walkthrough names the closest photo match so it is clear what the images depict.
