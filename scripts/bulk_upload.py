"""
Bulk upload script for seeding the missing persons database.

Usage (run from project root):
    python scripts/bulk_upload.py                        # uses 'gagan' as officer
    python scripts/bulk_upload.py --officer <username>   # match your login username

Directory layout:
    scripts/bulk_data/reported/        → images of missing persons (RegisteredCases)
    scripts/bulk_data/publicly_seen/   → images of sighted persons (PublicSubmissions)

Images can be jpg, jpeg, or png. The script generates realistic metadata for
each image and skips any image where no face is detected.
"""

import argparse
import json
import os
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ── Allow imports from project root ──────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import PIL.Image
import numpy as np

from pages.helper.data_models import RegisteredCases, PublicSubmissions
from pages.helper import db_queries
from pages.helper.utils import _ensure_model_silent, extract_face_mesh_from_frame

# ── Seed data ─────────────────────────────────────────────────────────────────

CITIES = [
    "Delhi", "Lucknow", "Kanpur", "Agra", "Meerut", "Varanasi",
    "Allahabad", "Mathura", "Bareilly", "Aligarh", "Moradabad",
    "Saharanpur", "Gorakhpur", "Firozabad", "Jhansi", "Noida",
    "Ghaziabad", "Faridabad", "Amritsar", "Ludhiana", "Jalandhar",
    "Chandigarh", "Dehradun", "Haridwar", "Rishikesh", "Shimla",
]

FIRST_NAMES_MALE = [
    "Anil", "Suresh", "Rajesh", "Ramesh", "Mahesh", "Dinesh", "Naresh",
    "Vikas", "Amit", "Deepak", "Rohit", "Mohit", "Sumit", "Sanjay",
    "Vijay", "Ajay", "Ravi", "Pavan", "Sachin", "Rahul", "Gaurav",
    "Nitin", "Pankaj", "Manish", "Rakesh", "Pradeep", "Hemant",
    "Vivek", "Arvind", "Harish",
]

FIRST_NAMES_FEMALE = [
    "Priya", "Sunita", "Geeta", "Seema", "Rekha", "Neha", "Pooja",
    "Kavita", "Anita", "Vandana", "Archana", "Sushma", "Meena",
    "Usha", "Asha", "Shweta", "Divya", "Nisha", "Sonia", "Ritu",
    "Poonam", "Anjali", "Sapna", "Komal", "Puja", "Swati",
]

LAST_NAMES = [
    "Sharma", "Gupta", "Singh", "Verma", "Yadav", "Mishra", "Tiwari",
    "Pandey", "Dubey", "Srivastava", "Chauhan", "Joshi", "Agarwal",
    "Bansal", "Garg", "Saxena", "Rastogi", "Chaudhary", "Shukla",
    "Tripathi", "Bajpai", "Gautam", "Kesarwani", "Awasthi",
]

AREAS = [
    "Sector {n} near main market",
    "near {landmark} railway station",
    "Civil Lines area",
    "{landmark} Chowk",
    "near {landmark} hospital",
    "Cantonment area",
    "near {landmark} bus stand",
    "old city area near {landmark} bazaar",
    "Model Town",
    "Gandhi Nagar",
    "Indira Nagar",
    "Rajiv Nagar",
    "Shastri Nagar",
    "Nehru Nagar",
    "Patel Nagar",
]

AREA_LANDMARKS = [
    "Central", "City", "New", "Old", "District", "Junction",
    "West", "East", "North", "South",
]

BIRTH_MARKS = [
    "Small mole on left cheek",
    "Scar on right forehead",
    "Dark birthmark near right ear",
    "Small scar below left eye",
    "Mole on chin",
    "",
    "",
    "Cut mark on left eyebrow",
    "Small mole on right cheek",
    "",
]

