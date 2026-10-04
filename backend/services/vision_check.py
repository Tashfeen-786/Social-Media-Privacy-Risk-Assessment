"""
vision_check.py
---------------
OPTIONAL local vision helper (project Step 7).

Counts faces in a locally supplied image using OpenCV Haar cascades so that
"children/minors in media" risk can be flagged when metadata is missing.

STRICT ETHICAL LIMITS
    * counts faces only - no recognition, no identification, no matching
    * never stores the image, never uploads it anywhere
    * no age/gender inference: a high count of small faces combined with
      self-reported child-related captions is treated as a *hint* only
    * fails gracefully (returns available=False) when OpenCV is absent
"""

from typing import Any, Dict

try:                                                    # optional dependency
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except Exception:                                       # noqa: BLE001
    _CV2_AVAILABLE = False


def vision_available() -> bool:
    return _CV2_AVAILABLE


def count_faces_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Count faces in an in-memory image. The image is never written to disk.

    Returns {available, faces, note} - `faces` is -1 when unavailable.
    """
    if not _CV2_AVAILABLE:
        return {"available": False, "faces": -1,
                "note": "OpenCV is not installed; the optional vision check is disabled."}
    try:
        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if image is None:
            return {"available": True, "faces": -1, "note": "Unsupported image format."}
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = detector.detectMultiScale(gray, 1.2, 5)
        return {
            "available": True,
            "faces": int(len(faces)),
            "note": ("Face COUNT only - no recognition, no identification and no age "
                     "inference. The image was processed locally and not stored."),
        }
    except Exception as exc:                            # noqa: BLE001
        return {"available": True, "faces": -1, "note": f"Vision check failed: {exc}"}


def count_faces(image_path: str) -> int:
    """Path-based helper kept for the batch/demo workflow."""
    if not _CV2_AVAILABLE:
        return -1
    with open(image_path, "rb") as handle:
        return count_faces_bytes(handle.read())["faces"]


__all__ = ["count_faces", "count_faces_bytes", "vision_available"]
