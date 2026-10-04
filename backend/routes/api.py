"""
api.py
------
REST API for the Social Media Privacy Risk Assessment Framework.

Required endpoints
    POST   /api/assessment
    GET    /api/assessment/{id}
    GET    /api/assessment/{id}/recommendations
    POST   /api/assessment/simulate-improvement
    GET    /api/dashboard/stats
    GET    /api/privacy-checklist
    DELETE /api/assessment/{id}                    (optional, implemented)

Data-contract endpoints (file-driven exposure rubric)
    POST   /api/analyze          profile + posts JSON  -> 8-category rubric
    POST   /api/upload           two uploaded JSON files
    GET    /api/stats            aggregate snapshot

Supporting endpoints
    GET  /api/health, /api/questionnaire, /api/improvements, /api/demo-profile,
    GET  /api/methodology, /api/privacy-areas, /api/database/schema,
    GET  /api/sample-profile, POST /api/assessment/report, POST /api/photo-metadata
"""

import json
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field, field_validator

from backend.models.categories import (
    CATEGORIES,
    DEFAULT_WEIGHTS,
    DISCLAIMER,
    METHODOLOGY,
    RISK_LEVELS,
    RUBRIC_CATEGORIES,
    RUBRIC_WEIGHTS,
)
from backend.models.database import PrivacyDatabase
from backend.models.profile_schema import AnalyzePayload
from backend.models.questions import PRIVACY_AREAS, QUESTIONS, area_coverage, get_questionnaire
from backend.services.assessment_engine import (
    ValidationError,
    calculate_privacy_risk,
    demo_profile_answers,
)
from backend.services.exposure_rubric import score_profile
from backend.services.improvement_simulator import (
    RECOMMENDED_SET,
    list_improvements,
    simulate_improvement,
)
from backend.services.metadata_module import read_image_metadata
from backend.services.privacy_checklist import checklist_html, get_checklist
from backend.services.report_generator import generate_html_report, generate_pdf_report
from backend.services.vision_check import count_faces_bytes, vision_available
from backend.utils.security import valid_assessment_id

router = APIRouter(prefix="/api")
db = PrivacyDatabase()

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
SAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "samples")


# --------------------------------------------------------------------------
# Request / response models
# --------------------------------------------------------------------------
class AssessmentRequest(BaseModel):
    answers: Dict[str, str] = Field(..., description="question_id -> answer value")
    weights: Optional[Dict[str, float]] = Field(
        default=None, description="Optional Model-A category weight overrides")
    rubric_caps: Optional[Dict[str, int]] = Field(
        default=None, description="Optional Model-B category cap overrides")
    save: bool = Field(default=True, description="Persist privacy-minimised record")

    @field_validator("answers")
    @classmethod
    def non_empty(cls, value):
        if not value:
            raise ValueError("answers must not be empty")
        if len(value) > 200:
            raise ValueError("too many answers submitted")
        return value


class SimulationRequest(BaseModel):
    answers: Dict[str, str]
    improvements: List[str] = Field(default_factory=list)
    weights: Optional[Dict[str, float]] = None

    @field_validator("improvements")
    @classmethod
    def limit(cls, value):
        if len(value) > 50:
            raise ValueError("too many improvements requested")
        return value


class AssessmentResponse(BaseModel):
    assessment_id: str
    overall_score: float
    risk_level: str
    category_scores: Dict[str, float]
    exposure_rubric: Dict[str, Any]
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    disclaimer: str

    model_config = {"extra": "allow"}


# --------------------------------------------------------------------------
# Meta endpoints
# --------------------------------------------------------------------------
@router.get("/health")
def health():
    return {"status": "ok", "service": "Social Media Privacy Risk Assessment Framework",
            "version": "2.0.0", "questions": len(QUESTIONS),
            "models": ["PRIVACY ASSESSMENT SCORE (10)", "PRIVACY EXPOSURE RUBRIC (8)"],
            "vision_module": vision_available()}


