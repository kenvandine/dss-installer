# About

Tool for initial setup of the Data Science Stack

## Dependencies

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-snapd-2
```

# Installation Instructions
## Build

### Dependances

- build-essential
- meson

### Build

```
rm -rf builddir
meson setup -Dprefix=$HOME/.local builddir
meson compile -C builddir --verbose
```

### Install

```
meson install -C builddir
```

### Run

```
$HOME/.local/bin/dss-installer
```
