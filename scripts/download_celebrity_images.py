"""
Download celebrity face images using DuckDuckGo image search (no API key needed).

Usage (run from project root):
    uv run scripts/download_celebrity_images.py

    # Download to reported/ (missing person cases)
    uv run scripts/download_celebrity_images.py --dest reported

    # Download to publicly_seen/ (sighting submissions)
    uv run scripts/download_celebrity_images.py --dest publicly_seen

    # Both folders (different images for each)
    uv run scripts/download_celebrity_images.py --dest both

Dependencies (added automatically by uv inline metadata below):
    duckduckgo-search, requests, Pillow
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "duckduckgo-search>=6.0",
#   "requests>=2.31",
#   "Pillow>=10.0",
# ]
# ///

import argparse
import io
import time
import random
from pathlib import Path

import requests
from PIL import Image
from duckduckgo_search import DDGS

# ── Celebrity list ─────────────────────────────────────────────────────────────
# Well-known public figures with plenty of clear, front-facing press photos.
CELEBRITIES = [
    "Amitabh Bachchan",
    "Shah Rukh Khan",
    "Aamir Khan",
    "Salman Khan",
    "Deepika Padukone",
    "Priyanka Chopra",
    "Kareena Kapoor",
    "Aishwarya Rai",
    "Ranveer Singh",
    "Ranbir Kapoor",
    "Akshay Kumar",
    "Hrithik Roshan",
    "Kajol",
    "Vidya Balan",
    "Taapsee Pannu",
    "Ayushmann Khurrana",
    "Vicky Kaushal",
    "Katrina Kaif",
    "Anushka Sharma",
    "Alia Bhatt",
]

IMAGES_PER_CELEBRITY = 2
TIMEOUT = 10  # seconds per image download
MIN_SIZE = (80, 80)  # discard tiny/broken images

BULK_DATA = Path(__file__).parent / "bulk_data"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_filename(name: str, idx: int) -> str:
    return name.lower().replace(" ", "_") + f"_{idx + 1}.jpg"


def _download_image(url: str) -> Image.Image | None:
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        if img.size[0] < MIN_SIZE[0] or img.size[1] < MIN_SIZE[1]:
            return None
        return img
    except Exception:
        return None


def _search_images(query: str, max_results: int = 10) -> list[str]:
    """Return up to max_results image URLs from DuckDuckGo."""
    with DDGS() as ddgs:
        results = ddgs.images(
            keywords=f"{query} face photo",
            type_image="photo",
            size="Medium",
            max_results=max_results,
        )
    return [r["image"] for r in results if "image" in r]


def download_for_folder(dest_folder: Path, celebrities: list[str]) -> tuple[int, int]:
    dest_folder.mkdir(parents=True, exist_ok=True)
    ok = skip = 0

    for celebrity in celebrities:
        print(f"\n  {celebrity}")
        try:
            urls = _search_images(celebrity, max_results=15)
        except Exception as e:
            print(f"    search failed: {e}")
            skip += IMAGES_PER_CELEBRITY
            continue

        saved = 0
        for url in urls:
            if saved >= IMAGES_PER_CELEBRITY:
                break
            img = _download_image(url)
            if img is None:
                continue
            filename = _safe_filename(celebrity, saved)
            out_path = dest_folder / filename
            try:
                img.save(str(out_path), "JPEG")
                print(f"    [{saved + 1}] saved → {filename}")
                saved += 1
                ok += 1
            except Exception as e:
                print(f"    save error: {e}")

            time.sleep(random.uniform(0.3, 0.7))  # be polite

        if saved < IMAGES_PER_CELEBRITY:
            missed = IMAGES_PER_CELEBRITY - saved
            print(f"    only got {saved}/{IMAGES_PER_CELEBRITY} images")
            skip += missed

        time.sleep(random.uniform(0.5, 1.2))  # between celebrities

    return ok, skip


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Download celebrity images for bulk upload seeding.")
    parser.add_argument(
        "--dest",
        choices=["reported", "publicly_seen", "both"],
        default="reported",
        help="Which bulk_data subfolder to populate (default: reported)",
    )
    args = parser.parse_args()

    celebs = CELEBRITIES.copy()
    random.shuffle(celebs)

    if args.dest == "both":
        # Split list — first half to reported, second half to publicly_seen
        mid = len(celebs) // 2
        reported_celebs = celebs[:mid]
        seen_celebs = celebs[mid:]

        print(f"\n=== Downloading {len(reported_celebs)} celebrities → reported/ ===")
        ok_r, skip_r = download_for_folder(BULK_DATA / "reported", reported_celebs)
        print(f"\n  Done: {ok_r} saved, {skip_r} skipped")

        print(f"\n=== Downloading {len(seen_celebs)} celebrities → publicly_seen/ ===")
        ok_s, skip_s = download_for_folder(BULK_DATA / "publicly_seen", seen_celebs)
        print(f"\n  Done: {ok_s} saved, {skip_s} skipped")

        print(f"\n=== Total: {ok_r + ok_s} saved, {skip_r + skip_s} skipped ===\n")

    else:
        folder = BULK_DATA / args.dest
        print(f"\n=== Downloading {len(celebs)} celebrities → {args.dest}/ ===")
        ok, skip = download_for_folder(folder, celebs)
        print(f"\n=== Done: {ok} saved, {skip} skipped ===\n")


if __name__ == "__main__":
    main()
