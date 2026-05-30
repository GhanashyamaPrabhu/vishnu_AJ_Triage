"""
AI Service for AJ Institute SATS AI Co-Pilot
Anthropic Claude API integration with pediatric triage expertise
Includes comprehensive few-shot examples for clinical accuracy
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import anthropic
from datetime import datetime


@dataclass
class AIAnalysisResult:
    """Result of AI triage analysis"""
    triage_category: str
    confidence_score: int
    gcs_interpretation: str
    primary_concern: str
    reasoning: str
    red_flags_detected: list
    differential_considerations: list
    recommendation: str
    escalation_note: str
    raw_response: dict
    analysis_timestamp: datetime


class TriageAIService:
    """
    AI-powered pediatric triage analysis using Anthropic Claude
    Specialized for South African Triage System (SATS) in Indian context
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI service with Anthropic API key"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-6"
    
    def analyze_case(self, case_data: Dict[str, Any]) -> AIAnalysisResult:
        """
        Analyze pediatric triage case using AI
        
        Args:
            case_data: Dictionary containing patient vitals, demographics, and narrative
            
        Returns:
            AIAnalysisResult with triage recommendation and reasoning
        """
        
        try:
            # Prepare the case for AI analysis
            formatted_case = self._format_case_for_ai(case_data)
            
            # Get AI response
            response = self._call_claude_api(formatted_case)
            
            # Parse and validate response
            parsed_result = self._parse_ai_response(response)
            
            return AIAnalysisResult(
                triage_category=parsed_result['triage_category'],
                confidence_score=parsed_result['confidence_score'],
                gcs_interpretation=parsed_result['gcs_interpretation'],
                primary_concern=parsed_result['primary_concern'],
                reasoning=parsed_result['reasoning'],
                red_flags_detected=parsed_result['red_flags_detected'],
                differential_considerations=parsed_result['differential_considerations'],
                recommendation=parsed_result['recommendation'],
                escalation_note=parsed_result.get('escalation_note', ''),
                raw_response=parsed_result,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            # Return error result
            return AIAnalysisResult(
                triage_category="ERROR",
                confidence_score=0,
                gcs_interpretation="Error",
                primary_concern=f"AI Analysis Error: {str(e)}",
                reasoning="Unable to complete AI analysis due to technical error",
                red_flags_detected=[],
                differential_considerations=[],
                recommendation="Manual triage assessment required",
                escalation_note="AI system unavailable - use clinical judgment",
                raw_response={"error": str(e)},
                analysis_timestamp=datetime.now()
            )
    
    def _format_case_for_ai(self, case_data: Dict[str, Any]) -> str:
        """Format case data for AI analysis"""
        
        # Extract key data points
        age_value = case_data.get('age_value', 0)
        age_unit = case_data.get('age_unit', 'Months')
        weight_grams = case_data.get('weight_grams', 0)
        weight_kg = weight_grams / 1000 if weight_grams > 0 else 0
        
        # Format vitals
        hr = case_data.get('hr', 0)
        rr = case_data.get('rr', 0)
        temp_f = case_data.get('temp_fahrenheit', 98.6)
        spo2 = case_data.get('spo2', 100)
        
        # Format GCS
        gcs_eye = case_data.get('gcs_eye', 4)
        gcs_verbal = case_data.get('gcs_verbal', 5)
        gcs_motor = case_data.get('gcs_motor', 6)
        gcs_total = case_data.get('gcs_total', 15)
        
        # Format narrative
        chief_complaint = case_data.get('chief_complaint', '')
        clinical_history = case_data.get('clinical_history', '')
        
        formatted_case = f"""
Input: Age={age_value}{age_unit.lower()}, Weight={weight_kg:.1f}kg, HR={hr}, RR={rr}, Temp={temp_f}°F, SpO2={spo2}, GCS E={gcs_eye} V={gcs_verbal} M={gcs_motor} Total={gcs_total}
Narrative: "{clinical_history}"
"""
        
        return formatted_case.strip()
    
    def _call_claude_api(self, formatted_case: str) -> str:
        """Call Anthropic Claude API with the formatted case"""
        
        system_prompt = self._get_system_prompt()
        few_shot_examples = self._get_few_shot_examples()
        
        # Combine system prompt with few-shot examples and current case
        full_prompt = f"{few_shot_examples}\n\nNow analyze this new case:\n{formatted_case}\n\nOutput:"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.1,  # Low temperature for consistent medical analysis
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )
        
        return response.content[0].text
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate AI response JSON"""
        
        try:
            # Extract JSON from response (handle potential extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_text = response_text[json_start:json_end]
            parsed = json.loads(json_text)
            
            # Validate required fields
            required_fields = [
                'triage_category', 'confidence_score', 'gcs_interpretation',
                'primary_concern', 'reasoning', 'red_flags_detected',
                'differential_considerations', 'recommendation'
            ]
            
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate triage category
            valid_categories = ['RED', 'ORANGE', 'YELLOW', 'GREEN']
            if parsed['triage_category'] not in valid_categories:
                raise ValueError(f"Invalid triage category: {parsed['triage_category']}")
            
            # Validate confidence score
            if not isinstance(parsed['confidence_score'], int) or not (0 <= parsed['confidence_score'] <= 100):
                raise ValueError(f"Invalid confidence score: {parsed['confidence_score']}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in AI response: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing AI response: {e}")
    
    def _get_system_prompt(self) -> str:
        """Get the comprehensive system prompt for pediatric triage AI"""
        
        return """You are a senior pediatric emergency consultant AI assistant embedded in the South African Triage System (SATS) at AJ Institute of Medical Sciences, Mangalore, India.

