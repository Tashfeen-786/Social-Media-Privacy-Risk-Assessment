"""
metadata_module.py
------------------
OPTIONAL local photo metadata (EXIF) awareness module.

Ethical rules enforced here:
  * the image is processed LOCALLY, in memory, and is never uploaded anywhere
  * no face recognition, no person identification, no tracking
  * no inference of hidden location beyond EXIF explicitly present in the file
  * metadata removal always writes a sanitised COPY; the original is untouched
"""

import io
import os
from typing import Any, Dict

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

INTERESTING_TAGS = {
    "Make", "Model", "Software", "DateTime", "DateTimeOriginal",
    "DateTimeDigitized", "Orientation", "LensModel", "Artist", "Copyright",
    "ExifImageWidth", "ExifImageHeight",
}


def read_image_metadata(image_bytes: bytes, filename: str = "upload") -> Dict[str, Any]:
    """Return EXIF metadata explicitly present in the file (local processing only)."""
    result: Dict[str, Any] = {
        "filename": os.path.basename(filename),
        "processed": "locally, in memory - the image was never uploaded elsewhere",
        "has_exif": False,
        "camera": {},
        "timestamps": {},
        "other": {},
        "gps_present": False,
        "privacy_warnings": [],
    }
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as exc:                                   # noqa: BLE001
        raise ValueError(f"Unsupported or corrupt image file: {exc}") from exc

    result["format"] = image.format
    result["size"] = {"width": image.width, "height": image.height}
    result["mode"] = image.mode

    exif = image.getexif()
    if not exif:
        result["privacy_warnings"].append(
            "No EXIF metadata found - this is the privacy-friendly case.")
        return result

    result["has_exif"] = True
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, str(tag_id))
        text = str(value)[:120]
        if tag in {"Make", "Model", "Software", "LensModel"}:
            result["camera"][tag] = text
        elif tag.startswith("DateTime"):
            result["timestamps"][tag] = text
        elif tag == "GPSInfo":
            result["gps_present"] = True
            gps = {}
            try:
                for key, val in exif.get_ifd(tag_id).items():
                    gps[GPSTAGS.get(key, str(key))] = str(val)[:80]
            except Exception:                                   # noqa: BLE001
                pass
            result["other"]["GPSInfo"] = gps
        elif tag in INTERESTING_TAGS:
            result["other"][tag] = text

    if result["camera"]:
        result["privacy_warnings"].append(
            "Camera / device information is embedded and can link photos to one device.")
    if result["timestamps"]:
        result["privacy_warnings"].append(
            "Capture timestamps are embedded and can reveal your routine.")
    if result["gps_present"]:
        result["privacy_warnings"].append(
            "GPS coordinates are embedded in this file. Remove metadata before sharing.")
    return result


def strip_metadata_to_copy(image_bytes: bytes, output_path: str) -> str:
    """
    Write a sanitised COPY without EXIF metadata.
    The original file is never modified.
    """
    image = Image.open(io.BytesIO(image_bytes))
    clean = Image.new(image.mode, image.size)
    clean.putdata(list(image.getdata()))
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    clean.save(output_path)
    return output_path


__all__ = ["read_image_metadata", "strip_metadata_to_copy"]