@router.get("/questionnaire")
def questionnaire():
    data = get_questionnaire()
    data["categories"] = CATEGORIES
    data["weights"] = DEFAULT_WEIGHTS
    data["rubric_categories"] = RUBRIC_CATEGORIES
    data["rubric_weights"] = RUBRIC_WEIGHTS
    data["risk_levels"] = [{"min": a, "max": b, "level": c} for a, b, c in RISK_LEVELS]
    data["disclaimer"] = DISCLAIMER
    data["privacy_notice"] = (
        "This questionnaire never asks for your actual phone number, e-mail address, "
        "postal address, birth date, password or any child's personal details - only "
        "whether such information is publicly visible.")
    return data


@router.get("/methodology")
def methodology():
    return {"methodology": METHODOLOGY, "risk_levels":
            [{"min": a, "max": b, "level": c} for a, b, c in RISK_LEVELS],
            "disclaimer": DISCLAIMER}


@router.get("/privacy-areas")
def privacy_areas():
    return {"total_areas": len(PRIVACY_AREAS), "areas": PRIVACY_AREAS,
            "coverage": area_coverage()}


@router.get("/improvements")
def improvements():
    return {"improvements": list_improvements(), "recommended_set": RECOMMENDED_SET}


@router.get("/demo-profile")
def demo_profile():
    return {"name": "Demo User (fictional, synthetic)",
            "note": "Fully synthetic demonstration profile. No real person or account.",
            "answers": demo_profile_answers()}


@router.get("/sample-profile")
def sample_profile(name: str = Query("demo_oversharer", pattern="^[a-z_]{3,40}$")):
    """Return one of the bundled SYNTHETIC profile.json / posts.json samples."""
    folder = os.path.join(SAMPLES_DIR, name)
    if not os.path.isdir(folder):
        raise HTTPException(status_code=404, detail="Unknown sample profile.")
    with open(os.path.join(folder, "profile.json"), encoding="utf-8") as handle:
        profile = json.load(handle)
    with open(os.path.join(folder, "posts.json"), encoding="utf-8") as handle:
        posts = json.load(handle)
    return {"sample": name, "synthetic": True, "profile": profile, "posts": posts}


# --------------------------------------------------------------------------
# Assessment endpoints (Model A + Model B)
# --------------------------------------------------------------------------
@router.post("/assessment", response_model=AssessmentResponse, status_code=201)
def create_assessment(payload: AssessmentRequest):
    try:
        result = calculate_privacy_risk(payload.answers, payload.weights,
                                        rubric_caps=payload.rubric_caps)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if payload.save:
        db.save_assessment(result)
    return result


@router.get("/assessment/{assessment_id}")
def get_assessment(assessment_id: str):
    if not valid_assessment_id(assessment_id):
        raise HTTPException(status_code=400, detail="Malformed assessment id.")
    record = db.get_assessment(assessment_id)
    if not record:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    record["category_labels"] = CATEGORIES
    record["rubric_labels"] = RUBRIC_CATEGORIES
    record["disclaimer"] = DISCLAIMER
    return record


@router.get("/assessment/{assessment_id}/recommendations")
def assessment_recommendations(assessment_id: str):
    if not valid_assessment_id(assessment_id):
        raise HTTPException(status_code=400, detail="Malformed assessment id.")
    if not db.get_assessment(assessment_id):
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return {"assessment_id": assessment_id,
            "recommendations": db.get_recommendations(assessment_id)}


@router.delete("/assessment/{assessment_id}")
def delete_assessment(assessment_id: str):
    """User control / retention limitation: an assessment can always be erased."""
    if not valid_assessment_id(assessment_id):
        raise HTTPException(status_code=400, detail="Malformed assessment id.")
    if not db.delete_assessment(assessment_id):
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return {"deleted": True, "assessment_id": assessment_id}


