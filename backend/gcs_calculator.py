"""
Glasgow Coma Scale Calculator for AJ Institute SATS AI Co-Pilot
Handles both standard and pediatric GCS scoring with age-appropriate interpretations
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class GCSScale(Enum):
    STANDARD = "standard"
    PEDIATRIC = "pediatric"


class GCSInterpretation(Enum):
    NORMAL = "Normal"
    MINOR = "Minor"
    MODERATE = "Moderate"
    SEVERE = "Severe"
    CRITICAL = "Critical"


@dataclass
class GCSResult:
    """Result of GCS calculation and interpretation"""
    eye: int
    verbal: int
    motor: int
    total: int
    scale_used: GCSScale
    interpretation: GCSInterpretation
    description: str
    clinical_significance: str


class GCSCalculator:
    """
    Glasgow Coma Scale calculator with pediatric modifications
    Automatically selects appropriate scale based on age
    """
    
    # Standard GCS descriptions (age ≥ 24 months)
    STANDARD_EYE = {
        4: "Spontaneous",
        3: "To Voice", 
        2: "To Pain",
        1: "None"
    }
    
    STANDARD_VERBAL = {
        5: "Oriented",
        4: "Confused",
        3: "Inappropriate Words",
        2: "Incomprehensible Sounds",
        1: "None"
    }
    
    # Pediatric GCS verbal responses (age < 24 months)
    PEDIATRIC_VERBAL = {
        5: "Coos/Babbles normally",
        4: "Irritable/Crying",
        3: "Cries to pain only",
        2: "Moans to pain",
        1: "None"
    }
    
    # Motor responses (same for both scales)
    MOTOR_RESPONSES = {
        6: "Obeys Commands",
        5: "Localizes Pain",
        4: "Withdraws from Pain",
        3: "Abnormal Flexion (Decorticate)",
        2: "Extension (Decerebrate)",
        1: "None"
    }
    
    @staticmethod
    def calculate_gcs(eye: int, verbal: int, motor: int, age_months: float) -> GCSResult:
        """
        Calculate GCS score and provide clinical interpretation
        
        Args:
            eye: Eye opening response (1-4)
            verbal: Verbal response (1-5)
            motor: Motor response (1-6)
            age_months: Patient age in months
            
        Returns:
            GCSResult with score, interpretation, and clinical significance
        """
        
        # Validate inputs
        if not (1 <= eye <= 4):
            raise ValueError(f"Eye score must be 1-4, got {eye}")
        if not (1 <= verbal <= 5):
            raise ValueError(f"Verbal score must be 1-5, got {verbal}")
        if not (1 <= motor <= 6):
            raise ValueError(f"Motor score must be 1-6, got {motor}")
        
        # Calculate total
        total = eye + verbal + motor
        
        # Determine scale based on age
        scale_used = GCSScale.PEDIATRIC if age_months < 24 else GCSScale.STANDARD
        
        # Get interpretation
        interpretation = GCSCalculator._interpret_total_score(total)
        
        # Generate description
        description = GCSCalculator._generate_description(
            eye, verbal, motor, scale_used
        )
        
        # Get clinical significance
        clinical_significance = GCSCalculator._get_clinical_significance(
            total, interpretation, age_months
        )
        
        return GCSResult(
            eye=eye,
            verbal=verbal,
            motor=motor,
            total=total,
            scale_used=scale_used,
            interpretation=interpretation,
            description=description,
            clinical_significance=clinical_significance
        )
    
    @staticmethod
    def _interpret_total_score(total: int) -> GCSInterpretation:
        """Interpret GCS total score"""
        if total == 15:
            return GCSInterpretation.NORMAL
        elif total >= 13:
            return GCSInterpretation.MINOR
        elif total >= 9:
            return GCSInterpretation.MODERATE
        elif total > 3:
            return GCSInterpretation.SEVERE
        else:  # total == 3
            return GCSInterpretation.CRITICAL
    
    @staticmethod
    def _generate_description(eye: int, verbal: int, motor: int, scale: GCSScale) -> str:
        """Generate human-readable GCS description"""
        
        eye_desc = GCSCalculator.STANDARD_EYE[eye]
        motor_desc = GCSCalculator.MOTOR_RESPONSES[motor]
        
        if scale == GCSScale.PEDIATRIC:
            verbal_desc = GCSCalculator.PEDIATRIC_VERBAL[verbal]
            scale_note = " (Pediatric GCS)"
        else:
            verbal_desc = GCSCalculator.STANDARD_VERBAL[verbal]
            scale_note = ""
        
        return f"E{eye} ({eye_desc}) + V{verbal} ({verbal_desc}) + M{motor} ({motor_desc}){scale_note}"
    
    @staticmethod
    def _get_clinical_significance(total: int, interpretation: GCSInterpretation, age_months: float) -> str:
        """Get clinical significance and triage implications"""
        
        age_context = ""
        if age_months < 24:
            age_context = " In infants, even minor GCS changes are significant."
        
        if interpretation == GCSInterpretation.NORMAL:
            return f"Normal consciousness level.{age_context}"
        
        elif interpretation == GCSInterpretation.MINOR:
            return f"Mild alteration in consciousness. Monitor closely for deterioration.{age_context}"
        
        elif interpretation == GCSInterpretation.MODERATE:
            return f"Moderate brain injury. Requires urgent medical attention and frequent neurological assessment. Minimum ORANGE triage category.{age_context}"
        
        elif interpretation == GCSInterpretation.SEVERE:
            return f"Severe brain injury. Immediate medical intervention required. Automatic RED triage category. Consider airway protection.{age_context}"
        
        else:  # CRITICAL
            return f"Critical brain injury. Immediate resuscitation required. Automatic RED triage category. Secure airway immediately.{age_context}"
    
    @staticmethod
    def get_triage_category_from_gcs(total: int) -> str:
        """Get minimum triage category based on GCS score"""
        if total <= 8:
            return "RED"  # Severe/Critical
        elif total <= 12:
            return "ORANGE"  # Moderate - requires urgent attention
        elif total <= 14:
            return "YELLOW"  # Minor - but still concerning
        else:
            return None  # Normal - no GCS-based triage escalation needed
    
    @staticmethod
    def get_normal_ranges_by_age(age_months: float) -> Dict[str, Any]:
        """Get age-appropriate GCS expectations and normal ranges"""
        
        if age_months < 1:  # Neonate
            return {
                "expected_total": "13-15",
                "notes": "Neonates may have lower verbal scores normally. Any GCS <13 is concerning.",
                "red_flags": ["No eye opening", "No response to voice", "Abnormal posturing"]
            }
        elif age_months < 6:  # Young infant
            return {
                "expected_total": "14-15", 
                "notes": "Young infants should respond to voice and localize pain. Verbal assessment uses crying/cooing.",
                "red_flags": ["No social interaction", "Weak cry", "Poor feeding with altered GCS"]
            }
        elif age_months < 24:  # Older infant/toddler
            return {
                "expected_total": "15",
                "notes": "Should have normal eye opening, appropriate crying, and purposeful movement.",
                "red_flags": ["Not recognizing parents", "Excessive irritability", "Lethargy"]
            }
        else:  # Child/adolescent
            return {
                "expected_total": "15",
                "notes": "Should be fully oriented and following commands appropriately for age.",
                "red_flags": ["Confusion", "Inappropriate responses", "Not following simple commands"]
            }


def calculate_pediatric_gcs(eye: int, verbal: int, motor: int, age_months: float) -> Dict[str, Any]:
    """
    Convenience function for calculating pediatric GCS
    Returns dictionary format suitable for API responses
    """
    
    try:
        result = GCSCalculator.calculate_gcs(eye, verbal, motor, age_months)
        
        return {
            "gcs_eye": result.eye,
            "gcs_verbal": result.verbal,
            "gcs_motor": result.motor,
            "gcs_total": result.total,
            "gcs_scale_used": result.scale_used.value,
            "gcs_interpretation": result.interpretation.value,
            "gcs_description": result.description,
            "clinical_significance": result.clinical_significance,
            "minimum_triage_category": GCSCalculator.get_triage_category_from_gcs(result.total),
            "normal_ranges": GCSCalculator.get_normal_ranges_by_age(age_months)
        }
        
    except ValueError as e:
        return {
            "error": str(e),
            "gcs_total": None,
            "gcs_interpretation": None
        }


# Example usage and testing
if __name__ == "__main__":
    # Test cases for different age groups and GCS scores
    
    test_cases = [
        {
            "name": "Normal 5-year-old",
            "eye": 4, "verbal": 5, "motor": 6,
            "age_months": 60
        },
        {
            "name": "Confused 8-year-old (moderate head injury)",
            "eye": 3, "verbal": 4, "motor": 5,
            "age_months": 96
        },
        {
            "name": "Severe head injury (10-year-old)",
            "eye": 2, "verbal": 2, "motor": 4,
            "age_months": 120
        },
        {
            "name": "Normal 6-month infant",
            "eye": 4, "verbal": 5, "motor": 6,
            "age_months": 6
        },
        {
            "name": "Sick 3-month infant",
            "eye": 3, "verbal": 3, "motor": 5,
            "age_months": 3
        },
        {
            "name": "Critical case (any age)",
            "eye": 1, "verbal": 1, "motor": 1,
            "age_months": 24
        }
    ]
    
    print("Testing GCS Calculator:")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Age: {test['age_months']} months")
        print(f"GCS: E{test['eye']} V{test['verbal']} M{test['motor']}")
        
        result = calculate_pediatric_gcs(
            test['eye'], test['verbal'], test['motor'], test['age_months']
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Total: {result['gcs_total']}/15")
            print(f"Scale: {result['gcs_scale_used']}")
            print(f"Interpretation: {result['gcs_interpretation']}")
            print(f"Description: {result['gcs_description']}")
            print(f"Clinical: {result['clinical_significance']}")
            
            if result['minimum_triage_category']:
                print(f"🔴 Minimum Triage: {result['minimum_triage_category']}")
        
        print("-" * 40)