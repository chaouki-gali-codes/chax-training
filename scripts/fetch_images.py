#!/usr/bin/env python3
"""Fetch free-exercise-db data and locally bundle the closest exercise photos."""
import json, re, urllib.request, difflib, unicodedata, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_URL = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json'
IMAGE_ROOT = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/'

# Requested program, in order. Edit these names to change the routine.
PROGRAM = [
('Day 1 · Push','Dumbbell bench press',3,'6-10',120,'Feet planted, shoulder blades back and down, lower under control'),
('Day 1 · Push','Incline dumbbell press',3,'8-12',120,'Low incline, wrists stacked, lower toward the upper chest'),
('Day 1 · Push','Seated dumbbell shoulder press',2,'8-12',120,'Back supported, ribs down, stop before arching'),
('Day 1 · Push','Cable lateral raise',3,'12-20',60,'Lead with the elbow and raise only to a comfortable shoulder height'),
('Day 1 · Push','Rope triceps pushdown',3,'10-15',60,'Keep elbows still and separate the rope at the bottom'),
('Day 2 · Pull','Lat pulldown',3,'8-12',120,'Use a comfortable shoulder-width grip; bring the bar to the upper chest'),
('Day 2 · Pull','Chest-supported dumbbell row',3,'8-12',120,'Keep your chest on the pad; pull elbows back and squeeze the shoulder blades'),
('Day 2 · Pull','Straight-arm cable pulldown',2,'12-15',75,'Keep a soft elbow bend and sweep the bar toward your thighs'),
('Day 2 · Pull','Reverse pec deck',3,'12-20',60,'Use a light load and lead with the elbows'),
('Day 2 · Pull','Hammer curl',3,'10-15',60,'Keep a neutral grip and your elbows still'),
('Day 4 · Lower A','Leg press (quad stance)',4,'8-12',150,'Use a comfortable depth; keep your lower back supported against the pad'),
('Day 4 · Lower A','Walking lunge (dumbbells)',3,'8-10 per leg',90,'Take a controlled stride, stay tall, and use support if balance is uncertain'),
('Day 4 · Lower A','Leg extension',3,'10-15',75,'Pause briefly at the top and lower under control'),
('Day 4 · Lower A','Lying leg curl',3,'10-15',75,'Keep hips pressed into the pad and lower slowly'),
('Day 4 · Lower A','Standing calf raise',3,'10-15',60,'Use a full comfortable stretch and pause at the top'),
('Day 5 · Upper','Cable fly',3,'10-15',75,'Keep a soft elbow bend and bring the hands together without shrugging'),
('Day 5 · Upper','Seated cable row',3,'8-12',120,'Stay tall and still; pull the handle toward your lower ribs'),
('Day 5 · Upper','Assisted neutral-grip pull-up',3,'6-10',120,'Start from a comfortable hang and pull without swinging'),
('Day 5 · Upper','Dumbbell lateral raise',3,'12-20',60,'Use a slight elbow bend; stop around shoulder height'),
('Day 5 · Upper','Cable curl',2,'10-15',60,'Keep elbows pinned and avoid swinging'),
('Day 5 · Upper','Overhead cable triceps extension',2,'10-15',60,'Keep elbows pointed forward and use a comfortable stretch'),
('Day 6 · Lower B + Core','Romanian deadlift (light, controlled)',2,'8-10',120,'Keep it light; hinge only through a comfortable range and stop around mid-shin'),
('Day 6 · Lower B + Core','Leg press (feet high and wide)',3,'10-15',120,'Keep your lower back against the pad; use a comfortable range'),
('Day 6 · Lower B + Core','Hip thrust',3,'8-12',90,'Keep your chin tucked, drive through the feet, and pause at the top'),
('Day 6 · Lower B + Core','Seated leg curl',3,'10-15',75,'Set the pad snugly above your heels and lower with control'),
('Day 6 · Lower B + Core','Seated calf raise',3,'12-20',60,'Use a deep comfortable stretch and pause at the top'),
('Day 6 · Lower B + Core','Cable crunch',3,'10-15',60,'Curl the ribs toward the pelvis; keep the hips still'),
('Day 6 · Lower B + Core','Plank',3,'30-45 sec',60,'Hold a straight line and keep the glutes and abs gently braced'),
]

# Manual map: requested exercise name -> exact dataset entry name. Keep editable.
OVERRIDES = {
    'Dumbbell bench press':'Dumbbell Bench Press',
    'Incline dumbbell press':'Incline Dumbbell Press',
    'Seated dumbbell shoulder press':'Seated Dumbbell Press',
    'Cable lateral raise':'Side Laterals to Front Raise',
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
    'Seated cable row':'Seated Cable Rows',
    'Assisted neutral-grip pull-up':'V-Bar Pullup',
    'Dumbbell lateral raise':'Side Laterals to Front Raise',
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
            out.append(exercise)
        else:
            reports.append(('NOT FOUND',name,found['name'] if found else '—'))
            out.append(dict(id=slug,name=name,day=day,sets=sets,reps=reps,rest=rest,cue=cue,target=[],secondary=[],instructions=[],images=[],matchedName=found['name'] if found else '',matchType='NOT FOUND'))
    (ROOT/'data.js').write_text('window.WORKOUT_DATA = '+json.dumps(out,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    print('\nIMAGE MATCH REPORT')
    for status,name,matched in reports: print(f'{status:10} | {name}'+(f' → {matched}' if status!='MATCHED' else ''))
    print(f'\n{sum(s=="MATCHED" for s,_,_ in reports)} matched, {sum(s=="EQUIVALENT" for s,_,_ in reports)} equivalents, {sum(s=="NOT FOUND" for s,_,_ in reports)} not found.')

if __name__=='__main__': main()
