#!/usr/bin/env python
"""Verify that a built package satisfies the Python metadata it ships.

Usage: check-deps.py PKGDIR

PKGDIR is makepkg's staging directory for the package (``pkg/<pkgname>``):
its ``.PKGINFO`` lists the declared dependencies and its ``usr/`` tree holds
the installed distributions. Every ``Requires-Dist`` entry of every
distribution that applies on Linux must be either:

* bundled in the package itself, at a version that satisfies the pin, or
* declared in ``depends``/``optdepends`` as ``python-<name>``.

This catches upstream adding a new dependency, or bumping the pin of a
bundled one, without the PKGBUILD following.
"""

import re
import sys
from importlib.metadata import Distribution
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def declared_names(pkginfo: Path) -> set[str]:
    """Canonical names satisfied by the depend/optdepend entries of .PKGINFO."""
    names: set[str] = set()
    for line in pkginfo.read_text().splitlines():
        key, _, value = line.partition(' = ')
        if key not in ('depend', 'optdepend'):
            continue
        pkg = re.split(r'[<>=:]', value, maxsplit=1)[0].strip()
        names.add(canonicalize_name(pkg))
        if pkg.startswith('python-'):
            names.add(canonicalize_name(pkg[len('python-'):]))
    return names


def main(pkgdir: Path) -> int:
    declared = declared_names(pkgdir / '.PKGINFO')
    bundled = {
        canonicalize_name(dist.metadata['Name']): dist
        for dist in map(Distribution.at, pkgdir.glob('usr/lib/python3.*/site-packages/*.dist-info'))
    }
    if not bundled:
        print(f'error: no distributions found under {pkgdir}', file=sys.stderr)
        return 1

    errors = []
    checked = 0
    for name, dist in sorted(bundled.items()):
        for req in map(Requirement, dist.requires or []):
            if req.marker and not req.marker.evaluate({'extra': ''}):
                continue
            checked += 1
            dep = canonicalize_name(req.name)
            if dep in bundled:
                version = bundled[dep].version
                if not req.specifier.contains(version, prereleases=True):
                    errors.append(f'{name} requires {req}, but the package bundles {dep} {version}')
            elif dep not in declared:
                errors.append(f'{name} requires {req}, which is neither bundled nor in depends/optdepends')

    for error in errors:
        print(f'error: {error}', file=sys.stderr)
    print(f'checked {checked} requirements across {len(bundled)} distributions, {len(errors)} problem(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
