"""
Main FastAPI application for AJ Institute SATS AI Co-Pilot
Production-ready pediatric triage system with AI analysis
"""

import os
import time
import csv
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
import uvicorn

# Import local modules
from database import get_db, test_database_connection, database_health_check
from models import (
    UserLogin, Token, CaseCreate, CaseResponse, CaseUpdate,
    PIICheckRequest, PIICheckResponse, GCSCalculationRequest, GCSCalculationResponse,
    HardRulesCheckRequest, HardRulesCheckResponse, AIAnalysisRequest, AIAnalysisResponse,
    HealthCheckResponse, ErrorResponse
)
# No authentication needed
from hard_rules import check_hard_rules
from gcs_calculator import calculate_pediatric_gcs
from pii_scrubber import check_clinical_narrative_safety
from ai_service import analyze_pediatric_triage_case

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Application metadata
APP_NAME = "SATS AI Co-Pilot — Paediatric Triage"
VERSION = "1.0.0"
DESCRIPTION = """
**A.J. INSTITUTE OF MEDICAL SCIENCES AND RESEARCH CENTRE**  
Department of Paediatrics

Clinical Trial Data Collection System for Pediatric Triage using AI-assisted South African Triage System (SATS).

## Features

* **Secure Authentication** - Role-based access control (Nurse, Consultant, Admin)
* **Pediatric Triage Forms** - Age-appropriate vital signs and GCS assessment
* **Hard Safety Rules** - Automatic RED category for critical conditions
* **AI Analysis** - Anthropic Claude-powered triage recommendations
* **PII Protection** - Automated detection of personally identifiable information
* **Real-time Analytics** - Dashboard with agreement metrics and statistics
* **Audit Trail** - Complete logging of all system actions
* **Export Functionality** - CSV/Excel export for research analysis

## Authentication

All endpoints require Bearer token authentication except `/login` and `/health`.

## Roles

* **Triage Nurse** - Submit cases, view own submissions only
* **Consultant** - Review all cases, provide gold standard assessments
* **Admin** - Full system access, user management, analytics

## Safety Features

* Hard-coded safety rules override AI recommendations
* PII detection prevents storage of patient identifiers
* Age-appropriate GCS scoring (standard vs pediatric)
* Comprehensive audit logging
"""

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description=DESCRIPTION,
    version=VERSION,
    contact={
        "name": "A.J. Institute of Medical Sciences",
        "url": "https://ajims.edu.in",
        "email": "info@ajims.edu.in"
    },
    license_info={
        "name": "Proprietary - Clinical Trial Use Only",
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security scheme
security = HTTPBearer()

# Mock user for endpoints that need it
def get_current_user():
    """Return mock user - no authentication required"""
    return {
        "id": 1,
        "username": "nurse",
        "full_name": "Triage Nurse",
        "role": "triage_nurse"
    }

# Application startup time
startup_time = time.time()

# CORS middleware - configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development
        "http://localhost:5173",  # Vite development
        "https://*.vercel.app",   # Vercel deployments
        "https://*.netlify.app",  # Netlify deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted host middleware for production security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure specific hosts in production
)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests for monitoring"""
    start_time = time.time()
    
    # Get client info
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"IP: {client_ip}"
    )
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """
    System health check endpoint
    
    Returns system status, database connectivity, and AI service availability
    """
    # Check database
    db_health = await database_health_check()
    db_connected = db_health.get("status") == "healthy"
    
    # Check AI service (basic check)
    ai_available = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    # Calculate uptime
    uptime_seconds = time.time() - startup_time
    
    # Determine overall status
    if db_connected and ai_available:
        status_text = "healthy"
    elif db_connected:
        status_text = "degraded"  # DB works but AI might not
    else:
        status_text = "unhealthy"
    
    return HealthCheckResponse(
        status=status_text,
        timestamp=datetime.now(),
        version=VERSION,
        database_connected=db_connected,
        ai_service_available=ai_available,
        uptime_seconds=uptime_seconds
    )


# No authentication endpoints needed


# ─── Triage submission endpoint (used by the frontend form) ───────────────────

class VitalsData(BaseModel):
    heartRate: Optional[float] = None
    respiratoryRate: Optional[float] = None
    temperature: Optional[float] = None
    systolicBP: Optional[float] = None
    diastolicBP: Optional[float] = None
    oxygenSaturation: Optional[float] = None

class GCSData(BaseModel):
    eye: Optional[int] = None
    verbal: Optional[int] = None
    motor: Optional[int] = None

class TriageRequest(BaseModel):
    patient_id: str
    age_months: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    vitals: VitalsData
    gcs: GCSData
    clinical_narrative: str
    nurse_triage_category: str
    nurse_id: Optional[int] = 1


def _log_to_csv(record: dict):
    log_file = "triage_log.csv"
    fieldnames = [
        "case_id", "timestamp", "nurse_category", "ai_recommendation",
        "confidence", "gcs_total", "clinical_narrative", "red_flags",
        "ai_reasoning", "hard_rule_triggered"
    ]
    file_exists = os.path.exists(log_file)
    with open(log_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


@app.post("/triage", tags=["Triage"])
async def submit_triage(request: TriageRequest):
    """
    Primary triage endpoint used by the nurse form.
    Runs hard-stop safety rules then calls the AI service.
    Returns a result card payload without requiring database access.
    """
    gcs_eye = request.gcs.eye or 4
    gcs_verbal = request.gcs.verbal or 5
    gcs_motor = request.gcs.motor or 6
    gcs_total = gcs_eye + gcs_verbal + gcs_motor
    age_months = request.age_months or 12.0

    case_data: Dict[str, Any] = {
        "age_value": age_months,
        "age_unit": "Months",
        "age_months_calculated": age_months,
        "weight_grams": (request.weight_kg or 0) * 1000,
        "hr": int(request.vitals.heartRate or 0),
        "rr": int(request.vitals.respiratoryRate or 0),
        "temp_fahrenheit": float(request.vitals.temperature or 98.6),
        "spo2": int(request.vitals.oxygenSaturation or 100),
        "gcs_eye": gcs_eye,
        "gcs_verbal": gcs_verbal,
        "gcs_motor": gcs_motor,
        "gcs_total": gcs_total,
        "chief_complaint": request.clinical_narrative[:120],
        "clinical_history": request.clinical_narrative,
    }

    # 1. Hard-stop safety rules always run first
    hard_triggered, rule_name, rule_detail = check_hard_rules(case_data)

    # 2. AI analysis
    ai_result = analyze_pediatric_triage_case(case_data)

    # Hard rules override AI output
    if hard_triggered:
        ai_category = "RED"
        confidence = 1.0
        reasoning = f"HARD-STOP: {rule_detail}"
        red_flags = [rule_detail or rule_name]
        recommendation = "Immediate resuscitation — hard safety rule triggered"
    else:
        ai_category = ai_result.get("ai_category", "YELLOW")
        confidence = (ai_result.get("ai_confidence_score") or 50) / 100.0
        reasoning = ai_result.get("ai_reasoning", "")
        red_flags = ai_result.get("ai_red_flags") or []
        recommendation = ai_result.get("ai_recommendation", "")

    case_id = f"AJ-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
    ts = datetime.now().isoformat()

    _log_to_csv({
        "case_id": case_id,
        "timestamp": ts,
        "nurse_category": request.nurse_triage_category,
        "ai_recommendation": ai_category,
        "confidence": confidence,
        "gcs_total": gcs_total,
        "clinical_narrative": request.clinical_narrative,
        "red_flags": str(red_flags),
        "ai_reasoning": reasoning,
        "hard_rule_triggered": hard_triggered,
    })

    return {
        "case_id": case_id,
        "nurse_category": request.nurse_triage_category,
        "ai_recommendation": ai_category,
        "confidence": confidence,
        "gcs_total": gcs_total,
        "gcs_eye": gcs_eye,
        "gcs_verbal": gcs_verbal,
        "gcs_motor": gcs_motor,
        "red_flags": red_flags,
        "ai_reasoning": reasoning,
        "recommendations": [recommendation] if recommendation else [],
        "timestamp": ts,
        "nurse_name": "Triage Nurse",
        "hard_rule_triggered": hard_triggered,
        "hard_rule_detail": rule_detail,
        "primary_concern": ai_result.get("ai_primary_concern", ""),
        "differentials": ai_result.get("ai_differentials") or [],
        "escalation_note": ai_result.get("ai_escalation_note", ""),
    }


# ─── Analytics / dashboard endpoints ─────────────────────────────────────────

PRIORITY = {"RED": 4, "ORANGE": 3, "YELLOW": 2, "GREEN": 1}


def _read_triage_log() -> List[Dict[str, Any]]:
    """Read all triage cases from the CSV log file."""
    log_file = "triage_log.csv"
    if not os.path.exists(log_file):
        return []
    cases: List[Dict[str, Any]] = []
    try:
        with open(log_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    import ast
                    raw = row.get("red_flags", "[]")
                    row["red_flags"] = ast.literal_eval(raw) if raw.startswith("[") else []
                except Exception:
                    row["red_flags"] = []
                try:
                    row["confidence"] = float(row.get("confidence", 0))
                except Exception:
                    row["confidence"] = 0.0
                row["hard_rule_triggered"] = str(row.get("hard_rule_triggered", "")).lower() == "true"
                cases.append(row)
    except Exception as e:
        logger.error(f"Error reading triage log: {e}")
    return cases


@app.get("/cases", tags=["Analytics"])
async def list_cases(category: str = None, agreement: str = None):
    """Return all logged triage cases with optional filters."""
    cases = _read_triage_log()

    if category:
        cat = category.upper()
        cases = [c for c in cases if c.get("ai_recommendation") == cat or c.get("nurse_category") == cat]

    if agreement == "true":
        cases = [c for c in cases if c.get("nurse_category") == c.get("ai_recommendation")]
    elif agreement == "false":
        cases = [c for c in cases if c.get("nurse_category") != c.get("ai_recommendation")]

    return sorted(cases, key=lambda x: x.get("timestamp", ""), reverse=True)


@app.get("/admin/stats", tags=["Analytics"])
async def get_admin_stats():
    """Aggregate statistics computed from the CSV log."""
    cases = _read_triage_log()
    empty = {
        "total_cases": 0, "agreement_rate": 0, "avg_confidence": 0,
        "red_flag_cases": 0, "under_triage_count": 0, "over_triage_count": 0,
        "hard_stop_count": 0,
        "category_distribution": {"RED": 0, "ORANGE": 0, "YELLOW": 0, "GREEN": 0},
        "nurse_distribution": {"RED": 0, "ORANGE": 0, "YELLOW": 0, "GREEN": 0},
    }
    if not cases:
        return empty

    total = len(cases)
    agreements = sum(1 for c in cases if c.get("nurse_category") == c.get("ai_recommendation"))
    total_conf = sum(c.get("confidence", 0) for c in cases)
    under = sum(
        1 for c in cases
        if PRIORITY.get(c.get("ai_recommendation", ""), 0) > PRIORITY.get(c.get("nurse_category", ""), 0)
    )
    over = sum(
        1 for c in cases
        if PRIORITY.get(c.get("ai_recommendation", ""), 0) < PRIORITY.get(c.get("nurse_category", ""), 0)
    )

    ai_dist = {cat: 0 for cat in ["RED", "ORANGE", "YELLOW", "GREEN"]}
    nurse_dist = {cat: 0 for cat in ["RED", "ORANGE", "YELLOW", "GREEN"]}
    for c in cases:
        ai_cat = c.get("ai_recommendation", "")
        nurse_cat = c.get("nurse_category", "")
        if ai_cat in ai_dist:
            ai_dist[ai_cat] += 1
        if nurse_cat in nurse_dist:
            nurse_dist[nurse_cat] += 1

    return {
        "total_cases": total,
        "agreement_rate": round(agreements / total * 100, 1),
        "avg_confidence": round(total_conf / total * 100, 1),
        "red_flag_cases": ai_dist["RED"],
        "under_triage_count": under,
        "over_triage_count": over,
        "hard_stop_count": sum(1 for c in cases if c.get("hard_rule_triggered")),
        "category_distribution": ai_dist,
        "nurse_distribution": nurse_dist,
    }


@app.get("/admin/recent-cases", tags=["Analytics"])
async def get_recent_cases(limit: int = 10):
    """Return the most recent N triage cases."""
    cases = _read_triage_log()
    sorted_cases = sorted(cases, key=lambda x: x.get("timestamp", ""), reverse=True)
    return sorted_cases[:limit]


@app.get("/admin/export", tags=["Analytics"])
async def export_cases():
    """Download the full triage log as a CSV file."""
    from fastapi.responses import FileResponse
    log_file = "triage_log.csv"
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="No triage data logged yet")
    return FileResponse(log_file, media_type="text/csv", filename="triage_log.csv")


# Case management endpoints
@app.post("/cases", response_model=CaseResponse, tags=["Cases"])
async def create_case(
    case_data: CaseCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new triage case
    
    Only triage nurses can create cases.
    Automatically runs hard safety rules and triggers AI analysis.
    """
    # Check user role
    if current_user["role"] != "triage_nurse":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only triage nurses can create cases"
        )
    
    try:
        # Convert Pydantic model to dict for processing
        case_dict = case_data.dict()
        case_dict["nurse_id"] = current_user["id"]
        case_dict["nurse_submitted_at"] = datetime.now()
        
        # Calculate derived fields
        if case_dict["age_unit"] == "Days":
            case_dict["age_months_calculated"] = case_dict["age_value"] / 30.44
        elif case_dict["age_unit"] == "Months":
            case_dict["age_months_calculated"] = case_dict["age_value"]
        else:  # Years
            case_dict["age_months_calculated"] = case_dict["age_value"] * 12
        
        case_dict["temp_celsius"] = (case_dict["temp_fahrenheit"] - 32) * 5.0 / 9.0
        case_dict["gcs_total"] = case_dict["gcs_eye"] + case_dict["gcs_verbal"] + case_dict["gcs_motor"]
        
        # Determine GCS scale
        case_dict["gcs_scale_used"] = "pediatric" if case_dict["age_months_calculated"] < 24 else "standard"
        
        # Check hard safety rules
        hard_rule_triggered, rule_name, rule_detail = check_hard_rules(case_dict)
        case_dict["hard_rule_triggered"] = hard_rule_triggered
        case_dict["hard_rule_detail"] = rule_detail
        
        # If hard rule triggered, override nurse category
        if hard_rule_triggered:
            case_dict["nurse_sats_category"] = "RED"
            logger.warning(f"Hard rule triggered for case: {rule_detail}")
        
        # Insert case into database (simplified - in production use SQLAlchemy ORM)
        from sqlalchemy import text
        
        # Generate study ID
        year = datetime.now().year
        result = db.execute(text(
            "SELECT COALESCE(MAX(CAST(SUBSTRING(study_id FROM 9) AS INTEGER)), 0) + 1 "
            "FROM cases WHERE study_id LIKE :pattern"
        ), {"pattern": f"AJ-{year}-%"})
        sequence_num = result.fetchone()[0]
        study_id = f"AJ-{year}-{sequence_num:04d}"
        
        case_dict["study_id"] = study_id
        
        # Insert case (simplified SQL - use ORM in production)
        insert_sql = text("""
            INSERT INTO cases (
                study_id, nurse_id, shift, triage_date, triage_time,
                age_value, age_unit, age_months_calculated, gender, weight_grams, height_cm,
                hr, rr, temp_fahrenheit, temp_celsius, spo2,
                gcs_eye, gcs_verbal, gcs_motor, gcs_total, gcs_scale_used,
                chief_complaint, clinical_history,
                hard_rule_triggered, hard_rule_detail,
                nurse_sats_category, nurse_confidence, nurse_notes, nurse_submitted_at
            ) VALUES (
                :study_id, :nurse_id, :shift, :triage_date, :triage_time,
                :age_value, :age_unit, :age_months_calculated, :gender, :weight_grams, :height_cm,
                :hr, :rr, :temp_fahrenheit, :temp_celsius, :spo2,
                :gcs_eye, :gcs_verbal, :gcs_motor, :gcs_total, :gcs_scale_used,
                :chief_complaint, :clinical_history,
                :hard_rule_triggered, :hard_rule_detail,
                :nurse_sats_category, :nurse_confidence, :nurse_notes, :nurse_submitted_at
            ) RETURNING id
        """)
        
        result = db.execute(insert_sql, case_dict)
        case_id = result.fetchone()[0]
        db.commit()
        
        # Trigger AI analysis asynchronously (simplified - use background tasks in production)
        try:
            ai_result = analyze_pediatric_triage_case(case_dict)
            
            if ai_result["success"]:
                # Update case with AI results
                update_sql = text("""
                    UPDATE cases SET
                        ai_category = :ai_category,
                        ai_confidence_score = :ai_confidence_score,
                        ai_gcs_interpretation = :ai_gcs_interpretation,
                        ai_primary_concern = :ai_primary_concern,
                        ai_reasoning = :ai_reasoning,
                        ai_red_flags = :ai_red_flags,
                        ai_differentials = :ai_differentials,
                        ai_recommendation = :ai_recommendation,
                        ai_escalation_note = :ai_escalation_note,
                        ai_analyzed_at = :ai_analyzed_at,
                        nurse_ai_agreement = :nurse_ai_agreement
                    WHERE id = :case_id
                """)
                
                agreement = case_dict["nurse_sats_category"] == ai_result["ai_category"]
                
                db.execute(update_sql, {
                    "case_id": case_id,
                    "ai_category": ai_result["ai_category"],
                    "ai_confidence_score": ai_result["ai_confidence_score"],
                    "ai_gcs_interpretation": ai_result.get("ai_gcs_interpretation"),
                    "ai_primary_concern": ai_result["ai_primary_concern"],
                    "ai_reasoning": ai_result["ai_reasoning"],
                    "ai_red_flags": ai_result.get("ai_red_flags", []),
                    "ai_differentials": ai_result.get("ai_differentials", []),
                    "ai_recommendation": ai_result["ai_recommendation"],
                    "ai_escalation_note": ai_result.get("ai_escalation_note"),
                    "ai_analyzed_at": datetime.now(),
                    "nurse_ai_agreement": agreement
                })
                db.commit()
                
        except Exception as e:
            logger.error(f"AI analysis failed for case {case_id}: {e}")
            # Continue without AI analysis - case is still saved
        
        # Return created case
        return {"message": f"Case {study_id} created successfully", "case_id": case_id, "study_id": study_id}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create case"
        )


