# browser-use-cli

[![AUR version](https://img.shields.io/aur/version/browser-use-cli?logo=archlinux&color=1793d1)](https://aur.archlinux.org/packages/browser-use-cli)
[![AUR votes](https://img.shields.io/aur/votes/browser-use-cli)](https://aur.archlinux.org/packages/browser-use-cli)

> Arch Linux (AUR) package for the [browser-use](https://github.com/browser-use/browser-use) CLI.

This repository is the source for the [`browser-use-cli`](https://aur.archlinux.org/packages/browser-use-cli) AUR package.

## Installation

**Using an AUR helper:**

```bash
paru -S browser-use-cli
# or
yay -S browser-use-cli
```

**Manually:**

```bash
git clone https://aur.archlinux.org/browser-use-cli.git
cd browser-use-cli
makepkg -si
```

## What it provides

The package installs the `browser-use` CLI and its aliases (`browseruse`, `bu`, `browser`) for fast, persistent browser automation from the terminal.

Some Python dependencies are not available in the official Arch repos and may need to be installed separately (via AUR or pip).

## Updates

A [GitHub Actions workflow](.github/workflows/update-aur.yml) checks weekly for new upstream releases on PyPI and automatically syncs the PKGBUILD and pushes to AUR.

## Contributing

Open issues and PRs on [GitHub](https://github.com/clalos/browser-use-cli). For package-specific discussion, see the [AUR comments](https://aur.archlinux.org/packages/browser-use-cli).

## License

The PKGBUILD is provided under the terms of the packaged software's [MIT License](https://github.com/browser-use/browser-use/blob/main/LICENSE).
