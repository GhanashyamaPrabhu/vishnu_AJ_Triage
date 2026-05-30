"""
Hard Safety Rules for AJ Institute SATS AI Co-Pilot
Critical safety checks that run BEFORE AI analysis
If any rule triggers, automatically assign RED category
"""

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class HardRuleResult:
    """Result of hard rule evaluation"""
    triggered: bool
    rule_name: str
    detail: str
    category: str = "RED"


class HardSafetyRules:
    """
    Hard-coded safety rules that override any AI analysis
    These are non-negotiable clinical safety thresholds
    """
    
    @staticmethod
    def evaluate_all_rules(case_data: Dict[str, Any]) -> Optional[HardRuleResult]:
        """
        Evaluate all hard safety rules in order of criticality
        Returns the first triggered rule, or None if no rules triggered
        
        Args:
            case_data: Dictionary containing patient vitals and demographics
            
        Returns:
            HardRuleResult if any rule triggered, None otherwise
        """
        
        # Extract vital signs
        spo2 = case_data.get('spo2', 100)
        gcs_total = case_data.get('gcs_total', 15)
        gcs_motor = case_data.get('gcs_motor', 6)
        gcs_eye = case_data.get('gcs_eye', 4)
        hr = case_data.get('hr', 100)
        rr = case_data.get('rr', 20)
        temp_f = case_data.get('temp_fahrenheit', 98.6)
        age_months = case_data.get('age_months_calculated', 12)
        
        # Rule 1: Critical SpO2
        if spo2 < 90:
            return HardRuleResult(
                triggered=True,
                rule_name="CRITICAL_SPO2",
                detail=f"SpO2 = {spo2}% (threshold <90%) → Automatic RED"
            )
        
        # Rule 2: Severe neurological impairment (GCS ≤ 8)
        if gcs_total <= 8:
            return HardRuleResult(
                triggered=True,
                rule_name="SEVERE_GCS",
                detail=f"GCS Total = {gcs_total} (threshold ≤8) → Automatic RED"
            )
        
        # Rule 3: No motor response or decerebrate/decorticate posturing
        if gcs_motor <= 2:
            motor_description = {
                1: "No Motor Response",
                2: "Extension (Decerebrate)"
            }.get(gcs_motor, "Abnormal Motor")
            
            return HardRuleResult(
                triggered=True,
                rule_name="CRITICAL_MOTOR",
                detail=f"GCS Motor = {gcs_motor} ({motor_description}) → Automatic RED"
            )
        
        # Rule 4: No eye opening
        if gcs_eye == 1:
            return HardRuleResult(
                triggered=True,
                rule_name="NO_EYE_OPENING",
                detail=f"GCS Eye = 1 (No Eye Opening) → Automatic RED"
            )
        
        # Rule 5: Critical heart rate (age-adjusted)
        hr_critical = HardSafetyRules._check_critical_heart_rate(hr, age_months)
        if hr_critical:
            return HardRuleResult(
                triggered=True,
                rule_name="CRITICAL_HEART_RATE",
                detail=f"HR = {hr} bpm {hr_critical} → Automatic RED"
            )
        
        # Rule 6: Critical respiratory rate (age-adjusted)
        rr_critical = HardSafetyRules._check_critical_respiratory_rate(rr, age_months)
        if rr_critical:
            return HardRuleResult(
                triggered=True,
                rule_name="CRITICAL_RESPIRATORY_RATE",
                detail=f"RR = {rr} breaths/min {rr_critical} → Automatic RED"
            )
        
        # Rule 7: Hyperpyrexia (extreme fever)
        if temp_f > 105.8:
            return HardRuleResult(
                triggered=True,
                rule_name="HYPERPYREXIA",
                detail=f"Temperature = {temp_f}°F (threshold >105.8°F) → Automatic RED"
            )
        
        # Rule 8: Sick neonate (any abnormal vital in <28 days old)
        if age_months < 1:  # Less than 1 month (neonate)
            neonate_issue = HardSafetyRules._check_sick_neonate(case_data)
            if neonate_issue:
                return HardRuleResult(
                    triggered=True,
                    rule_name="SICK_NEONATE",
                    detail=f"Neonate (<28 days) with {neonate_issue} → Automatic RED"
                )
        
        # No hard rules triggered
        return None
    
    @staticmethod
    def _check_critical_heart_rate(hr: int, age_months: float) -> Optional[str]:
        """Check for critically abnormal heart rate based on age"""
        
        # Age-specific heart rate thresholds (bradycardia/tachycardia)
        if age_months < 1:  # Neonate (0-28 days)
            if hr < 80 or hr > 180:
                return f"(normal 80-180 for neonate)"
        elif age_months < 12:  # Infant (1-12 months)
            if hr < 80 or hr > 160:
                return f"(normal 80-160 for infant)"
        elif age_months < 24:  # Toddler (1-2 years)
            if hr < 70 or hr > 150:
                return f"(normal 70-150 for toddler)"
        elif age_months < 60:  # Child (2-5 years)
            if hr < 65 or hr > 140:
                return f"(normal 65-140 for child)"
        elif age_months < 144:  # Child (5-12 years)
            if hr < 60 or hr > 120:
                return f"(normal 60-120 for child)"
        else:  # Adolescent (12+ years)
            if hr < 55 or hr > 110:
                return f"(normal 55-110 for adolescent)"
        
        return None
    
    @staticmethod
    def _check_critical_respiratory_rate(rr: int, age_months: float) -> Optional[str]:
        """Check for critically abnormal respiratory rate based on age"""
        
        # Age-specific respiratory rate thresholds
        if age_months < 1:  # Neonate (0-28 days)
            if rr < 20 or rr > 60:
                return f"(normal 20-60 for neonate)"
        elif age_months < 12:  # Infant (1-12 months)
            if rr < 20 or rr > 50:
                return f"(normal 20-50 for infant)"
        elif age_months < 24:  # Toddler (1-2 years)
            if rr < 15 or rr > 40:
                return f"(normal 15-40 for toddler)"
        elif age_months < 60:  # Child (2-5 years)
            if rr < 15 or rr > 35:
                return f"(normal 15-35 for child)"
        elif age_months < 144:  # Child (5-12 years)
            if rr < 12 or rr > 30:
                return f"(normal 12-30 for child)"
        else:  # Adolescent (12+ years)
            if rr < 10 or rr > 25:
                return f"(normal 10-25 for adolescent)"
        
        return None
    
    @staticmethod
    def _check_sick_neonate(case_data: Dict[str, Any]) -> Optional[str]:
        """
        Check for any concerning signs in neonates (<28 days)
        Neonates can deteriorate rapidly and need aggressive triage
        """
        
        # Extract vitals
        temp_f = case_data.get('temp_fahrenheit', 98.6)
        hr = case_data.get('hr', 120)
        rr = case_data.get('rr', 40)
        spo2 = case_data.get('spo2', 100)
        gcs_total = case_data.get('gcs_total', 15)
        
        # Check for any abnormal vital signs in neonate
        issues = []
        
        # Temperature instability (hypothermia or fever in neonate)
        if temp_f < 97.0:
            issues.append(f"hypothermia ({temp_f}°F)")
        elif temp_f > 100.4:
            issues.append(f"fever ({temp_f}°F)")
        
        # Borderline vitals that are concerning in neonates
        if hr < 100 or hr > 160:
            issues.append(f"abnormal HR ({hr})")
        
        if rr < 30 or rr > 50:
            issues.append(f"abnormal RR ({rr})")
        
        if spo2 < 95:
            issues.append(f"low SpO2 ({spo2}%)")
        
        if gcs_total < 15:
            issues.append(f"altered consciousness (GCS {gcs_total})")
        
        # Check clinical narrative for concerning phrases
        chief_complaint = case_data.get('chief_complaint', '').lower()
        clinical_history = case_data.get('clinical_history', '').lower()
        narrative = f"{chief_complaint} {clinical_history}"
        
        # Red flag phrases for neonates
        neonate_red_flags = [
            'not feeding', 'poor feeding', 'refusing feeds',
            'lethargic', 'floppy', 'weak cry', 'high pitched cry',
            'cold to touch', 'mottled', 'pale', 'cyanotic',
            'grunting', 'retractions', 'apnea',
            'seizure', 'jittery', 'irritable'
        ]
        
        for flag in neonate_red_flags:
            if flag in narrative:
                issues.append(f"red flag: '{flag}'")
        
        if issues:
            return ", ".join(issues[:3])  # Limit to first 3 issues for brevity
        
        return None