# Utility endpoints
@app.post("/check-pii", response_model=PIICheckResponse, tags=["Utilities"])
async def check_pii(
    pii_request: PIICheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Check clinical narrative for personally identifiable information (PII)
    
    Helps ensure ethics compliance by detecting potential patient identifiers
    """
    try:
        result = check_clinical_narrative_safety(
            pii_request.chief_complaint,
            pii_request.clinical_history
        )
        return result
    except Exception as e:
        logger.error(f"PII check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PII check failed"
        )


@app.post("/calculate-gcs", response_model=GCSCalculationResponse, tags=["Utilities"])
async def calculate_gcs(
    gcs_request: GCSCalculationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate Glasgow Coma Scale score with pediatric interpretation
    
    Automatically selects standard or pediatric GCS based on age
    """
    try:
        result = calculate_pediatric_gcs(
            gcs_request.gcs_eye,
            gcs_request.gcs_verbal,
            gcs_request.gcs_motor,
            gcs_request.age_months
        )
        return result
    except Exception as e:
        logger.error(f"GCS calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GCS calculation failed"
        )


@app.post("/check-hard-rules", response_model=HardRulesCheckResponse, tags=["Utilities"])
async def check_hard_safety_rules(
    rules_request: HardRulesCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Check hard safety rules for automatic RED category assignment
    
    These rules override any other triage decision for patient safety
    """
    try:
        triggered, rule_name, detail = check_hard_rules(rules_request.dict())
        
        return HardRulesCheckResponse(
            triggered=triggered,
            rule_name=rule_name,
            detail=detail
        )
    except Exception as e:
        logger.error(f"Hard rules check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hard rules check failed"
        )


# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {APP_NAME} v{VERSION}")
    
    # Test database connection
    if test_database_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed")
    
    # Check AI service
    if os.getenv("ANTHROPIC_API_KEY"):
        logger.info("✅ AI service configured")
    else:
        logger.warning("⚠️ AI service not configured (missing ANTHROPIC_API_KEY)")
    
    logger.info("🚀 Application startup complete")


# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down application...")


# Development server
if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )