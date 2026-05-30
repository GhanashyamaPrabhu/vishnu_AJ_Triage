"""
PII Scrubber for AJ Institute SATS AI Co-Pilot
Detects and flags potential personally identifiable information in clinical narratives
Ensures ethics compliance by preventing storage of patient identifiers
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class PIIDetection:
    """Result of PII detection scan"""
    text: str
    pii_found: bool
    flagged_patterns: List[Dict[str, Any]]
    cleaned_text: str
    risk_level: str  # LOW, MEDIUM, HIGH


class PIIScrubber:
    """
    Detects potential PII in clinical narratives
    Designed for Indian healthcare context
    """
    
    # Common Indian names (sample - not exhaustive)
    INDIAN_NAMES = [
        'aarav', 'vivaan', 'aditya', 'vihaan', 'arjun', 'sai', 'reyansh', 'ayaan', 'krishna', 'ishaan',
        'saanvi', 'aadya', 'kiara', 'diya', 'pihu', 'prisha', 'ananya', 'fatima', 'aadhya', 'kavya',
        'ravi', 'raj', 'kumar', 'sharma', 'singh', 'patel', 'gupta', 'jain', 'agarwal', 'mehta',
        'priya', 'pooja', 'neha', 'kavita', 'sunita', 'geeta', 'rita', 'sita', 'meera', 'radha'
    ]
    
    # PII detection patterns
    PATTERNS = {
        'phone_number': {
            'regex': r'\b(?:\+91[-.\s]?)?[6-9]\d{9}\b',
            'description': 'Indian phone number',
            'risk': 'HIGH'
        },
        'hospital_number': {
            'regex': r'\b(?:IP|OP|MRD?|REG|UHID)[-.\s]?\d{4,}\b',
            'description': 'Hospital/Medical record number',
            'risk': 'HIGH'
        },
        'date_of_birth': {
            'regex': r'\b(?:DOB|born|birth)[-:\s]*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
            'description': 'Date of birth',
            'risk': 'HIGH'
        },
        'full_date': {
            'regex': r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
            'description': 'Specific date',
            'risk': 'MEDIUM'
        },
        'address_keywords': {
            'regex': r'\b(?:address|street|road|lane|colony|nagar|puram|ganj|chowk|circle)\b',
            'description': 'Address-related terms',
            'risk': 'MEDIUM'
        },
        'email': {
            'regex': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'description': 'Email address',
            'risk': 'HIGH'
        },
        'aadhar_like': {
            'regex': r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
            'description': 'Aadhar-like number pattern',
            'risk': 'HIGH'
        },
        'father_mother_name': {
            'regex': r'\b(?:father|mother|parent|guardian)[-:\s]*(?:name[-:\s]*)?[A-Za-z]{3,}\b',
            'description': 'Parent/guardian name reference',
            'risk': 'HIGH'
        },
        'specific_location': {
            'regex': r'\b(?:mangalore|udupi|karnataka|kerala|mumbai|bangalore|delhi|chennai|hyderabad|pune|ahmedabad|kolkata)\b',
            'description': 'Specific geographic location',
            'risk': 'LOW'
        }
    }
    
    @staticmethod
    def scan_text(text: str) -> PIIDetection:
        """
        Scan text for potential PII
        
        Args:
            text: Clinical narrative text to scan
            
        Returns:
            PIIDetection with findings and risk assessment
        """
        
        if not text or not text.strip():
            return PIIDetection(
                text=text,
                pii_found=False,
                flagged_patterns=[],
                cleaned_text=text,
                risk_level="LOW"
            )
        
        text_lower = text.lower()
        flagged_patterns = []
        
        # Check each pattern
        for pattern_name, pattern_info in PIIScrubber.PATTERNS.items():
            matches = re.finditer(pattern_info['regex'], text_lower)
            
            for match in matches:
                flagged_patterns.append({
                    'pattern': pattern_name,
                    'matched_text': match.group(),
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'description': pattern_info['description'],
                    'risk': pattern_info['risk']
                })
        
        # Check for potential names
        name_flags = PIIScrubber._check_potential_names(text_lower)
        flagged_patterns.extend(name_flags)
        
        # Determine overall risk level
        risk_level = PIIScrubber._calculate_risk_level(flagged_patterns)
        
        # Generate cleaned text (for display purposes)
        cleaned_text = PIIScrubber._generate_cleaned_text(text, flagged_patterns)
        
        return PIIDetection(
            text=text,
            pii_found=len(flagged_patterns) > 0,
            flagged_patterns=flagged_patterns,
            cleaned_text=cleaned_text,
            risk_level=risk_level
        )
    
    @staticmethod
    def _check_potential_names(text_lower: str) -> List[Dict[str, Any]]:
        """Check for potential Indian names in text"""
        
        flagged_names = []
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        
        for word in words:
            if word in PIIScrubber.INDIAN_NAMES:
                # Find position in original text
                pattern = r'\b' + re.escape(word) + r'\b'
                match = re.search(pattern, text_lower)
                
                if match:
                    flagged_names.append({
                        'pattern': 'potential_name',
                        'matched_text': word,
                        'start_pos': match.start(),
                        'end_pos': match.end(),
                        'description': 'Potential Indian name',
                        'risk': 'HIGH'
                    })
        
        return flagged_names
    
    @staticmethod
    def _calculate_risk_level(flagged_patterns: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level based on flagged patterns"""
        
        if not flagged_patterns:
            return "LOW"
        
        high_risk_count = sum(1 for p in flagged_patterns if p['risk'] == 'HIGH')
        medium_risk_count = sum(1 for p in flagged_patterns if p['risk'] == 'MEDIUM')
        
        if high_risk_count >= 2:
            return "HIGH"
        elif high_risk_count >= 1:
            return "HIGH"
        elif medium_risk_count >= 3:
            return "MEDIUM"
        elif medium_risk_count >= 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def _generate_cleaned_text(original_text: str, flagged_patterns: List[Dict[str, Any]]) -> str:
        """Generate text with PII markers for review"""
        
        if not flagged_patterns:
            return original_text
        
        # Sort patterns by position (reverse order for replacement)
        sorted_patterns = sorted(flagged_patterns, key=lambda x: x['start_pos'], reverse=True)
        
        cleaned_text = original_text
        
        for pattern in sorted_patterns:
            start = pattern['start_pos']
            end = pattern['end_pos']
            replacement = f"[{pattern['description'].upper()}]"
            
            cleaned_text = cleaned_text[:start] + replacement + cleaned_text[end:]
        
        return cleaned_text
    
    @staticmethod
    def get_safety_recommendations(detection: PIIDetection) -> List[str]:
        """Get safety recommendations based on PII detection results"""
        
        recommendations = []
        
        if not detection.pii_found:
            recommendations.append("✅ No obvious PII detected. Text appears safe for storage.")
            return recommendations
        
        if detection.risk_level == "HIGH":
            recommendations.extend([
                "🔴 HIGH RISK: Potential PII detected. Review before submission.",
                "Remove any patient names, contact details, or identification numbers.",
                "Use generic terms like 'patient', 'child', 'infant' instead of names."
            ])
        
        elif detection.risk_level == "MEDIUM":
            recommendations.extend([
                "🟡 MEDIUM RISK: Some potentially identifying information found.",
                "Review flagged content and remove if it could identify the patient."
            ])
        
        else:  # LOW risk
            recommendations.append("🟢 LOW RISK: Minor flags detected. Review recommended but likely acceptable.")
        
        # Specific recommendations based on pattern types
        pattern_types = {p['pattern'] for p in detection.flagged_patterns}
        
        if 'phone_number' in pattern_types:
            recommendations.append("• Remove phone numbers")
        
        if 'hospital_number' in pattern_types:
            recommendations.append("• Remove hospital/medical record numbers")
        
        if 'potential_name' in pattern_types:
            recommendations.append("• Replace names with generic terms (patient, child, etc.)")
        
        if 'date_of_birth' in pattern_types:
            recommendations.append("• Remove specific dates of birth")
        
        if 'email' in pattern_types:
            recommendations.append("• Remove email addresses")
        
        return recommendations


