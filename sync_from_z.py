#!/usr/bin/env python3
"""Sync gallery images from Z:\Portfolio to website, then update projects.json.
   Mapping: Z:\Portfolio folder -> website project ID(s)"""

import json, os, shutil, sys

Z_PORTFOLIO = 'Z:/Portfolio'
WEBSITE_IMG = 'images/projects'
JSON_PATH = 'data/projects.json'

# Mapping: Z:\Portfolio folder name -> list of website project IDs
Z_TO_PROJECT = {
    'Cathy':               ['cathay-pacific-rtbo'],
    'Zen':                 ['zen-portable'],
    'OLAY Pro X 無添加系列': ['olay-pro-x'],
    'KIX':                 ['kix-rebrand', 'kix-fight-club', 'kix-chinese-action', 'kix-christmas'],
    'olay sea weed':       ['olay-cell-level', 'olay-diamond'],
    'CM+':                 ['cm-plus-rebrand'],
    'APO':                 ['art-in-motion'],
    'HKEX':                ['hkex-led'],
    'GiGi Leung Concert':  ['gigi-leung'],
    'Andy Hui':            ['andy-hui'],
    'Kitkat':              ['kitkat'],
    'light up':            ['lights-up'],
    'mobile talk':         ['mobiletalk-osaka'],
    'Phil Concert 2018':   ['philromantic'],
    'Sogo':                ['sogo-autumn', 'sogo-hanami', 'sogo-newyear', 'sogo-family'],
    'HKCA':                ['hkca'],
    'HSMC':                ['hsmc'],
}

# ---- Step 1: Sync images from Z: to website ----
total_copied = 0
total_deleted = 0

for z_folder, project_ids in Z_TO_PROJECT.items():
    z_path = os.path.join(Z_PORTFOLIO, z_folder)
    if not os.path.isdir(z_path):
        print(f"⚠ Z:\\Portfolio\\{z_folder} not found, skipping")
        continue
    
    # Get all image files from Z:
    z_files = sorted([
        f for f in os.listdir(z_path)
        if os.path.isfile(os.path.join(z_path, f))
        and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        and not f.startswith('.')
    ])
    
    if not z_files:
        print(f"  {z_folder}: no images found")
        continue
    
    for pid in project_ids:
        gal_dir = os.path.join(WEBSITE_IMG, pid, 'gallery')
        os.makedirs(gal_dir, exist_ok=True)
        
        # Files currently in website gallery
        existing = set([
            f for f in os.listdir(gal_dir)
            if os.path.isfile(os.path.join(gal_dir, f))
        ])
        z_set = set(z_files)
        
        # Copy new/updated files
        copied = 0
        for f in z_files:
            src = os.path.join(z_path, f)
            dst = os.path.join(gal_dir, f)
            if f not in existing or os.path.getmtime(src) > os.path.getmtime(dst):
                shutil.copy2(src, dst)
                copied += 1
        
        # Delete files that are in website but not in Z:
        deleted = 0
        for f in existing:
            if f not in z_set:
                os.remove(os.path.join(gal_dir, f))
                deleted += 1
        
        if copied or deleted:
            print(f"  {pid} ({z_folder}): +{copied} / -{deleted} = {len(z_files)} files")
            total_copied += copied
            total_deleted += deleted
        else:
            print(f"  {pid} ({z_folder}): {len(z_files)} files (unchanged)")

print(f"\n📦 Sync complete: +{total_copied} copied, -{total_deleted} deleted")

# ---- Step 2: Update projects.json ----
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

all_projects = []
for section in ['motion', 'illustration']:
    for p in data.get(section, []):
        p['_section'] = section
        all_projects.append(p)

updated = 0
for p in all_projects:
    pid = p['id']
    gal_dir = os.path.join(WEBSITE_IMG, pid, 'gallery')
    
    if not os.path.isdir(gal_dir):
        continue
    
    files = sorted([
        f for f in os.listdir(gal_dir)
        if os.path.isfile(os.path.join(gal_dir, f))
        and not f.startswith('.')
    ])
    
    expected_paths = [f'{WEBSITE_IMG}/{pid}/gallery/{f}' for f in files]
    current = p.get('gallery', [])
    
    if expected_paths != current:
        if expected_paths:
            p['gallery'] = expected_paths
        else:
            p.pop('gallery', None)
        updated += 1
        added = len([e for e in expected_paths if e not in current])
        removed = len([c for c in current if c not in expected_paths])
        print(f"  JSON {pid}: {len(current)} → {len(expected_paths)}")

# Rebuild JSON
new_data = {
    'site': data.get('site', {}),
    'motion': [p for p in all_projects if p['_section'] == 'motion'],
    'illustration': [p for p in all_projects if p['_section'] == 'illustration'],
}
for section in ['motion', 'illustration']:
    for p in new_data[section]:
        del p['_section']

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ JSON updated: {updated} project(s) changed")
print(f"   Run: python3 build.py && git add -A && git commit -m 'gallery sync' && git push")
