#!/usr/bin/env python3
"""Fetch free-exercise-db data and locally bundle the closest exercise photos."""
import json, re, urllib.request, difflib, unicodedata, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_URL = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json'
IMAGE_ROOT = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/'

# Requested program, in order. Edit these names to change the routine.
PROGRAM = [
    # Day 1: the user's Push day. Images map to the barbell / machine / dumbbell choices noted.
    ('Day 1 · Push', 'Incline Smith or barbell press', 3, '6-8', 150, 'Use a controlled range; set the bench incline, keep elbows about 45° from your torso, and lower toward the upper chest.'),
    ('Day 1 · Push', 'Flat machine or dumbbell press', 3, '8-10', 120, 'Set the handles at mid-chest; keep shoulder blades back and down.'),
    ('Day 1 · Push', 'Cable fly (mid or low)', 2, '12-15', 90, 'Keep a slight elbow bend and squeeze the chest without shrugging.'),
    ('Day 1 · Push', 'Shoulder press (dumbbell or machine)', 3, '6-10', 120, 'Keep ribs down and press without arching your lower back.'),
    ('Day 1 · Push', 'Lateral raise', 4, '12-15', 60, 'Keep a slight elbow bend and raise to shoulder height without swinging.'),
    ('Day 1 · Push', 'Triceps pushdown', 3, '8-12', 60, 'Keep elbows fixed and lower the handle under control.'),
    ('Day 1 · Push', 'Overhead triceps extension', 2, '10-12', 60, 'Point elbows forward and allow a comfortable stretch; extend without flaring.'),

    # Day 2: Pull.
    ('Day 2 · Pull', 'Pull-up or lat pulldown', 3, '6-10', 120, 'Start from a controlled hang, or use a shoulder-width grip and pull the bar to your upper chest.'),
    ('Day 2 · Pull', 'Chest-supported row', 3, '8-10', 120, 'Keep your chest on the pad, pull your elbows back, and squeeze your shoulder blades.'),
    ('Day 2 · Pull', 'Seated cable row', 2, '10-12', 120, 'Pull toward your lower ribs with a neutral, steady spine.'),
    ('Day 2 · Pull', 'Rear-delt fly or reverse pec deck', 3, '12-15', 60, 'Use a light load and lead the fly with your elbows.'),
    ('Day 2 · Pull', 'Preacher curl', 3, '8-10', 60, 'Keep upper arms supported on the pad and lower without bouncing.'),
    ('Day 2 · Pull', 'Bayesian or incline curl', 2, '12-15', 60, 'Keep your upper arm slightly behind your torso and avoid swinging.'),
    ('Day 2 · Pull', 'Forearms (optional)', 2, '15-20', 60, 'Use a controlled wrist curl through a comfortable range.'),

    # Day 3: once-weekly legs. RDL is intentionally light due to the user's back discomfort.
    ('Day 3 · Legs', 'Hack squat or barbell squat', 4, '6-10', 150, 'Use a controlled, comfortable depth and drive through mid-foot.'),
    ('Day 3 · Legs', 'Romanian deadlift (light, controlled)', 3, '6-10', 120, 'Keep the load light; hinge with a neutral spine and stop around mid-shin or sooner if your back position changes.'),
    ('Day 3 · Legs', 'Leg press or Bulgarian split squat', 3, '10-12', 120, 'Control the descent; on leg press, keep your lower back against the pad.'),
    ('Day 3 · Legs', 'Leg curl', 3, '10-15', 90, 'Keep your hips against the pad and control the lowering phase.'),
    ('Day 3 · Legs', 'Leg extension', 2, '12-15', 90, 'Pause for one second at the top and lower under control.'),
    ('Day 3 · Legs', 'Standing calf raise', 4, '10-15', 60, 'Use a full comfortable stretch and pause at the top.'),
    ('Day 3 · Legs', 'Hanging leg raise', 3, '12-15', 60, 'Keep the swing small and curl your pelvis up with control.'),

    # Day 4: the user's Upper pump / weak-points day.
    ('Day 4 · Upper', 'Incline fly machine', 3, '12-15', 90, 'Keep a slight elbow bend and squeeze without shrugging.'),
    ('Day 4 · Upper', 'Cable row (upper back)', 3, '12', 120, 'Pull toward your upper-to-mid torso and keep a steady, neutral spine.'),
    ('Day 4 · Upper', 'Lateral raise (partials on last set)', 4, '15-20', 60, 'Use strict full reps; add short partials only at the end of the last set if form stays controlled.'),
    ('Day 4 · Upper', 'Single-arm cable triceps extension', 3, '12-15', 60, 'Keep the upper arm still and extend without twisting your torso.'),
    ('Day 4 · Upper', 'Hammer curl', 3, '10-12', 60, 'Use a neutral grip and keep elbows still.'),

    # Day 5: short arms / delts specialization, added to round out the week.
    ('Day 5 · Arms + Delts', 'Cable curl', 3, '10-12', 60, 'Keep elbows pinned and lower the handle slowly.'),
    ('Day 5 · Arms + Delts', 'Rope triceps pushdown', 3, '10-12', 60, 'Keep elbows fixed and split the rope at the bottom.'),
    ('Day 5 · Arms + Delts', 'Cable lateral raise', 3, '15-20', 60, 'Lead with the elbow; use a controlled range and avoid leaning.'),
]

