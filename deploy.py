#!/usr/bin/env python3
"""Verify the site then commit + push to GitHub in one step.

   python deploy.py "commit message"
   python deploy.py                 # uses a default message

Runs check_site.py first and aborts if it fails, so the live site can never
receive a commit with missing image references.
"""

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else 'site update'

    print("== 1/3 health check ==")
    chk = run([sys.executable, 'check_site.py'])
    print(chk.stdout.rstrip())
    if chk.returncode != 0:
        print("\nABORTED: health check failed. Nothing was committed or pushed.")
        return 1

    print("\n== 2/3 commit ==")
    run(['git', 'add', '-A'])
    status = run(['git', 'status', '--short']).stdout.strip()
    if not status:
        print("No changes to commit.")
        return 0
    print(status)
    c = run(['git', 'commit', '-m', msg])
    print((c.stdout or c.stderr).strip()[-600:])
    if c.returncode != 0:
        print("ABORTED: commit failed.")
        return 1

    print("\n== 3/3 push ==")
    # wincred holds the stored GitHub credential; the bundled
    # 'helper-selector' hangs waiting on an interactive prompt.
    p = run(['git', '-c', 'credential.helper=', '-c', 'credential.helper=wincred',
             'push', 'origin', 'HEAD'], timeout=180)
    print((p.stdout or '') + (p.stderr or ''))
    if p.returncode != 0:
        print("PUSH FAILED (check credentials).")
        return 1

    print("Done. GitHub Pages usually goes live within ~1 minute.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
