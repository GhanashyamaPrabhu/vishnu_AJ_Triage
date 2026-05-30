-- AJ Institute SATS AI Co-Pilot Database Schema
-- PostgreSQL/Supabase Schema for Clinical Trial Data Collection

-- Enable UUID extension for better ID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for authentication and role management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('triage_nurse', 'consultant', 'admin')),
    department VARCHAR(50) DEFAULT 'Department of Paediatrics',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Main cases table for triage data
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    study_id VARCHAR(20) UNIQUE NOT NULL, -- Format: AJ-YYYY-NNNN
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    nurse_id INTEGER REFERENCES users(id),
    shift VARCHAR(20) CHECK (shift IN ('Morning', 'Afternoon', 'Night')),
    triage_date DATE NOT NULL,
    triage_time TIME NOT NULL,
    
    -- Patient demographics (de-identified)
    age_value NUMERIC NOT NULL,
    age_unit VARCHAR(10) NOT NULL CHECK (age_unit IN ('Days', 'Months', 'Years')),
    age_months_calculated NUMERIC NOT NULL, -- Always stored as months for calculations
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Unknown')),
    weight_grams NUMERIC NOT NULL, -- Always stored in grams
    height_cm NUMERIC,
    patient_category VARCHAR(20) CHECK (patient_category IN ('Neonate', 'Infant', 'Toddler', 'Child', 'Adolescent')),
    
    -- Vital signs
    hr INTEGER NOT NULL, -- Heart rate (beats/min)
    rr INTEGER NOT NULL, -- Respiratory rate (breaths/min)
    temp_fahrenheit NUMERIC NOT NULL,
    temp_celsius NUMERIC NOT NULL, -- Auto-calculated
    spo2 INTEGER NOT NULL CHECK (spo2 >= 0 AND spo2 <= 100),
    
    -- Glasgow Coma Scale
    gcs_eye INTEGER NOT NULL CHECK (gcs_eye >= 1 AND gcs_eye <= 4),
    gcs_verbal INTEGER NOT NULL CHECK (gcs_verbal >= 1 AND gcs_verbal <= 5),
    gcs_motor INTEGER NOT NULL CHECK (gcs_motor >= 1 AND gcs_motor <= 6),
    gcs_total INTEGER NOT NULL CHECK (gcs_total >= 3 AND gcs_total <= 15),
    gcs_scale_used VARCHAR(20) NOT NULL CHECK (gcs_scale_used IN ('standard', 'pediatric')),
    gcs_interpretation VARCHAR(20) CHECK (gcs_interpretation IN ('Normal', 'Minor', 'Moderate', 'Severe', 'Critical')),
    
    -- Clinical narrative
    chief_complaint TEXT NOT NULL,
    clinical_history TEXT NOT NULL,
    
    -- Hard safety rules
    hard_rule_triggered BOOLEAN DEFAULT false,
    hard_rule_detail VARCHAR(255),
    
    -- Nurse triage decision (submitted before AI analysis)
    nurse_sats_category VARCHAR(10) NOT NULL CHECK (nurse_sats_category IN ('RED', 'ORANGE', 'YELLOW', 'GREEN')),
    nurse_confidence INTEGER NOT NULL CHECK (nurse_confidence >= 1 AND nurse_confidence <= 10),
    nurse_notes TEXT,
    nurse_submitted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- AI analysis results
    ai_category VARCHAR(10) CHECK (ai_category IN ('RED', 'ORANGE', 'YELLOW', 'GREEN')),
    ai_confidence_score INTEGER CHECK (ai_confidence_score >= 0 AND ai_confidence_score <= 100),
    ai_gcs_interpretation VARCHAR(20),
    ai_primary_concern TEXT,
    ai_reasoning TEXT,
    ai_red_flags TEXT[], -- Array of detected red flags
    ai_differentials TEXT[], -- Array of differential diagnoses
    ai_recommendation TEXT,
    ai_escalation_note TEXT,
    ai_raw_response JSONB, -- Full AI response for debugging
    ai_analyzed_at TIMESTAMP WITH TIME ZONE,
    
    -- Gold standard (consultant review)
    consultant_id INTEGER REFERENCES users(id),
    gold_standard_category VARCHAR(10) CHECK (gold_standard_category IN ('RED', 'ORANGE', 'YELLOW', 'GREEN')),
    consultant_notes TEXT,
    gold_standard_at TIMESTAMP WITH TIME ZONE,
    
    -- Analysis flags (auto-calculated)
    nurse_ai_agreement BOOLEAN,
    discrepancy_type VARCHAR(20) CHECK (discrepancy_type IN ('under_triage', 'over_triage', 'agreement')),
    
    -- Audit fields
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for tracking all system actions
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_cases_study_id ON cases(study_id);
CREATE INDEX idx_cases_nurse_id ON cases(nurse_id);
CREATE INDEX idx_cases_created_at ON cases(created_at);
CREATE INDEX idx_cases_nurse_category ON cases(nurse_sats_category);
CREATE INDEX idx_cases_ai_category ON cases(ai_category);
CREATE INDEX idx_cases_agreement ON cases(nurse_ai_agreement);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- Function to auto-generate study IDs
CREATE OR REPLACE FUNCTION generate_study_id()
RETURNS TRIGGER AS $$
DECLARE
    year_part VARCHAR(4);
    sequence_num INTEGER;
    new_study_id VARCHAR(20);