# Manual map: requested exercise name -> exact dataset entry name. Keep editable.
OVERRIDES = {
    'Incline Smith or barbell press': 'Smith Machine Incline Bench Press',
    'Flat machine or dumbbell press': 'Leverage Chest Press',
    'Cable fly (mid or low)': 'Cable Crossover',
    'Shoulder press (dumbbell or machine)': 'Dumbbell Shoulder Press',
    'Lateral raise': 'Side Lateral Raise',
    'Triceps pushdown': 'Triceps Pushdown',
    'Overhead triceps extension': 'Cable Rope Overhead Triceps Extension',
    'Pull-up or lat pulldown': 'Wide-Grip Lat Pulldown',
    'Chest-supported row': 'Incline Bench Pull',
    'Seated cable row': 'Seated Cable Rows',
    'Rear-delt fly or reverse pec deck': 'Reverse Machine Flyes',
    'Preacher curl': 'Preacher Curl',
    'Bayesian or incline curl': 'Incline Dumbbell Curl',
    'Forearms (optional)': 'Palms-Up Barbell Wrist Curl Over A Bench',
    'Hack squat or barbell squat': 'Hack Squat',
    'Romanian deadlift (light, controlled)': 'Romanian Deadlift',
    'Leg press or Bulgarian split squat': 'Leg Press',
    'Leg curl': 'Lying Leg Curls',
    'Leg extension': 'Leg Extensions',
    'Standing calf raise': 'Standing Calf Raises',
    'Hanging leg raise': 'Hanging Leg Raise',
    'Incline fly machine': 'Incline Cable Flye',
    'Cable row (upper back)': 'Seated Cable Rows',
    'Lateral raise (partials on last set)': 'Side Lateral Raise',
    'Single-arm cable triceps extension': 'Cable One Arm Tricep Extension',
    'Hammer curl': 'Hammer Curls',
    'Cable lateral raise': 'Cable Seated Lateral Raise',
    'Rope triceps pushdown': 'Triceps Pushdown - Rope Attachment',
    'Cable curl': 'Standing Biceps Cable Curl',
    'Reverse pec deck': 'Reverse Machine Flyes',
}

# Exact variants available in the in-app movement picker. Each includes locally
# bundled start/end images from the same public-domain source.
LIBRARY_NAMES = [
    'Smith Machine Incline Bench Press', 'Barbell Incline Bench Press - Medium Grip',
    'Leverage Chest Press', 'Dumbbell Bench Press', 'Cable Crossover', 'Low Cable Crossover',
    'Dumbbell Shoulder Press', 'Leverage Shoulder Press', 'Side Lateral Raise',
    'Triceps Pushdown', 'Triceps Pushdown - Rope Attachment', 'Cable Rope Overhead Triceps Extension',
    'Wide-Grip Lat Pulldown', 'Band Assisted Pull-Up', 'Incline Bench Pull', 'Seated Cable Rows',
    'Reverse Machine Flyes', 'Preacher Curl', 'Incline Dumbbell Curl',
    'Palms-Up Barbell Wrist Curl Over A Bench', 'Hack Squat', 'Barbell Squat', 'Romanian Deadlift',
    'Leg Press', 'Split Squat with Dumbbells', 'Lying Leg Curls', 'Seated Leg Curl',
    'Leg Extensions', 'Standing Calf Raises', 'Hanging Leg Raise', 'Incline Cable Flye',
    'Butterfly', 'Cable One Arm Tricep Extension', 'Hammer Curls', 'Cable Seated Lateral Raise',
    'Standing Biceps Cable Curl',
]

# Only these mappings change exercise setup enough to call the picture an equivalent.
EQUIVALENT_OVERRIDES = {'Incline fly machine': 'Incline Cable Flye'}

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def download(url):
    req=urllib.request.Request(url,headers={'User-Agent':'gym-workout-pwa/1.0'})
    with urllib.request.urlopen(req,timeout=35) as r: return r.read()