You analyze pediatric clinical narratives and vital signs to suggest the most appropriate SATS triage category.

TRIAGE CATEGORIES:
- RED (Priority 1): Immediate life threat. Act now.
- ORANGE (Priority 2): Very urgent. Seen within 10 minutes.
- YELLOW (Priority 3): Urgent. Seen within 1 hour.
- GREEN (Priority 4): Non-urgent. Routine.

GCS INTERPRETATION:
  15 = Normal | 13–14 = Minor | 9–12 = Moderate (min ORANGE)
  ≤8 = Severe (automatic RED) | 3 = Critical RED
  For infants <2yr: use Pediatric GCS scoring interpretation.
  A DROPPING GCS trend always escalates to RED.

CRITICAL RED FLAGS (escalate regardless of vitals):
Neurological: not interacting, weak cry, staring spells, excessively sleepy, lethargy, altered consciousness, post-seizure, GCS dropping
Respiratory: abdominal breathing, head bobbing, grunting, nasal flaring, chest recession, stridor, apnea
Circulatory: no urine 12+ hours, mottled skin, cold hands with fever, poor perfusion, prolonged CRT, weak pulse
Feeding (infants <3mo): not feeding, poor feeding, refusing breast

MEDICAL ABBREVIATIONS: SOB=shortness of breath, h/o=history of, c/o=complains of, CRT=capillary refill time, GCS=Glasgow Coma Scale, E=Eye, V=Verbal, M=Motor, yo=years old, mo=months old, pGCS=Pediatric GCS, hx=history

TEMPERATURE SCALE: Fahrenheit
  Normal: 97.8–99.1°F | Fever: >100.4°F | High fever: >103°F | Danger: >105.8°F

UNITS: Weight in g (infants) or kg (children). Height in cm.

RULES:
1. Normal vitals do NOT exclude sick child if red flag phrases are present in narrative.
2. Active, playing, hydrated child with GCS=15 lowers urgency.
3. Always over-triage rather than under-triage.
4. You are a support tool. Final decision = clinician.
5. Consider local Indian context: tropical infections, dengue, malaria, typhoid as differentials for fever.

RESPOND ONLY IN THIS JSON FORMAT — no other text:
{
  "triage_category": "RED|ORANGE|YELLOW|GREEN",
  "confidence_score": 0-100,
  "gcs_interpretation": "Normal|Minor|Moderate|Severe|Critical",
  "primary_concern": "One phrase e.g. Possible septic shock",
  "reasoning": "2-3 sentence clinical justification citing specific phrases from the narrative and GCS",
  "red_flags_detected": ["flag1", "flag2"],
  "differential_considerations": ["dx1", "dx2"],
  "recommendation": "Specific immediate action steps",
  "escalation_note": "Any additional safety concerns"
}"""
    
    def _get_few_shot_examples(self) -> str:
        """Get comprehensive few-shot examples for training the AI"""
        
        return """[Case 1 — Sepsis infant]
Input: Age=3mo, Weight=5.2kg, HR=160, RR=50, Temp=100.6°F, SpO2=97, GCS E=4 V=4 M=6 Total=14
Narrative: "3mo baby, poor feeding, cold to touch, lethargic"
Output: {"triage_category":"RED","confidence_score":88,"gcs_interpretation":"Minor","primary_concern":"Possible neonatal/infant sepsis","reasoning":"Poor feeding and cold peripheries with low-grade fever in a 3-month-old indicates compensated sepsis. GCS=14 with lethargy in this age group is highly significant.","red_flags_detected":["poor feeding","cold to touch","lethargic","GCS=14 in infant"],"differential_considerations":["Sepsis","Meningitis","Metabolic"],"recommendation":"Immediate IV access, blood cultures, FBC, CRP, septic screen, senior review now","escalation_note":"3-month-olds can deteriorate rapidly. Do not wait for fever to develop."}