BEGIN
    -- Get current year
    year_part := EXTRACT(YEAR FROM NOW())::VARCHAR;
    
    -- Get next sequence number for this year
    SELECT COALESCE(MAX(CAST(SUBSTRING(study_id FROM 9) AS INTEGER)), 0) + 1
    INTO sequence_num
    FROM cases
    WHERE study_id LIKE 'AJ-' || year_part || '-%';
    
    -- Generate new study ID
    new_study_id := 'AJ-' || year_part || '-' || LPAD(sequence_num::VARCHAR, 4, '0');
    
    NEW.study_id := new_study_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate study IDs
CREATE TRIGGER trigger_generate_study_id
    BEFORE INSERT ON cases
    FOR EACH ROW
    EXECUTE FUNCTION generate_study_id();

-- Function to calculate age in months
CREATE OR REPLACE FUNCTION calculate_age_months(age_val NUMERIC, age_unit VARCHAR)
RETURNS NUMERIC AS $$
BEGIN
    CASE age_unit
        WHEN 'Days' THEN RETURN age_val / 30.44; -- Average days per month
        WHEN 'Months' THEN RETURN age_val;
        WHEN 'Years' THEN RETURN age_val * 12;
        ELSE RETURN 0;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- Function to convert Fahrenheit to Celsius
