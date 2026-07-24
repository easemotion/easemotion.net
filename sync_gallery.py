#!/usr/bin/env python3
"""Scan gallery folders and sync projects.json to match actual files on disk.
   Windows-safe path handling."""

import json, os

JSON_PATH = 'data/projects.json'
GALLERY_BASE = 'images/projects'

# Load current JSON
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build a dict of project_id -> project entry for all projects
all_projects = []
for section in ['motion', 'illustration']:
    for p in data.get(section, []):
        p['_section'] = section
        all_projects.append(p)

# Scan all gallery folders (Windows-safe: use os.scandir)
gallery_folders = {}
for entry in os.scandir(GALLERY_BASE):
    if not entry.is_dir():
        continue
    gallery_path = os.path.join(entry.path, 'gallery')
    if not os.path.isdir(gallery_path):
        continue
    files = sorted([
        f for f in os.listdir(gallery_path)
        if os.path.isfile(os.path.join(gallery_path, f))
        and not f.startswith('.')
    ])
    gallery_folders[entry.name] = files
    if files:
        print(f"  {entry.name}: {len(files)} files")

# Update each project's gallery entry
updated_count = 0
for p in all_projects:
    pid = p['id']
    expected = gallery_folders.get(pid, [])
    
    # Build gallery paths with forward slashes (web standard)
    expected_paths = [f'{GALLERY_BASE}/{pid}/gallery/{f}' for f in expected]
    
    current = p.get('gallery', [])
    
    if expected_paths != current:
        if expected_paths:
            p['gallery'] = expected_paths
        else:
            p.pop('gallery', None)
        updated_count += 1
        added = len([e for e in expected_paths if e not in current])
        removed = len([c for c in current if c not in expected_paths])
        change = f"({'+'+str(added) if added else ''}{'-'+str(removed) if removed else ''})" if added or removed else "(reordered)"
        print(f"  → {pid}: {len(current)} → {len(expected_paths)} {change}")

# Rebuild JSON preserving order
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

print(f"\n✅ {updated_count} project(s) updated.")