def check_clinical_narrative_safety(chief_complaint: str, clinical_history: str) -> Dict[str, Any]:
    """
    Convenience function to check both chief complaint and clinical history for PII
    
    Args:
        chief_complaint: Chief complaint text
        clinical_history: Clinical history text
        
    Returns:
        Dictionary with PII analysis results
    """
    
    # Scan both texts
    complaint_scan = PIIScrubber.scan_text(chief_complaint)
    history_scan = PIIScrubber.scan_text(clinical_history)
    
    # Combine results
    all_patterns = complaint_scan.flagged_patterns + history_scan.flagged_patterns
    overall_pii_found = complaint_scan.pii_found or history_scan.pii_found
    
    # Calculate overall risk
    overall_risk = "LOW"
    if complaint_scan.risk_level == "HIGH" or history_scan.risk_level == "HIGH":
        overall_risk = "HIGH"
    elif complaint_scan.risk_level == "MEDIUM" or history_scan.risk_level == "MEDIUM":
        overall_risk = "MEDIUM"
    
    # Generate recommendations
    combined_detection = PIIDetection(
        text=f"{chief_complaint} {clinical_history}",
        pii_found=overall_pii_found,
        flagged_patterns=all_patterns,
        cleaned_text="",
        risk_level=overall_risk
    )
    
    recommendations = PIIScrubber.get_safety_recommendations(combined_detection)
    
    return {
        "chief_complaint_scan": {
            "pii_found": complaint_scan.pii_found,
            "risk_level": complaint_scan.risk_level,
            "flagged_patterns": complaint_scan.flagged_patterns,
            "cleaned_text": complaint_scan.cleaned_text
        },
        "clinical_history_scan": {
            "pii_found": history_scan.pii_found,
            "risk_level": history_scan.risk_level,
            "flagged_patterns": history_scan.flagged_patterns,
            "cleaned_text": history_scan.cleaned_text
        },
        "overall_assessment": {
            "pii_found": overall_pii_found,
            "risk_level": overall_risk,
            "total_flags": len(all_patterns),
            "safe_to_submit": overall_risk != "HIGH"
        },
        "recommendations": recommendations
    }