CREATE OR REPLACE FUNCTION fahrenheit_to_celsius(temp_f NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN ROUND((temp_f - 32) * 5.0 / 9.0, 1);
END;
$$ LANGUAGE plpgsql;

-- Function to determine patient category from age
CREATE OR REPLACE FUNCTION determine_patient_category(age_months NUMERIC)
RETURNS VARCHAR AS $$
BEGIN
    IF age_months <= 1 THEN RETURN 'Neonate'; -- 0-28 days
    ELSIF age_months <= 12 THEN RETURN 'Infant'; -- 1-12 months
    ELSIF age_months <= 36 THEN RETURN 'Toddler'; -- 1-3 years
    ELSIF age_months <= 144 THEN RETURN 'Child'; -- 3-12 years
    ELSE RETURN 'Adolescent'; -- 12-18 years
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate nurse-AI agreement
CREATE OR REPLACE FUNCTION calculate_agreement()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate agreement when AI analysis is completed
    IF NEW.ai_category IS NOT NULL AND OLD.ai_category IS NULL THEN
        NEW.nurse_ai_agreement := (NEW.nurse_sats_category = NEW.ai_category);
        
        -- Determine discrepancy type
        IF NEW.nurse_sats_category = NEW.ai_category THEN
            NEW.discrepancy_type := 'agreement';
        ELSE
            -- Define triage severity order: GREEN < YELLOW < ORANGE < RED
            CASE 
                WHEN (NEW.nurse_sats_category = 'GREEN' AND NEW.ai_category IN ('YELLOW', 'ORANGE', 'RED')) OR
                     (NEW.nurse_sats_category = 'YELLOW' AND NEW.ai_category IN ('ORANGE', 'RED')) OR
                     (NEW.nurse_sats_category = 'ORANGE' AND NEW.ai_category = 'RED') THEN
                    NEW.discrepancy_type := 'under_triage';
                ELSE
                    NEW.discrepancy_type := 'over_triage';
            END CASE;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to calculate agreement
CREATE TRIGGER trigger_calculate_agreement
    BEFORE UPDATE ON cases
    FOR EACH ROW
    EXECUTE FUNCTION calculate_agreement();

-- Trigger to auto-calculate derived fields on insert/update
CREATE OR REPLACE FUNCTION auto_calculate_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate age in months
    NEW.age_months_calculated := calculate_age_months(NEW.age_value, NEW.age_unit);
    
    -- Convert temperature to Celsius
    NEW.temp_celsius := fahrenheit_to_celsius(NEW.temp_fahrenheit);
    
    -- Auto-determine patient category if not provided
    IF NEW.patient_category IS NULL THEN
        NEW.patient_category := determine_patient_category(NEW.age_months_calculated);
    END IF;
    
    -- Calculate GCS total
    NEW.gcs_total := NEW.gcs_eye + NEW.gcs_verbal + NEW.gcs_motor;
    
    -- Update timestamp
    NEW.updated_at := NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-calculations
CREATE TRIGGER trigger_auto_calculate_fields
    BEFORE INSERT OR UPDATE ON cases
    FOR EACH ROW
    EXECUTE FUNCTION auto_calculate_fields();

-- Row Level Security (RLS) policies
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Policy: Nurses can only see their own cases
CREATE POLICY nurse_own_cases ON cases
    FOR ALL TO authenticated
    USING (
        CASE 
            WHEN auth.jwt() ->> 'role' = 'triage_nurse' THEN nurse_id = (auth.jwt() ->> 'user_id')::INTEGER
            WHEN auth.jwt() ->> 'role' IN ('consultant', 'admin') THEN true
            ELSE false
        END
    );

-- Policy: Users can see their own user record
CREATE POLICY users_own_record ON users
    FOR ALL TO authenticated
    USING (
        CASE 
            WHEN auth.jwt() ->> 'role' = 'admin' THEN true
            ELSE id = (auth.jwt() ->> 'user_id')::INTEGER
        END
    );

-- Policy: Audit log access for admins only
CREATE POLICY audit_admin_only ON audit_log
    FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');

-- Views for analytics
CREATE VIEW case_statistics AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_cases,
    COUNT(CASE WHEN nurse_sats_category = 'RED' THEN 1 END) as nurse_red,
    COUNT(CASE WHEN nurse_sats_category = 'ORANGE' THEN 1 END) as nurse_orange,
    COUNT(CASE WHEN nurse_sats_category = 'YELLOW' THEN 1 END) as nurse_yellow,
    COUNT(CASE WHEN nurse_sats_category = 'GREEN' THEN 1 END) as nurse_green,
    COUNT(CASE WHEN ai_category = 'RED' THEN 1 END) as ai_red,
    COUNT(CASE WHEN ai_category = 'ORANGE' THEN 1 END) as ai_orange,
    COUNT(CASE WHEN ai_category = 'YELLOW' THEN 1 END) as ai_yellow,
    COUNT(CASE WHEN ai_category = 'GREEN' THEN 1 END) as ai_green,
    ROUND(AVG(CASE WHEN nurse_ai_agreement THEN 1.0 ELSE 0.0 END) * 100, 1) as agreement_percentage,
    COUNT(CASE WHEN discrepancy_type = 'under_triage' THEN 1 END) as under_triage_cases,
    COUNT(CASE WHEN discrepancy_type = 'over_triage' THEN 1 END) as over_triage_cases
FROM cases
WHERE ai_category IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY date DESC;

CREATE VIEW shift_statistics AS
SELECT 
    shift,
    COUNT(*) as total_cases,
    ROUND(AVG(CASE WHEN nurse_ai_agreement THEN 1.0 ELSE 0.0 END) * 100, 1) as agreement_percentage,
    AVG(nurse_confidence) as avg_nurse_confidence,
    AVG(ai_confidence_score) as avg_ai_confidence
FROM cases
WHERE ai_category IS NOT NULL
GROUP BY shift;

-- Comments for documentation
COMMENT ON TABLE cases IS 'Main table storing all pediatric triage cases for clinical trial';
COMMENT ON TABLE users IS 'User authentication and role management';
COMMENT ON TABLE audit_log IS 'Audit trail for all system actions';
COMMENT ON COLUMN cases.study_id IS 'Unique study identifier in format AJ-YYYY-NNNN';
COMMENT ON COLUMN cases.age_months_calculated IS 'Age converted to months for consistent calculations';
COMMENT ON COLUMN cases.weight_grams IS 'Weight always stored in grams for consistency';
COMMENT ON COLUMN cases.hard_rule_triggered IS 'True if any hard safety rule was triggered';
COMMENT ON COLUMN cases.nurse_ai_agreement IS 'True if nurse and AI categories match';
COMMENT ON COLUMN cases.discrepancy_type IS 'Type of disagreement: under_triage, over_triage, or agreement';