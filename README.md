# WCD Design Static

A static website with localized Framer assets.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the asset downloader:
```bash
python download_framer_assets.py
```

3. Fix asset paths:
```bash
python fix_paths.py
```

## Structure

- `/public/assets/` - Contains all downloaded assets
  - `/fonts/` - Font files
  - `/icons/` - Icons and favicons
  - `/images/` - Images
  - `/scripts/` - JavaScript files
  - `/styles/` - CSS files
  - `/misc/` - Other asset types
