#!/usr/bin/env python3
"""Fetch free-exercise-db data and locally bundle the closest exercise photos."""
import json, re, urllib.request, difflib, unicodedata, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_URL = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json'
IMAGE_ROOT = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/'

# Requested program, in order. Edit these names to change the routine.
PROGRAM = [
    # Day 1: Push. Dumbbell variations keep the visual guide and make setup accessible.
    ('Day 1 · Push', 'Incline dumbbell press', 3, '6-8', 150, 'Use a 30-degree incline; keep elbows about 45 degrees from the torso and lower toward the upper chest.'),
    ('Day 1 · Push', 'Dumbbell bench press', 3, '8-10', 120, 'Set shoulder blades back and down; lower the dumbbells under control.'),
    ('Day 1 · Push', 'Cable fly', 2, '12-15', 90, 'Keep a slight elbow bend and squeeze the chest without shrugging.'),
    ('Day 1 · Push', 'Seated dumbbell shoulder press', 3, '6-10', 120, 'Keep your back supported and ribs down; stop before your lower back arches.'),
    ('Day 1 · Push', 'Dumbbell lateral raise', 3, '12-15', 60, 'Keep a slight elbow bend and raise to shoulder height without swinging.'),
    ('Day 1 · Push', 'Rope triceps pushdown', 3, '8-12', 60, 'Keep elbows still by your sides; separate the rope at the bottom.'),
    ('Day 1 · Push', 'Overhead cable triceps extension', 2, '10-12', 60, 'Point elbows forward and allow a comfortable stretch; extend without flaring.'),

    # Day 2: Pull. Supported rows reduce unnecessary lower-back loading.
    ('Day 2 · Pull', 'Lat pulldown', 3, '6-10', 120, 'Use a shoulder-width overhand grip; bring the bar to your upper chest with a steady torso.'),
    ('Day 2 · Pull', 'Chest-supported dumbbell row', 3, '8-10', 120, 'Keep your chest on the pad, lead with your elbows, and squeeze your shoulder blades.'),
    ('Day 2 · Pull', 'Seated cable row', 2, '10-12', 120, 'Keep a neutral, comfortable spine and pull toward your lower ribs.'),
    ('Day 2 · Pull', 'Reverse pec deck', 3, '12-15', 60, 'Use a light load and lead the reverse fly with your elbows.'),
    ('Day 2 · Pull', 'Cable curl', 3, '8-10', 60, 'Keep your elbows pinned and torso still; lower the handle slowly.'),
    ('Day 2 · Pull', 'Hammer curl', 2, '12-15', 60, 'Keep a neutral grip and elbows still; avoid swinging.'),

    # Day 3: One balanced leg day, as requested. Keep the hinge light and controlled.
    ('Day 3 · Legs', 'Leg press (quad stance)', 4, '8-10', 150, 'Use a controlled, comfortable depth and drive through the mid-foot; keep your back on the pad.'),
    ('Day 3 · Legs', 'Romanian deadlift (light, controlled)', 2, '8-10', 120, 'Keep this light; hinge with a neutral spine and stop around mid-shin or sooner if your back position changes.'),
    ('Day 3 · Legs', 'Walking lunge (dumbbells)', 3, '10 per leg', 90, 'Take a controlled stride, keep your torso upright, and use support if balance is uncertain.'),
    ('Day 3 · Legs', 'Seated leg curl', 4, '10-15', 90, 'Set the pad just above your heels and control the return.'),
    ('Day 3 · Legs', 'Leg extension', 2, '12-15', 90, 'Pause for one second at the top and lower under control.'),
    ('Day 3 · Legs', 'Standing calf raise', 4, '10-15', 60, 'Use a comfortable full stretch and pause briefly at the top.'),
    ('Day 3 · Legs', 'Cable crunch', 3, '12-15', 60, 'Round your spine toward your pelvis; keep your hips still.'),

    # Day 4: Upper pump and second chest/back exposure.
    ('Day 4 · Upper + Arms', 'Incline fly machine', 3, '12-15', 90, 'Keep a slight bend in your elbows and squeeze without shrugging.'),
    ('Day 4 · Upper + Arms', 'Seated cable row', 3, '12', 120, 'Keep your spine neutral and pull toward your lower ribs.'),
    ('Day 4 · Upper + Arms', 'Lat pulldown', 2, '10-12', 90, 'Use a comfortable grip and bring the bar to your upper chest without leaning back.'),
    ('Day 4 · Upper + Arms', 'Dumbbell lateral raise', 3, '15-20', 60, 'Raise with control; use small partials only on the final set if form stays strict.'),
    ('Day 4 · Upper + Arms', 'Overhead cable triceps extension', 3, '12-15', 60, 'Keep elbows forward and allow a comfortable stretch.'),
    ('Day 4 · Upper + Arms', 'Cable curl', 3, '10-12', 60, 'Keep elbows pinned and avoid swinging.'),

    # Day 5: Short arm/delt specialization session; Friday remains the closed day.
    ('Day 5 · Arms + Delts', 'Cable lateral raise', 2, '15-20', 60, 'Lead with the elbow; use a controlled range and avoid leaning.'),
    ('Day 5 · Arms + Delts', 'Rope triceps pushdown', 2, '12-15', 60, 'Keep elbows fixed and split the rope at the bottom.'),
    ('Day 5 · Arms + Delts', 'Cable curl', 2, '12-15', 60, 'Keep elbows pinned and lower the handle slowly.'),
    ('Day 5 · Arms + Delts', 'Hammer curl', 2, '10-12', 60, 'Use a neutral grip and keep your elbows still.'),
]

# Manual map: requested exercise name -> exact dataset entry name. Keep editable.
OVERRIDES = {
    'Dumbbell bench press':'Dumbbell Bench Press',
    'Incline dumbbell press':'Incline Dumbbell Press',
    'Seated dumbbell shoulder press':'Seated Dumbbell Press',
    'Cable lateral raise':'Side Lateral Raise',
    'Rope triceps pushdown':'Triceps Pushdown - Rope Attachment',
    'Lat pulldown':'Wide-Grip Lat Pulldown',
    'Chest-supported dumbbell row':'Incline Bench Pull',
    'Straight-arm cable pulldown':'Straight-Arm Pulldown',
    'Reverse pec deck':'Reverse Machine Flyes',
    'Hammer curl':'Hammer Curls',
    'Leg press (quad stance)':'Leg Press',
    'Walking lunge (dumbbells)':'Barbell Walking Lunge',
    'Leg extension':'Leg Extensions',
    'Lying leg curl':'Lying Leg Curls',
    'Standing calf raise':'Standing Calf Raises',
    'Cable fly':'Cable Crossover',
    'Incline fly machine':'Incline Dumbbell Flyes',
    'Seated cable row':'Seated Cable Rows',
    'Assisted neutral-grip pull-up':'V-Bar Pullup',
    'Dumbbell lateral raise':'Side Lateral Raise',
    'Cable curl':'High Cable Curls',
    'Overhead cable triceps extension':'Cable One Arm Tricep Extension',
    'Romanian deadlift (light, controlled)':'Romanian Deadlift',
    'Leg press (feet high and wide)':'Leg Press',
    'Hip thrust':'Barbell Hip Thrust',
    'Seated leg curl':'Seated Leg Curl',
    'Seated calf raise':'Seated Calf Raise',
    'Cable crunch':'Cable Crunch',
    'Plank':'Plank',
}

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
    out=[]; reports=[]
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
            match_type='MATCHED' if norm(found['name'])==norm(name) else 'EQUIVALENT'
            reports.append((match_type,name,found['name']))
            exercise=dict(id=slug,name=name,day=day,sets=sets,reps=reps,rest=rest,cue=cue,target=found.get('primaryMuscles',[]),secondary=found.get('secondaryMuscles',[]),instructions=found.get('instructions',[]),images=images,matchedName=found['name'],matchType=match_type)
            if name == 'Plank': exercise['weightless']=True
            if name.startswith('Romanian deadlift'): exercise['limitedLoad']=True
            if day in {'Day 2 · Pull','Day 3 · Legs'} or set(exercise['target']) & {'lats','middle back','lower back','quadriceps','hamstrings','glutes'}:
                exercise['backCaution']=True
            out.append(exercise)
        else:
            reports.append(('NOT FOUND',name,found['name'] if found else '—'))
            out.append(dict(id=slug,name=name,day=day,sets=sets,reps=reps,rest=rest,cue=cue,target=[],secondary=[],instructions=[],images=[],matchedName=found['name'] if found else '',matchType='NOT FOUND'))
    (ROOT/'data.js').write_text('window.WORKOUT_DATA = '+json.dumps(out,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    print('\nIMAGE MATCH REPORT')
    for status,name,matched in reports: print(f'{status:10} | {name}'+(f' → {matched}' if status!='MATCHED' else ''))
    print(f'\n{sum(s=="MATCHED" for s,_,_ in reports)} matched, {sum(s=="EQUIVALENT" for s,_,_ in reports)} equivalents, {sum(s=="NOT FOUND" for s,_,_ in reports)} not found.')

if __name__=='__main__': main()
