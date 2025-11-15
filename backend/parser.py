import re
from typing import List, Dict
import math
import io
import numpy as np

# Optional OCR support
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False
    # Try to detect EasyOCR as a fallback (may handle handwriting better)
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    EASYOCR_AVAILABLE = False

HEADING_RE = re.compile(r"(?im)^(chapter\s+\d+[:.-]?\s*(.*)|\bchapter\b.*$)", re.MULTILINE)


def extract_topics(text: str) -> List[Dict]:
    """Try to extract chapters/sections from syllabus text.

    This is a simple heuristic parser:
    - Look for lines starting with 'Chapter X' (case-insensitive)
    - If none found, try splitting on patterns like "Chapter" or periods followed by "Chapter"
    - If still none, split on double newlines and use chunks
    - Return list of {'title': str, 'length': int}
    """
    if not text:
        return []

    # Normalize simple whitespace
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Quick heuristic: if user provided a short manual list (many short lines),
    # treat each non-empty line as a separate topic.
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if len(lines) >= 2 and all(len(l) < 120 for l in lines):
        # If there are several short lines, assume manual topic list
        topics = []
        for l in lines:
            topics.append({
                "title": l[:120],
                "content": "",
                "length": len(l),
            })
        return topics

    headings = []
    for match in re.finditer(r"(?im)^chapter\s+\d+\b.*$", text, flags=re.MULTILINE):
        h = match.group(0).strip()
        headings.append(h)

    topics = []
    if headings:
        # Split by headings: find positions
        parts = re.split(r"(?im)^chapter\s+\d+\b.*$", text, flags=re.MULTILINE)
        # re.split includes leading text before first heading; pair headings with parts
        # Build titles from headings list
        for i, h in enumerate(headings):
            content = parts[i+1] if i+1 < len(parts) else ""
            topics.append({
                "title": h,
                "content": content.strip(),
                "length": len(content),
            })
    else:
        # Try splitting on " Chapter " pattern (inline chapters)
        chapter_parts = re.split(r'\s+chapter\s+\d+:', text, flags=re.IGNORECASE)
        if len(chapter_parts) > 1:
            # Found inline chapters, extract them
            for i, part in enumerate(chapter_parts[1:]):
                # Extract title (first part before period or colon)
                lines = part.strip().split('\n')
                title = lines[0][:80].strip()
                if not title:
                    title = f"Chapter {i+1}"
                topics.append({
                    "title": f"Chapter {i+1}: {title}",
                    "content": part.strip(),
                    "length": len(part),
                })
        else:
            # Fallback: split into paragraphs/sections by two newlines
            chunks = [c.strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
            # Keep chunks that are reasonably sized
            for i, c in enumerate(chunks):
                if len(c) < 30:
                    continue
                title = c.split('\n')[0][:80]
                topics.append({
                    "title": title,
                    "content": c,
                    "length": len(c),
                })

    # If still empty, create a single topic
    if not topics:
        topics = [{"title": "Syllabus", "content": text, "length": len(text)}]

    return topics


def extract_text_from_image(image_bytes: bytes, use_gpu: bool = False) -> str:
    """Attempt to extract text from an image (bytes) using pytesseract.

    Returns the extracted text or an empty string if OCR not available.
    """
    if not image_bytes:
        return ""
    # Prefer pytesseract if available
    if OCR_AVAILABLE:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img)
            return text or ""
        except Exception:
            # fall through to EasyOCR if available
            pass

    # Try EasyOCR if available (better on some handwriting)
    if EASYOCR_AVAILABLE:
        try:
            reader = easyocr.Reader(['en'], gpu=use_gpu)
            # easyocr expects image path or numpy array; we pass bytes via PIL
            img = Image.open(io.BytesIO(image_bytes))
            res = reader.readtext(np.array(img))
            # `res` is list of (bbox, text, confidence)
            texts = [r[1] for r in res if r[2] > 0.3]
            return "\n".join(texts) if texts else ""
        except Exception:
            return ""

    return ""