def main():
    entries=json.loads(download(DATA_URL))
    if isinstance(entries,dict): entries=entries.get('exercises',entries.get('data',[]))
    names=[e['name'] for e in entries]
    byname={e['name']:e for e in entries}
    out=[]; reports=[]; image_paths_by_match={}
    for row in PROGRAM:
        day,name,sets,reps,rest,cue,*fallback=row
        wanted=OVERRIDES.get(name)
        found=byname.get(wanted) if wanted else None
        exact=False
        if not found:
            close=difflib.get_close_matches(norm(name),[norm(n) for n in names],n=1,cutoff=.40)
            if close:
                idx=[norm(n) for n in names].index(close[0]); found=entries[idx]
                exact=norm(found['name'])==norm(name)
        if not found and fallback:
            close=difflib.get_close_matches(norm(fallback[0]),[norm(n) for n in names],n=1,cutoff=.3)
            if close: found=entries[[norm(n) for n in names].index(close[0])]
        slug=re.sub(r'[^a-z0-9]+','-',norm(name)).strip('-')
        images=[]
        if found and len(found.get('images',[]))>=2:
            folder=ROOT/'images'/slug; folder.mkdir(parents=True,exist_ok=True)
            try:
                for i,path in enumerate(found['images'][:2]):
                    target=folder/f'{i}.jpg'
                    target.write_bytes(download(IMAGE_ROOT+path))
                    images.append(f'images/{slug}/{i}.jpg')
            except Exception as exc:
                print(f'Image download failed for {name}: {exc}')
                images=[]
        if not images:
            # Search closest visual equivalent using primary muscle and still bundle real photos.
            muscle_hint={'core':'abdominals'}
            if found:
                pool=[e for e in entries if len(e.get('images',[]))>=2 and set(e.get('primaryMuscles',[])) & set(found.get('primaryMuscles',[]))]
            else: pool=[]
            if pool:
                found=pool[0]; folder=ROOT/'images'/slug; folder.mkdir(parents=True,exist_ok=True)
                try:
                    for i,path in enumerate(found['images'][:2]):
                        (folder/f'{i}.jpg').write_bytes(download(IMAGE_ROOT+path)); images.append(f'images/{slug}/{i}.jpg')
                except Exception: images=[]
        if found and len(images)==2:
            match_type='EQUIVALENT' if EQUIVALENT_OVERRIDES.get(name)==found['name'] else 'MATCHED'
            image_paths_by_match.setdefault(found['name'],images)
            reports.append((match_type,name,found['name']))
            exercise=dict(id=slug,name=name,day=day,sets=sets,reps=reps,rest=rest,cue=cue,target=found.get('primaryMuscles',[]),secondary=found.get('secondaryMuscles',[]),instructions=found.get('instructions',[]),images=images,matchedName=found['name'],matchType=match_type)
            if name == 'Plank': exercise['weightless']=True
            if name.startswith('Forearms (optional)'): exercise['optional']=True
            if name.startswith('Romanian deadlift'): exercise['limitedLoad']=True
            if day in {'Day 2 · Pull','Day 3 · Legs'} or set(exercise['target']) & {'lats','middle back','lower back','quadriceps','hamstrings','glutes'}:
                exercise['backCaution']=True
            out.append(exercise)
        else:
            reports.append(('NOT FOUND',name,found['name'] if found else '—'))
            out.append(dict(id=slug,name=name,day=day,sets=sets,reps=reps,rest=rest,cue=cue,target=[],secondary=[],instructions=[],images=[],matchedName=found['name'] if found else '',matchType='NOT FOUND'))
    library=[]; library_reports=[]
    for entry_name in LIBRARY_NAMES:
        found=byname.get(entry_name)
        if not found or len(found.get('images',[]))<2:
            library_reports.append(('NOT FOUND',entry_name)); continue
        slug=re.sub(r'[^a-z0-9]+','-',norm(entry_name)).strip('-')
        folder=ROOT/'images'/slug; folder.mkdir(parents=True,exist_ok=True)
        images=list(image_paths_by_match.get(entry_name,[]))
        if not images:
            try:
                for i,path in enumerate(found['images'][:2]):
                    target=folder/f'{i}.jpg'
                    target.write_bytes(download(IMAGE_ROOT+path))
                    images.append(f'images/{slug}/{i}.jpg')
            except Exception as exc:
                print(f'Library image download failed for {entry_name}: {exc}')
                library_reports.append(('NOT FOUND',entry_name)); continue
        asset=dict(id=slug,name=entry_name,target=found.get('primaryMuscles',[]),secondary=found.get('secondaryMuscles',[]),instructions=found.get('instructions',[]),images=images,matchedName=entry_name,matchType='MATCHED')
        if entry_name == 'Romanian Deadlift': asset['limitedLoad']=True
        if set(asset['target']) & {'lats','middle back','lower back','quadriceps','hamstrings','glutes'}: asset['backCaution']=True
        if 'forearms' in asset['target']: asset['optional']=True
        library.append(asset)
        library_reports.append(('MATCHED',entry_name))
    (ROOT/'data.js').write_text('window.WORKOUT_DATA = '+json.dumps(out,ensure_ascii=False,indent=2)+';\nwindow.EXERCISE_LIBRARY = '+json.dumps(library,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    print('\nIMAGE MATCH REPORT')
    for status,name,matched in reports: print(f'{status:10} | {name}'+(f' → {matched}' if status!='MATCHED' else ''))
    print(f'\n{sum(s=="MATCHED" for s,_,_ in reports)} matched, {sum(s=="EQUIVALENT" for s,_,_ in reports)} equivalents, {sum(s=="NOT FOUND" for s,_,_ in reports)} not found.')
    print('\nALTERNATIVE PHOTO LIBRARY')
    for status,name in library_reports: print(f'{status:10} | {name}')
    print(f'\n{len(library)} of {len(LIBRARY_NAMES)} alternatives bundled.')

if __name__=='__main__': main()