def check_hard_rules(case_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convenience function to check all hard rules
    
    Args:
        case_data: Dictionary containing patient data
        
    Returns:
        Tuple of (triggered: bool, rule_name: str, detail: str)
    """
    
    result = HardSafetyRules.evaluate_all_rules(case_data)
    
    if result:
        return True, result.rule_name, result.detail
    else:
        return False, None, None


# Example usage and testing
if __name__ == "__main__":
    # Test cases for hard rules
    
    test_cases = [
        {
            "name": "Critical SpO2",
            "data": {
                "spo2": 85,
                "gcs_total": 15,
                "hr": 100,
                "rr": 20,
                "temp_fahrenheit": 98.6,
                "age_months_calculated": 24
            }
        },
        {
            "name": "Severe GCS",
            "data": {
                "spo2": 98,
                "gcs_total": 6,
                "gcs_motor": 3,
                "gcs_eye": 2,
                "hr": 100,
                "rr": 20,
                "temp_fahrenheit": 98.6,
                "age_months_calculated": 24
            }
        },
        {
            "name": "Sick Neonate",
            "data": {
                "spo2": 94,
                "gcs_total": 14,
                "hr": 90,
                "rr": 25,
                "temp_fahrenheit": 101.2,
                "age_months_calculated": 0.5,
                "chief_complaint": "poor feeding",
                "clinical_history": "3 week old baby, not feeding well, lethargic"
            }
        },
        {
            "name": "Normal Case",
            "data": {
                "spo2": 98,
                "gcs_total": 15,
                "gcs_motor": 6,
                "gcs_eye": 4,
                "hr": 110,
                "rr": 24,
                "temp_fahrenheit": 99.1,
                "age_months_calculated": 24
            }
        }
    ]
    
    print("Testing Hard Safety Rules:")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        triggered, rule_name, detail = check_hard_rules(test['data'])
        
        if triggered:
            print(f"🔴 HARD RULE TRIGGERED: {rule_name}")
            print(f"   Detail: {detail}")
        else:
            print("✅ No hard rules triggered")