@router.post("/assessment/simulate-improvement")
def simulate(payload: SimulationRequest):
    try:
        return simulate_improvement(payload.answers, payload.improvements, payload.weights)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/assessment/report")
def build_report(payload: AssessmentRequest, fmt: str = Query("html", pattern="^(html|pdf)$")):
    """Generate a downloadable report for a submitted questionnaire."""
    try:
        result = calculate_privacy_risk(payload.answers, payload.weights,
                                        rubric_caps=payload.rubric_caps)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if payload.save:
        db.save_assessment(result)
    path = generate_pdf_report(result) if fmt == "pdf" else generate_html_report(result)
    media = "application/pdf" if fmt == "pdf" else "text/html"
    return FileResponse(path, media_type=media, filename=os.path.basename(path))


# --------------------------------------------------------------------------
# Data-contract endpoints: file-driven exposure rubric
# --------------------------------------------------------------------------
@router.post("/analyze")
def analyze(payload: AnalyzePayload):
    """
    Analyse a SYNTHETIC exported profile + posts payload with the rule-based
    8-category exposure rubric. No scraping, no network calls.
    """
    if not isinstance(payload.profile, dict):
        raise HTTPException(status_code=422, detail="profile must be an object.")
    if len(payload.posts) > 2000:
        raise HTTPException(status_code=413, detail="Too many posts (max 2000).")
    try:
        return score_profile(payload.profile, payload.posts, payload.caps)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/upload")
async def upload(profile: UploadFile = File(...), posts: UploadFile = File(...)):
    """Upload profile.json and posts.json (synthetic/self-owned exports only)."""
    profile_bytes = await profile.read()
    posts_bytes = await posts.read()
    if len(profile_bytes) > MAX_JSON_BYTES or len(posts_bytes) > MAX_JSON_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 2 MB each).")
    try:
        profile_data = json.loads(profile_bytes.decode("utf-8"))
        posts_data = json.loads(posts_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {exc}") from exc
    if not isinstance(profile_data, dict) or not isinstance(posts_data, list):
        raise HTTPException(status_code=422,
                            detail="profile.json must be an object and posts.json an array.")
    return score_profile(profile_data, posts_data)


@router.get("/stats")
def stats():
    """Aggregate snapshot (alias of /api/dashboard/stats, kept per the data contract)."""
    return db.dashboard_stats()


# --------------------------------------------------------------------------
# Dashboard / checklist / schema
# --------------------------------------------------------------------------
@router.get("/dashboard/stats")
def dashboard_stats():
    data = db.dashboard_stats()
    data["category_labels"] = CATEGORIES
    data["rubric_labels"] = RUBRIC_CATEGORIES
    data["disclaimer"] = DISCLAIMER
    return data


@router.get("/privacy-checklist")
def privacy_checklist(fmt: str = Query("json", pattern="^(json|html)$")):
    if fmt == "html":
        return HTMLResponse(checklist_html())
    return get_checklist()


@router.get("/database/schema")
def database_schema():
    return {"database": "SQLite (privacy-first)", "tables": db.schema_info(),
            "never_stored": ["phone numbers", "e-mail addresses", "home addresses",
                             "birth dates", "passwords", "exact locations",
                             "private messages", "raw questionnaire answers",
                             "children's personal details"]}


# --------------------------------------------------------------------------
# Optional local photo modules (metadata + vision)
# --------------------------------------------------------------------------
@router.post("/photo-metadata")
async def photo_metadata(file: UploadFile = File(...), count_faces: bool = Query(False)):
    """
    Local EXIF metadata viewer. The image is processed in memory and never
    uploaded elsewhere or stored. Optional face COUNT (no recognition).
    """
    content = await file.read()
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 8 MB).")
    try:
        result = read_image_metadata(content, file.filename or "upload")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if count_faces:
        result["vision"] = count_faces_bytes(content)
    return result
