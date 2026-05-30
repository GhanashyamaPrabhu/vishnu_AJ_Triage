"""
Pydantic Models for AJ Institute SATS AI Co-Pilot
Data validation and serialization models for the FastAPI backend
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum


class UserRole(str, Enum):
    TRIAGE_NURSE = "triage_nurse"
    CONSULTANT = "consultant"
    ADMIN = "admin"


class TriageCategory(str, Enum):
    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class AgeUnit(str, Enum):
    DAYS = "Days"
    MONTHS = "Months"
    YEARS = "Years"


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"


class Shift(str, Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    NIGHT = "Night"


class PatientCategory(str, Enum):
    NEONATE = "Neonate"
    INFANT = "Infant"
    TODDLER = "Toddler"
    CHILD = "Child"
    ADOLESCENT = "Adolescent"


# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole
    department: str = Field(default="Department of Paediatrics", max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    department: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]  # Use dict instead of UserResponse for simple auth


# Case Models
class CaseBase(BaseModel):
    shift: Shift
    triage_date: date
    triage_time: time
    
    # Patient demographics
    age_value: float = Field(..., gt=0, description="Age value (must be positive)")
    age_unit: AgeUnit
    gender: Gender
    weight_grams: float = Field(..., gt=0, description="Weight in grams")
    height_cm: Optional[float] = Field(None, gt=0, description="Height in centimeters")
    patient_category: Optional[PatientCategory] = None
    
    # Vital signs
    hr: int = Field(..., ge=30, le=300, description="Heart rate (30-300 bpm)")
    rr: int = Field(..., ge=5, le=100, description="Respiratory rate (5-100 breaths/min)")
    temp_fahrenheit: float = Field(..., ge=90.0, le=115.0, description="Temperature in Fahrenheit")
    spo2: int = Field(..., ge=50, le=100, description="SpO2 percentage (50-100%)")
    
    # Glasgow Coma Scale
    gcs_eye: int = Field(..., ge=1, le=4, description="GCS Eye opening (1-4)")
    gcs_verbal: int = Field(..., ge=1, le=5, description="GCS Verbal response (1-5)")
    gcs_motor: int = Field(..., ge=1, le=6, description="GCS Motor response (1-6)")
    
    # Clinical narrative
    chief_complaint: str = Field(..., min_length=5, max_length=200, description="Chief complaint")
    clinical_history: str = Field(..., min_length=20, max_length=2000, description="Clinical history")
    
    # Nurse triage decision
    nurse_sats_category: TriageCategory
    nurse_confidence: int = Field(..., ge=1, le=10, description="Nurse confidence (1-10)")
    nurse_notes: Optional[str] = Field(None, max_length=500)

    @validator('age_value')
    def validate_age_value(cls, v, values):
        """Validate age value based on unit"""
        if 'age_unit' in values:
            unit = values['age_unit']
            if unit == AgeUnit.DAYS and (v < 0 or v > 365):
                raise ValueError('Age in days must be 0-365')
            elif unit == AgeUnit.MONTHS and (v < 0 or v > 216):  # 18 years
                raise ValueError('Age in months must be 0-216')
            elif unit == AgeUnit.YEARS and (v < 0 or v > 18):
                raise ValueError('Age in years must be 0-18')
        return v

    @validator('weight_grams')
    def validate_weight(cls, v):
        """Validate weight is reasonable for pediatric patients"""
        if v < 500 or v > 150000:  # 500g to 150kg
            raise ValueError('Weight must be between 500g and 150kg')
        return v


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    # Only allow updating consultant review fields
    gold_standard_category: Optional[TriageCategory] = None
    consultant_notes: Optional[str] = Field(None, max_length=1000)


class CaseResponse(CaseBase):
    id: int
    study_id: str
    created_at: datetime
    nurse_id: int
    
    # Auto-calculated fields
    age_months_calculated: float
    temp_celsius: float
    gcs_total: int
    gcs_scale_used: str
    gcs_interpretation: Optional[str] = None
    
    # Hard rules
    hard_rule_triggered: bool
    hard_rule_detail: Optional[str] = None
    
    # Nurse submission
    nurse_submitted_at: datetime
    
    # AI analysis results
    ai_category: Optional[TriageCategory] = None
    ai_confidence_score: Optional[int] = None
    ai_gcs_interpretation: Optional[str] = None
    ai_primary_concern: Optional[str] = None
    ai_reasoning: Optional[str] = None
    ai_red_flags: Optional[List[str]] = None
    ai_differentials: Optional[List[str]] = None
    ai_recommendation: Optional[str] = None
    ai_escalation_note: Optional[str] = None
    ai_analyzed_at: Optional[datetime] = None
    
    # Gold standard (consultant review)
    consultant_id: Optional[int] = None
    gold_standard_category: Optional[TriageCategory] = None
    consultant_notes: Optional[str] = None
    gold_standard_at: Optional[datetime] = None
    
    # Analysis flags
    nurse_ai_agreement: Optional[bool] = None
    discrepancy_type: Optional[str] = None
    
    # Audit
    updated_at: datetime
    
    class Config:
        from_attributes = True


# AI Analysis Models
class AIAnalysisRequest(BaseModel):
    case_id: int


class AIAnalysisResponse(BaseModel):
    success: bool
    ai_category: Optional[str] = None
    ai_confidence_score: Optional[int] = None
    ai_gcs_interpretation: Optional[str] = None
    ai_primary_concern: Optional[str] = None
    ai_reasoning: Optional[str] = None
    ai_red_flags: Optional[List[str]] = None
    ai_differentials: Optional[List[str]] = None
    ai_recommendation: Optional[str] = None
    ai_escalation_note: Optional[str] = None
    ai_analyzed_at: Optional[datetime] = None
    error: Optional[str] = None


# PII Scrubber Models
class PIICheckRequest(BaseModel):
    chief_complaint: str
    clinical_history: str


class PIIFlaggedPattern(BaseModel):
    pattern: str
    matched_text: str
    start_pos: int
    end_pos: int
    description: str
    risk: str


class PIIScanResult(BaseModel):
    pii_found: bool
    risk_level: str
    flagged_patterns: List[PIIFlaggedPattern]
    cleaned_text: str


class PIICheckResponse(BaseModel):
    chief_complaint_scan: PIIScanResult
    clinical_history_scan: PIIScanResult
    overall_assessment: Dict[str, Any]
    recommendations: List[str]


# GCS Calculator Models
class GCSCalculationRequest(BaseModel):
    gcs_eye: int = Field(..., ge=1, le=4)
    gcs_verbal: int = Field(..., ge=1, le=5)
    gcs_motor: int = Field(..., ge=1, le=6)
    age_months: float = Field(..., gt=0)


class GCSCalculationResponse(BaseModel):
    gcs_eye: int
    gcs_verbal: int
    gcs_motor: int
    gcs_total: int
    gcs_scale_used: str
    gcs_interpretation: str
    gcs_description: str
    clinical_significance: str
    minimum_triage_category: Optional[str] = None
    normal_ranges: Dict[str, Any]


# Hard Rules Models
class HardRulesCheckRequest(BaseModel):
    spo2: int
    gcs_total: int
    gcs_motor: int
    gcs_eye: int
    hr: int
    rr: int
    temp_fahrenheit: float
    age_months_calculated: float
    chief_complaint: Optional[str] = ""
    clinical_history: Optional[str] = ""


class HardRulesCheckResponse(BaseModel):
    triggered: bool
    rule_name: Optional[str] = None
    detail: Optional[str] = None


# Analytics Models
class CaseStatistics(BaseModel):
    date: date
    total_cases: int
    nurse_red: int
    nurse_orange: int
    nurse_yellow: int
    nurse_green: int
    ai_red: int
    ai_orange: int
    ai_yellow: int
    ai_green: int
    agreement_percentage: float
    under_triage_cases: int
    over_triage_cases: int


class ShiftStatistics(BaseModel):
    shift: str
    total_cases: int
    agreement_percentage: float
    avg_nurse_confidence: float
    avg_ai_confidence: float


class DashboardStats(BaseModel):
    total_cases: int
    cases_today: int
    agreement_percentage: float
    cases_needing_gold_standard: int
    recent_cases: List[CaseResponse]
    case_statistics: List[CaseStatistics]
    shift_statistics: List[ShiftStatistics]


# Export Models
class ExportRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    format: str = Field(default="csv", pattern="^(csv|xlsx)$")


class ExportResponse(BaseModel):
    success: bool
    filename: str
    download_url: str
    total_records: int
    error: Optional[str] = None


# Audit Log Models
class AuditLogEntry(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Error Response Models
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ValidationErrorResponse(BaseModel):
    detail: str
    errors: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.now)


# Health Check Model
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    ai_service_available: bool
    uptime_seconds: float


# Pagination Models
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


# Search and Filter Models
class CaseFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    nurse_category: Optional[TriageCategory] = None
    ai_category: Optional[TriageCategory] = None
    agreement: Optional[bool] = None
    shift: Optional[Shift] = None
    nurse_id: Optional[int] = None
    consultant_id: Optional[int] = None
    has_gold_standard: Optional[bool] = None


class CaseSearchRequest(BaseModel):
    filters: Optional[CaseFilters] = None
    search_query: Optional[str] = None  # Search in chief complaint or clinical history
    pagination: PaginationParams = PaginationParams()
    sort_by: str = Field(default="created_at", pattern="^(created_at|study_id|nurse_category|ai_category|agreement)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# Configuration Models
class AppConfig(BaseModel):
    app_name: str = "SATS AI Co-Pilot — Paediatric Triage"
    version: str = "1.0"
    institution: str = "A.J. INSTITUTE OF MEDICAL SCIENCES AND RESEARCH CENTRE"
    department: str = "Department of Paediatrics"
    tagline: str = "Clinical Trial Data Collection System — v1.0"
    max_cases_per_hour: int = 100
    session_timeout_hours: int = 12
    enable_pii_checking: bool = True
    enable_hard_rules: bool = True
    enable_ai_analysis: bool = True