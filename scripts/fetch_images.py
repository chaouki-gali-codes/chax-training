#!/usr/bin/env python3
"""Fetch free-exercise-db data and locally bundle the closest exercise photos."""
import json, re, urllib.request, difflib, unicodedata, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_URL = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json'
IMAGE_ROOT = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/'

# Requested program, in order. Edit these names to change the routine.
PROGRAM = [
('Day 1 · Upper','Incline dumbbell press',4,'6-8',150,'30 deg bench, elbows ~45 deg from torso, lower to upper chest'),
('Day 1 · Upper','Chest-supported dumbbell row',4,'8-10',120,'Chest on incline bench pad, pull elbows back, squeeze shoulder blades'),
('Day 1 · Upper','Seated dumbbell shoulder press',3,'8-10',120,'Back on pad, ribs down, no arching'),
('Day 1 · Upper','Lat pulldown',3,'8-12',90,'Shoulder-width overhand grip, bar to upper chest'),
('Day 1 · Upper','Dumbbell lateral raise',3,'12-15',60,'Slight elbow bend, raise to shoulder height'),
('Day 1 · Upper','Cable curl',2,'10-12',60,'Elbows pinned, no swinging'),
('Day 1 · Upper','Rope triceps pushdown',2,'10-12',60,'Elbows fixed, split the rope at the bottom'),
('Day 2 · Lower A','Hack squat',4,'8-10',150,'Full controlled depth, drive through mid-foot','Leg Press'),
('Day 2 · Lower A','Leg extension',3,'12-15',90,'Pause 1 s at the top'),
('Day 2 · Lower A','Walking lunges (dumbbells)',3,'10 per leg',90,'Long stride, torso upright'),
('Day 2 · Lower A','Lying leg curl',3,'10-12',90,'Hips pressed into pad, slow negative'),
('Day 2 · Lower A','Standing calf raise',4,'10-15',60,'Full stretch, pause at the top'),
('Day 4 · Push','Machine chest press',4,'8-10',120,'Handles at mid-chest, shoulder blades back and down','Dumbbell Bench Press'),
('Day 4 · Push','Pec deck',3,'12-15',90,'Slight elbow bend, squeeze','Cable Crossover'),
('Day 4 · Push','Machine shoulder press',3,'8-10',120,'Handles start at ear level'),
('Day 4 · Push','Cable lateral raise',4,'15',60,'Lead with the elbow'),
('Day 4 · Push','Overhead cable triceps extension',3,'10-12',60,'Elbows forward, full stretch'),
('Day 4 · Push','Incline dumbbell curl',3,'10-12',60,'Arms behind torso, no swinging'),
('Day 5 · Pull','Neutral-grip pull-up',4,'8-10',120,'Dead hang start, chin over hands','Lat Pulldown'),
('Day 5 · Pull','Chest-supported T-bar row',4,'8-12',120,'Pull to lower ribs, neutral spine','Seated Cable Rows'),
('Day 5 · Pull','Straight-arm cable pulldown',3,'12-15',90,'Arms nearly straight, sweep to thighs'),
('Day 5 · Pull','Reverse pec deck',4,'15',60,'Light weight, lead with elbows'),
('Day 5 · Pull','Face pulls (rope)',3,'15',60,'Rope to forehead height, elbows high'),
('Day 5 · Pull','Hammer curl',3,'10-12',60,'Neutral grip, elbows still'),
('Day 6 · Lower B + Core','Romanian deadlift (light, controlled)',3,'8-10',120,'Hips back, flat back, stop at mid-shin'),
('Day 6 · Lower B + Core','Leg press (feet high and wide)',3,'10-12',120,'Do not let lower back round off the pad'),
('Day 6 · Lower B + Core','Bulgarian split squat (dumbbells)',3,'10 per leg',90,'Rear foot on bench, drop straight down'),
('Day 6 · Lower B + Core','Seated leg curl',3,'10-12',90,'Pad snug above heels'),
('Day 6 · Lower B + Core','Hip thrust',3,'10',90,'Chin tucked, drive through heels, pause at top'),
('Day 6 · Lower B + Core','Seated calf raise',4,'12-15',60,'Deep stretch, pause at top'),
('Day 6 · Lower B + Core','Cable crunch',3,'12-15',60,'Round the spine, hips stay still'),
('Day 6 · Lower B + Core','Plank',3,'45-60 s',60,'Straight line, glutes and abs tight'),
]

# Manual map: requested exercise name -> exact dataset entry name. Keep editable.
OVERRIDES = {
    'Incline dumbbell press':'Incline Dumbbell Press',
    'Lat pulldown':'Wide-Grip Lat Pulldown',
    'Cable curl':'High Cable Curls',
    'Rope triceps pushdown':'Triceps Pushdown - Rope Attachment',
    'Leg extension':'Leg Extensions',
    'Walking lunges (dumbbells)':'Barbell Walking Lunge',
    'Lying leg curl':'Lying Leg Curls',
    'Standing calf raise':'Standing Calf Raises',
    'Neutral-grip pull-up':'V-Bar Pullup',
    'Straight-arm cable pulldown':'Straight-Arm Pulldown',
    'Face pulls (rope)':'Face Pull',
    'Hammer curl':'Hammer Curls',
    'Leg press (feet high and wide)':'Leg Press',
    'Chest-supported dumbbell row':'Incline Bench Pull',
    'Seated dumbbell shoulder press':'Seated Dumbbell Press',
    'Dumbbell lateral raise':'Side Laterals to Front Raise',
    'Hack squat':'Leg Press',
    'Machine chest press':'Dumbbell Bench Press',
    'Pec deck':'Cable Crossover',
    'Machine shoulder press':'Seated Dumbbell Press',
    'Cable lateral raise':'Side Laterals to Front Raise',
    'Overhead cable triceps extension':'Cable One Arm Tricep Extension',
    'Chest-supported T-bar row':'Seated Cable Rows',
    'Reverse pec deck':'Reverse Machine Flyes',
    'Face pulls (rope)':'Face Pulls',
    'Romanian deadlift (light, controlled)':'Romanian Deadlift',
    'Hip thrust':'Barbell Hip Thrust',
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
            out.append(dict(id=slug,name=name,day=day,sets=sets,reps=reps,rest=rest,cue=cue,target=found.get('primaryMuscles',[]),secondary=found.get('secondaryMuscles',[]),instructions=found.get('instructions',[]),images=images,matchedName=found['name'],matchType=match_type))
        else:
            reports.append(('NOT FOUND',name,found['name'] if found else '—'))
            out.append(dict(id=slug,name=name,day=day,sets=sets,reps=reps,rest=rest,cue=cue,target=[],secondary=[],instructions=[],images=[],matchedName=found['name'] if found else '',matchType='NOT FOUND'))
    (ROOT/'data.js').write_text('window.WORKOUT_DATA = '+json.dumps(out,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    print('\nIMAGE MATCH REPORT')
    for status,name,matched in reports: print(f'{status:10} | {name}'+(f' → {matched}' if status!='MATCHED' else ''))
    print(f'\n{sum(s=="MATCHED" for s,_,_ in reports)} matched, {sum(s=="EQUIVALENT" for s,_,_ in reports)} equivalents, {sum(s=="NOT FOUND" for s,_,_ in reports)} not found.')

if __name__=='__main__': main()