# Example usage and testing
if __name__ == "__main__":
    # Test cases for PII detection
    
    test_cases = [
        {
            "name": "Safe clinical text",
            "chief_complaint": "Fever and cough",
            "clinical_history": "3 year old child with fever since 2 days, cough, no vomiting"
        },
        {
            "name": "Text with potential name",
            "chief_complaint": "Aarav has fever",
            "clinical_history": "Child Priya brought by mother, fever since yesterday"
        },
        {
            "name": "Text with phone number",
            "chief_complaint": "Fever",
            "clinical_history": "Contact number 9876543210 for follow up"
        },
        {
            "name": "Text with hospital number",
            "chief_complaint": "Follow up case",
            "clinical_history": "Previous admission IP-12345, now presenting with fever"
        },
        {
            "name": "Text with multiple PII",
            "chief_complaint": "Ravi has fever",
            "clinical_history": "DOB 15/03/2020, father Rajesh Kumar, phone 9876543210, address Mangalore"
        }
    ]
    
    print("Testing PII Scrubber:")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Chief Complaint: '{test['chief_complaint']}'")
        print(f"Clinical History: '{test['clinical_history']}'")
        
        result = check_clinical_narrative_safety(
            test['chief_complaint'], 
            test['clinical_history']
        )
        
        print(f"Overall Risk: {result['overall_assessment']['risk_level']}")
        print(f"Safe to Submit: {result['overall_assessment']['safe_to_submit']}")
        print(f"Total Flags: {result['overall_assessment']['total_flags']}")
        
        if result['overall_assessment']['pii_found']:
            print("Recommendations:")
            for rec in result['recommendations']:
                print(f"  {rec}")
        
        print("-" * 40)