[Case 2 — Stable febrile child]
Input: Age=5yr, Weight=18kg, HR=110, RR=26, Temp=102.0°F, SpO2=98, GCS E=4 V=5 M=6 Total=15
Narrative: "5yo with fever, playing in corner, drinking well"
Output: {"triage_category":"YELLOW","confidence_score":82,"gcs_interpretation":"Normal","primary_concern":"Simple febrile illness","reasoning":"GCS=15, interactive, hydrated child with fever. No red flag phrases. Clinical appearance is reassuring.","red_flags_detected":[],"differential_considerations":["Viral URTI","UTI","Malaria"],"recommendation":"Antipyretics, urine dipstick, monitor","escalation_note":"Reassess if fever >48hrs or child deteriorates"}

[Case 3 — Chest pain]
Input: Age=10yr, Weight=32kg, HR=90, RR=20, Temp=98.6°F, SpO2=96, GCS E=4 V=5 M=6 Total=15
Narrative: "10yo sudden onset chest pain, pale, sweaty"
Output: {"triage_category":"ORANGE","confidence_score":85,"gcs_interpretation":"Normal","primary_concern":"Cardiac/respiratory cause of chest pain","reasoning":"Sudden onset chest pain with pallor and diaphoresis requires urgent workup. GCS=15 but clinical appearance concerning.","red_flags_detected":["chest pain","pale","sweaty"],"differential_considerations":["Arrhythmia","Pneumothorax","PE"],"recommendation":"ECG immediately, oxygen, IV access, senior review","escalation_note":"Do not delay ECG. Rule out arrhythmia first."}

[Case 4 — Severe bronchiolitis]
Input: Age=8mo, Weight=7.8kg, HR=155, RR=65, Temp=101.3°F, SpO2=93, GCS E=3 V=3 M=5 Total=11
Narrative: "8mo, grunting while sleeping, head bobbing, not feeding"
Output: {"triage_category":"RED","confidence_score":97,"gcs_interpretation":"Moderate","primary_concern":"Impending respiratory failure","reasoning":"Grunting and head bobbing = respiratory failure in infants. SpO2=93% and GCS=11 with poor feeding confirms severity.","red_flags_detected":["grunting","head bobbing","not feeding","SpO2=93","RR=65","GCS=11"],"differential_considerations":["Severe bronchiolitis","Pneumonia"],"recommendation":"Resuscitation bay, high-flow O2, suction, PICU alert, senior now","escalation_note":"Infant respiratory failure — can arrest rapidly"}

[Case 5 — DKA]
Input: Age=12yr, Weight=40kg, HR=122, RR=36, Temp=99.1°F, SpO2=97, GCS E=3 V=4 M=5 Total=12
Narrative: "12yo known diabetic, vomiting, deep fast breathing, fruity breath, confused"
Output: {"triage_category":"RED","confidence_score":96,"gcs_interpretation":"Moderate","primary_concern":"Diabetic Ketoacidosis (DKA)","reasoning":"Kussmaul breathing, confusion, fruity breath in a known diabetic = DKA. GCS=12 confirms altered sensorium.","red_flags_detected":["deep fast breathing","confused","GCS=12","fruity breath","known diabetic"],"differential_considerations":["DKA","HHS","Sepsis"],"recommendation":"BGL stat, blood gas, IV fluids 10ml/kg, insulin protocol, endocrine alert","escalation_note":"Check K+ before insulin. Monitor neuro closely."}

[Case 6 — Meningitis]
Input: Age=7yr, Weight=22kg, HR=98, RR=22, Temp=102.8°F, SpO2=99, GCS E=4 V=4 M=6 Total=14
Narrative: "7yo, severe headache, neck stiffness, vomiting, hates light, irritable"
Output: {"triage_category":"RED","confidence_score":93,"gcs_interpretation":"Minor","primary_concern":"Bacterial meningitis until proven otherwise","reasoning":"Classic triad: headache, neck stiffness, photophobia. GCS=14 (confused) with meningism = immediate LP prep needed.","red_flags_detected":["neck stiffness","photophobia","severe headache","GCS=14 with confusion"],"differential_considerations":["Bacterial meningitis","Viral meningitis","Encephalitis"],"recommendation":"IV access, blood cultures, LP prep, ceftriaxone on standby, senior review immediately","escalation_note":"Do not delay antibiotics if LP not immediately possible. CT first if papilledema suspected."}