DESCRIPTIONS = [
    "Was last seen wearing a blue kurta and dark trousers.",
    "Wearing school uniform — white shirt and navy blue trousers.",
    "Last seen in a red saree near the vegetable market.",
    "Was wearing jeans and a white t-shirt when last seen.",
    "Elderly person, wearing traditional dhoti and kurta.",
    "Teenager, medium height, last seen near the school gate.",
    "Was attending a wedding and went missing from the venue.",
    "Left home in the morning and did not return.",
    "Known to visit the nearby temple every morning.",
    "Works as a daily-wage labourer; did not return from worksite.",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _random_name(gender: str = None) -> str:
    if gender == "female":
        first = random.choice(FIRST_NAMES_FEMALE)
    elif gender == "male":
        first = random.choice(FIRST_NAMES_MALE)
    else:
        first = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"


def _random_mobile() -> str:
    prefixes = ["98", "97", "96", "95", "94", "93", "80", "81", "70", "99"]
    return random.choice(prefixes) + str(random.randint(10000000, 99999999))


def _random_aadhaar() -> str:
    return str(random.randint(200000000000, 999999999999))


def _random_area(city: str) -> str:
    template = random.choice(AREAS)
    landmark = random.choice(AREA_LANDMARKS)
    n = random.randint(3, 25)
    return template.format(landmark=landmark, n=n) + f", {city}"


def _random_last_seen(city: str) -> str:
    days_ago = random.randint(1, 90)
    past_date = datetime.now() - timedelta(days=days_ago)
    date_str = past_date.strftime("%d %b %Y")
    area = _random_area(city)
    return f"{area} on {date_str}"


def _load_image_as_numpy(path: str) -> np.ndarray:
    img = PIL.Image.open(path).convert("RGB")
    return np.array(img)


def _image_files(folder: Path) -> list:
    exts = {".jpg", ".jpeg", ".png"}
    return [f for f in sorted(folder.iterdir()) if f.suffix.lower() in exts]


# ── Main upload routines ──────────────────────────────────────────────────────

def upload_reported(folder: Path, officer: str = "gagan") -> tuple[int, int]:
    """Process images in reported/ and insert RegisteredCases rows."""
    files = _image_files(folder)
    if not files:
        print("  No image files found in reported/")
        return 0, 0

    ok = skip = 0
    resources_dir = ROOT / "resources"
    resources_dir.mkdir(exist_ok=True)

    for img_path in files:
        print(f"  [{img_path.name}] ", end="", flush=True)
        try:
            image_np = _load_image_as_numpy(str(img_path))
            landmarks = extract_face_mesh_from_frame(image_np)
        except Exception as e:
            print(f"ERROR loading image: {e}")
            skip += 1
            continue

        if landmarks is None:
            print("no face detected — skipped")
            skip += 1
            continue

        case_id = str(uuid.uuid4())

        # Copy image to resources/
        dest = resources_dir / f"{case_id}.jpg"
        try:
            PIL.Image.open(img_path).convert("RGB").save(str(dest), "JPEG")
        except Exception as e:
            print(f"ERROR saving image: {e}")
            skip += 1
            continue

        city = random.choice(CITIES)
        age = random.randint(5, 75)

        case = RegisteredCases(
            id=case_id,
            submitted_by=officer,
            name=_random_name(),
            father_name=_random_name(gender="male"),
            age=str(age),
            complainant_name=_random_name(),
            complainant_mobile=_random_mobile(),
            complainant_email=None,
            adhaar_card=_random_aadhaar(),
            last_seen=_random_last_seen(city),
            address=_random_area(city),
            city=city,
            description=random.choice(DESCRIPTIONS),
            face_mesh=json.dumps(landmarks),
            status="NF",
            birth_marks=random.choice(BIRTH_MARKS),
            matched_with="",
        )

        try:
            db_queries.register_new_case(case)
            print(f"registered as {case_id[:8]}…")
            ok += 1
        except Exception as e:
            print(f"DB ERROR: {e}")
            if dest.exists():
                dest.unlink()
            skip += 1

    return ok, skip


def upload_publicly_seen(folder: Path) -> tuple[int, int]:
    """Process images in publicly_seen/ and insert PublicSubmissions rows."""
    files = _image_files(folder)
    if not files:
        print("  No image files found in publicly_seen/")
        return 0, 0

    ok = skip = 0
    resources_dir = ROOT / "resources"
    resources_dir.mkdir(exist_ok=True)

    for img_path in files:
        print(f"  [{img_path.name}] ", end="", flush=True)
        try:
            image_np = _load_image_as_numpy(str(img_path))
            landmarks = extract_face_mesh_from_frame(image_np)
        except Exception as e:
            print(f"ERROR loading image: {e}")
            skip += 1
            continue

        if landmarks is None:
            print("no face detected — skipped")
            skip += 1
            continue

        sub_id = str(uuid.uuid4())

        # Copy image to resources/ so the app can display it
        dest = resources_dir / f"{sub_id}.jpg"
        try:
            PIL.Image.open(img_path).convert("RGB").save(str(dest), "JPEG")
        except Exception as e:
            print(f"ERROR saving image: {e}")
            skip += 1
            continue

        city = random.choice(CITIES)

        submission = PublicSubmissions(
            id=sub_id,
            submitted_by=_random_name(),
            face_mesh=json.dumps(landmarks),
            location=_random_area(city),
            mobile=_random_mobile(),
            email=None,
            status="NF",
            birth_marks=random.choice(BIRTH_MARKS),
        )

        try:
            db_queries.new_public_case(submission)
            print(f"submitted as {sub_id[:8]}…")
            ok += 1
        except Exception as e:
            print(f"DB ERROR: {e}")
            if dest.exists():
                dest.unlink()
            skip += 1

    return ok, skip


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bulk upload images into the missing persons DB.")
    parser.add_argument(
        "--officer",
        default="gagan",
        help="Login username to assign as submitted_by for reported cases (default: gagan)",
    )
    args = parser.parse_args()

    # Change to project root so relative DB path resolves correctly
    os.chdir(ROOT)

    db_queries.create_db()

    _ensure_model_silent()

    bulk_dir = Path(__file__).parent / "bulk_data"
    reported_dir = bulk_dir / "reported"
    seen_dir = bulk_dir / "publicly_seen"

    print(f"\n=== Bulk upload — Reported (missing persons) [officer: {args.officer}] ===")
    ok_r, skip_r = upload_reported(reported_dir, officer=args.officer)
    print(f"  Done: {ok_r} registered, {skip_r} skipped\n")

    print("=== Bulk upload — Publicly Seen (sightings) ===")
    ok_s, skip_s = upload_publicly_seen(seen_dir)
    print(f"  Done: {ok_s} submitted, {skip_s} skipped\n")

    total_ok = ok_r + ok_s
    total_skip = skip_r + skip_s
    print(f"=== Summary: {total_ok} uploaded, {total_skip} skipped ===\n")


if __name__ == "__main__":
    main()
