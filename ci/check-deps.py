#!/usr/bin/env python
"""Verify that the built package satisfies the Python metadata it ships.

Usage: check-deps.py PKGROOT SRCINFO

PKGROOT is a directory containing the extracted package (its ``usr/`` tree).
Every ``Requires-Dist`` entry of every distribution installed there that
applies on Linux must be either:

* bundled in the package itself, at a version that satisfies the pin, or
* listed in ``depends``/``optdepends`` of the PKGBUILD as ``python-<name>``.

This catches upstream adding a new dependency, or bumping the pin of a
bundled one, without the PKGBUILD following.
"""

import re
import sys
from email.parser import Parser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def pkgbuild_names(srcinfo: Path) -> set[str]:
    """Canonical names satisfied by depends/optdepends in .SRCINFO."""
    names: set[str] = set()
    for line in srcinfo.read_text().splitlines():
        key, _, value = line.strip().partition(' = ')
        if key not in ('depends', 'optdepends'):
            continue
        pkg = re.split(r'[<>=:]', value, maxsplit=1)[0].strip()
        names.add(canonicalize_name(pkg))
        if pkg.startswith('python-'):
            names.add(canonicalize_name(pkg[len('python-'):]))
    return names


def bundled_dists(pkgroot: Path) -> dict[str, tuple[str, list[str]]]:
    """Canonical name -> (version, Requires-Dist lines) for shipped dists."""
    dists = {}
    for metadata in pkgroot.glob('usr/lib/python3.*/site-packages/*.dist-info/METADATA'):
        msg = Parser().parsestr(metadata.read_text())
        dists[canonicalize_name(msg['Name'])] = (msg['Version'], msg.get_all('Requires-Dist') or [])
    return dists


def main(pkgroot: Path, srcinfo: Path) -> int:
    provided = pkgbuild_names(srcinfo)
    bundled = bundled_dists(pkgroot)
    if not bundled:
        print(f'error: no distributions found under {pkgroot}', file=sys.stderr)
        return 1

    errors = []
    checked = 0
    for dist, (_, requires) in sorted(bundled.items()):
        for line in requires:
            req = Requirement(line)
            if req.marker and not req.marker.evaluate({'extra': ''}):
                continue
            checked += 1
            name = canonicalize_name(req.name)
            if name in bundled:
                version = bundled[name][0]
                if not req.specifier.contains(version, prereleases=True):
                    errors.append(f'{dist} requires {req}, but the PKGBUILD bundles {name} {version}')
            elif name not in provided:
                errors.append(f'{dist} requires {req}, which is neither bundled nor in depends/optdepends')

    for error in errors:
        print(f'error: {error}', file=sys.stderr)
    print(f'checked {checked} requirements across {len(bundled)} distributions, {len(errors)} problem(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