[Case 7 — Febrile seizure]
Input: Age=18mo, Weight=10.5kg, HR=140, RR=30, Temp=103.5°F, SpO2=96, GCS E=3 V=3 M=5 Total=11
Narrative: "18mo, seizure at home 2 min, now drowsy, high fever"
Output: {"triage_category":"RED","confidence_score":95,"gcs_interpretation":"Moderate","primary_concern":"Post-ictal state — rule out meningitis","reasoning":"Post-ictal GCS=11 with fever. Cannot distinguish simple febrile seizure from meningitic seizure clinically yet.","red_flags_detected":["post-seizure","drowsy","GCS=11","Temp>103°F"],"differential_considerations":["Simple febrile seizure","Meningitis","Encephalitis"],"recommendation":"Airway monitoring, rectal diazepam on standby, LP after stabilization, senior review now","escalation_note":"GCS must improve to 15 within 1hr post-ictally or escalate to meningitis workup"}

[Case 8 — Septic shock]
Input: Age=4yr, Weight=16kg, HR=178, RR=42, Temp=104.2°F, SpO2=94, GCS E=3 V=4 M=4 Total=11
Narrative: "4yo, no urine since yesterday, mottled skin, cold hands, high fever, very weak, not responding well"
Output: {"triage_category":"RED","confidence_score":99,"gcs_interpretation":"Moderate","primary_concern":"Decompensating septic shock","reasoning":"Mottled skin, cold extremities, oliguria, HR=178, GCS=11 = septic shock. Immediate resuscitation required.","red_flags_detected":["mottled skin","no urine","cold hands","GCS=11","HR=178","weak"],"differential_considerations":["Septic shock","Dengue shock","Severe malaria"],"recommendation":"2x large bore IV, 20ml/kg NS bolus stat, blood cultures, FBC, lactate, senior emergency physician now","escalation_note":"Consider dengue/malaria given Indian context. ICU bed alert now."}"""


# Convenience function for API integration
def analyze_pediatric_triage_case(case_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze a pediatric triage case
    
    Args:
        case_data: Dictionary containing patient data
        api_key: Optional Anthropic API key (uses env var if not provided)
        
    Returns:
        Dictionary with AI analysis results
    """
    
    try:
        ai_service = TriageAIService(api_key)
        result = ai_service.analyze_case(case_data)
        
        return {
            "success": True,
            "ai_category": result.triage_category,
            "ai_confidence_score": result.confidence_score,
            "ai_gcs_interpretation": result.gcs_interpretation,
            "ai_primary_concern": result.primary_concern,
            "ai_reasoning": result.reasoning,
            "ai_red_flags": result.red_flags_detected,
            "ai_differentials": result.differential_considerations,
            "ai_recommendation": result.recommendation,
            "ai_escalation_note": result.escalation_note,
            "ai_raw_response": result.raw_response,
            "ai_analyzed_at": result.analysis_timestamp.isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ai_category": "ERROR",
            "ai_confidence_score": 0,
            "ai_primary_concern": f"AI Analysis Failed: {str(e)}",
            "ai_reasoning": "Unable to complete AI analysis",
            "ai_recommendation": "Use manual clinical assessment",
            "ai_escalation_note": "AI system unavailable"
        }


# Example usage and testing
if __name__ == "__main__":
    # Test case for AI analysis
    test_case = {
        "age_value": 3,
        "age_unit": "Months",
        "weight_grams": 5200,
        "hr": 160,
        "rr": 50,
        "temp_fahrenheit": 100.6,
        "spo2": 97,
        "gcs_eye": 4,
        "gcs_verbal": 4,
        "gcs_motor": 6,
        "gcs_total": 14,
        "chief_complaint": "Poor feeding",
        "clinical_history": "3 month old baby brought by mother with poor feeding since yesterday, cold to touch, more sleepy than usual"
    }
    
    print("Testing AI Triage Analysis:")
    print("=" * 50)
    print(f"Test case: {test_case['clinical_history']}")
    
    # Note: This will only work if ANTHROPIC_API_KEY is set
    try:
        result = analyze_pediatric_triage_case(test_case)
        
        if result['success']:
            print(f"AI Category: {result['ai_category']}")
            print(f"Confidence: {result['ai_confidence_score']}%")
            print(f"Primary Concern: {result['ai_primary_concern']}")
            print(f"Reasoning: {result['ai_reasoning']}")
            print(f"Red Flags: {result['ai_red_flags']}")
            print(f"Recommendation: {result['ai_recommendation']}")
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Test failed: {e}")
        print("Note: Requires ANTHROPIC_API_KEY environment variable")