def generate_plan(topics: List[Dict], plan_length: int = 14, hours_per_day: float = 2.0, exam_type: str = "final", review_day_fraction: float = None) -> List[Dict]:
    """Generate a simple day-by-day plan.

    Heuristic:
    - Compute total length of all topics
    - Allocate total available minutes = plan_length * hours_per_day * 60
    - For each topic, estimate minutes proportionally to its length
    - Assign topics to days trying to fill each day's minutes
    - Insert a review day every 7th day where no new topics assigned (marked as review)
    """
    capacity = int(hours_per_day * 60)
    total_capacity = plan_length * capacity
    total_length = sum(t.get("length", 1) for t in topics) or 1

    # Reserve a modest chunk of total capacity for review days and ensure
    # review days are fewer than study days. We pick a small fraction of days
    # to be review days and cap reserved minutes to the available review-day minutes.
    if review_day_fraction is not None:
        try:
            review_day_fraction = float(review_day_fraction)
        except Exception:
            review_day_fraction = None

    if review_day_fraction is not None:
        # clamp between 0 and 0.3
        review_day_fraction = max(0.0, min(0.3, review_day_fraction))
        review_share = review_day_fraction
    else:
        if exam_type == "final":
            review_day_fraction = 0.08  # 8% of days reserved for review (reduced from 15%)
            review_share = 0.08  # ~8% of total time reserved for review
        else:
            review_day_fraction = 0.04  # 4% of days for regular tests (reduced from 8%)
            review_share = 0.04

    # Compute a small number of review days, ensure at least 1 for multi-day plans
    if plan_length <= 1:
        review_days_count = 0
    else:
        review_days_count = max(1, int(plan_length * review_day_fraction))
        # Ensure there is at least one more study day than review days
        if review_days_count >= plan_length:
            review_days_count = max(0, plan_length - 1)

    # Reserve minutes for review but don't exceed the physical minutes available
    reserved_for_review = int(total_capacity * review_share)
    max_review_capacity = review_days_count * capacity
    if reserved_for_review > max_review_capacity and max_review_capacity > 0:
        reserved_for_review = max_review_capacity

    # Available minutes for topic study
    topic_capacity = max(0, total_capacity - reserved_for_review)

    # Estimate minutes per topic (proportional) but reduce aggressiveness to be faster
    total_minutes = 0
    for t in topics:
        proportion = t.get("length", 0) / total_length
        # base estimate scaled to topic_capacity
        t["estimated_minutes"] = max(5, int(round(proportion * topic_capacity)))
        total_minutes += t["estimated_minutes"]

    # If estimated total exceeds topic_capacity (due to rounding), scale down proportionally
    if total_minutes > topic_capacity and total_minutes > 0:
        scale = topic_capacity / total_minutes
        total_minutes = 0
        for t in topics:
            t["estimated_minutes"] = max(3, int(round(t["estimated_minutes"] * scale)))
            total_minutes += t["estimated_minutes"]

    # Create day containers
    days = []
    for d in range(plan_length):
        days.append({"day": d + 1, "topics": [], "total_minutes": 0, "is_review": False})

    # Choose which days are review days and space them across the plan
    if review_days_count > 0:
        # spread review days evenly across the plan
        positions = []
        for i in range(review_days_count):
            pos = int(round((i + 1) * plan_length / (review_days_count + 1))) - 1
            pos = max(0, min(plan_length - 1, pos))
            if pos not in positions:
                positions.append(pos)
        # mark chosen positions as review days
        for d in positions:
            days[d]["is_review"] = True

    # Helper to allocate minutes of a topic across days following a day order
    def allocate_minutes(title: str, minutes: int, day_order: List[int]):
        remaining = minutes
        part_idx = 1
        while remaining > 0:
            allocated_in_pass = False
            for di in day_order:
                day = days[di]
                # allow placing on any day (including review) but respect capacity
                avail = capacity - day["total_minutes"]
                if avail <= 0:
                    continue
                take = min(remaining, avail)
                part_title = title
                if minutes > take:
                    part_title = f"{title} (Part {part_idx})"
                day["topics"].append({"title": part_title, "estimated_minutes": take})
                day["total_minutes"] += take
                remaining -= take
                part_idx += 1
                allocated_in_pass = True
                if remaining <= 0:
                    break
            if not allocated_in_pass:
                # No available space anywhere (shouldn't happen after scaling) — break to avoid infinite loop
                break

    # Determine day order based on exam type
    if exam_type == "regular_test":
        # front-load: earliest to latest
        day_order = [i for i in range(plan_length) if not days[i]["is_review"]]
        # Sort topics by size descending to pack big topics first
        topics_sorted = sorted(topics, key=lambda x: x.get("length", 0), reverse=True)
        for t in topics_sorted:
            allocate_minutes(t.get("title"), t.get("estimated_minutes"), day_order)
    else:
        # final: spread topics round-robin across non-review days
        non_review_days = [i for i in range(plan_length) if not days[i]["is_review"]]
        if not non_review_days:
            non_review_days = list(range(plan_length))
        next_idx = 0
        for t in topics:
            # create a day order starting at next_idx to spread allocations
            order = non_review_days[next_idx:] + non_review_days[:next_idx]
            allocate_minutes(t.get("title"), t.get("estimated_minutes"), order)
            # advance next_idx for next topic to encourage spreading
            next_idx = (next_idx + 1) % len(non_review_days)

    # Build daily summary
    for d in days:
        if d["is_review"]:
            d["daily_summary"] = "Review day: revisit previous topics and do practice questions."
        elif d["topics"]:
            titles = [t["title"] for t in d["topics"]]
            d["daily_summary"] = f"Today's goal: {', '.join(titles[:2])} + practice problems ({len(d['topics'])} topics)."
        else:
            d["daily_summary"] = "Light day: review notes or rest."

    return days
