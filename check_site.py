#!/usr/bin/env python3
"""Pre-push health check for the Easemotion site.

Fails (exit 1) if any image referenced by the site is missing on disk,
or if any live-external URL is still referenced (the old WordPress host
is dead, so http(s) references are a guaranteed broken image).

Usage:  python check_site.py        # verify only
        python check_site.py --fix  # re-point dead thumbs at a local gallery image
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(ROOT, 'data', 'projects.json')
SECTIONS = ('motion', 'illustration')
IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif', '.svg')
HTML_FILES = [f for f in os.listdir(ROOT) if f.endswith('.html')]
JS_FILES = [os.path.join('js', f) for f in os.listdir(os.path.join(ROOT, 'js'))
            if f.endswith('.js')] if os.path.isdir(os.path.join(ROOT, 'js')) else []


def disk(path):
    """Map a web-style relative path to an absolute on-disk path."""
    return os.path.join(ROOT, path.replace('/', os.sep))


def exists(path):
    return os.path.isfile(disk(path))


def list_images(folder_rel):
    """Return web-style paths of real image files directly inside folder_rel."""
    d = disk(folder_rel)
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if os.path.isfile(os.path.join(d, f)) and f.lower().endswith(IMG_EXT) \
                and f != 'Thumbs.db' and not f.startswith('.'):
            out.append(f"{folder_rel}/{f}")
    return out


def load():
    with open(JSON_PATH, encoding='utf-8') as fh:
        return json.load(fh)


def save(data):
    with open(JSON_PATH, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def iter_projects(data):
    for sec in SECTIONS:
        for p in data.get(sec, []):
            yield sec, p


def audit(data):
    """Return (broken, external) lists of (project_id, field, value)."""
    broken, external = [], []
    for sec, p in iter_projects(data):
        pid = p.get('id', '?')
        refs = []
        if p.get('thumb'):
            refs.append(('thumb', p['thumb']))
        for i, g in enumerate(p.get('gallery') or []):
            refs.append((f'gallery[{i}]', g))
        for i, g in enumerate(p.get('images') or []):
            refs.append((f'images[{i}]', g))
        for field, val in refs:
            if re.match(r'^https?://', val) or val.startswith('//'):
                external.append((pid, field, val))
            elif not exists(val):
                broken.append((pid, field, val))
    return broken, external


def fix(data):
    """Re-point dead thumbs and prune dead gallery/image refs. Returns list of changes."""
    changes = []
    for sec, p in iter_projects(data):
        pid = p.get('id', '?')
        # drop dead/missing gallery + images entries
        for key in ('gallery', 'images'):
            if not p.get(key):
                continue
            keep = [v for v in p[key]
                    if not re.match(r'^https?://', v) and exists(v)]
            if keep != p[key]:
                changes.append(f"{pid}.{key}: dropped {len(p[key]) - len(keep)} bad ref(s)")
                if keep:
                    p[key] = keep
                else:
                    del p[key]
        # if the gallery is empty but files exist on disk, adopt them
        if not p.get('gallery') and not p.get('images'):
            on_disk = list_images(f"images/projects/{pid}/gallery")
            if on_disk:
                p['gallery'] = on_disk
                changes.append(f"{pid}.gallery: filled {len(on_disk)} from disk")
        # re-point a dead or external thumb at the first real local image
        thumb = p.get('thumb', '')
        bad_thumb = (not thumb) or re.match(r'^https?://', thumb) or not exists(thumb)
        if bad_thumb:
            cands = [v for v in (p.get('gallery') or []) if exists(v)]
            if not cands:
                cands = [v for v in (p.get('images') or []) if exists(v)]
            if not cands:
                cands = list_images(f"images/projects/{pid}")
            if cands:
                p['thumb'] = cands[0]
                changes.append(f"{pid}.thumb: -> {cands[0]}")
            else:
                changes.append(f"{pid}.thumb: NO IMAGE AVAILABLE (left as-is)")
    return changes


def audit_html():
    """Find external i0.wp.com references left in HTML/JS."""
    hits = []
    for f in HTML_FILES + JS_FILES:
        path = os.path.join(ROOT, f)
        try:
            txt = open(path, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        for m in re.finditer(r'https?://[^\s"\'<>]*wp-content[^\s"\'<>]*', txt):
            hits.append((f, m.group(0)))
    return hits


def main():
    data = load()
    if '--fix' in sys.argv:
        changes = fix(data)
        if changes:
            save(data)
            print("Applied fixes:")
            for c in changes:
                print("  ", c)
        else:
            print("Nothing to fix.")
        print()

    data = load()
    broken, external = audit(data)
    html_hits = audit_html()

    projects = list(iter_projects(data))
    total_imgs = sum(len(p.get('gallery') or []) + len(p.get('images') or [])
                     for _, p in projects)

    print(f"Projects: {len(projects)}   referenced gallery/images: {total_imgs}")
    ok = True

    if broken:
        ok = False
        print(f"\n[FAIL] {len(broken)} reference(s) point to files that do not exist:")
        for pid, field, val in broken:
            print(f"   {pid}.{field}: {val}")
    else:
        print("[OK] every local image reference exists on disk")

    if external:
        ok = False
        print(f"\n[FAIL] {len(external)} reference(s) still point at an external URL "
              f"(dead WordPress host = guaranteed broken image):")
        for pid, field, val in external:
            print(f"   {pid}.{field}: {val[:110]}")
    else:
        print("[OK] no external image URLs in projects.json")

    if html_hits:
        ok = False
        print(f"\n[FAIL] {len(html_hits)} dead wp-content reference(s) in HTML/JS:")
        for f, val in html_hits:
            print(f"   {f}: {val[:110]}")
    else:
        print("[OK] no wp-content references in HTML/JS")

    # projects with no usable image at all — these render blank on the site
    imageless = [p['id'] for _, p in projects
                 if not (p.get('thumb') and exists(p.get('thumb', '')))]
    if imageless:
        print(f"\n[WARN] {len(imageless)} project(s) have no usable thumbnail "
              f"(hidden by the site's fallback, but worth filling):")
        print("   " + ", ".join(imageless))

    print()
    if ok:
        print("RESULT: PASS — safe to commit and push")
        return 0
    print("RESULT: FAIL — run `python check_site.py --fix`, or add the missing images")
    return 1


if __name__ == '__main__':
    sys.exit(main())
