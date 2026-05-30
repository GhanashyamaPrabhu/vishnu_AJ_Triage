-- Seed data for AJ Institute SATS AI Co-Pilot
-- Default users for clinical trial setup

-- Insert default admin user
-- Password: AJTriage2024! (hashed with bcrypt)
INSERT INTO users (username, password_hash, full_name, role, department, is_active) VALUES
('ajadmin', '$2b$12$LQv3c1yqBwlVHpPiKk/.Oe7vlNyNyeZpx.HL4ueuG9QqOqHd/tASi', 'AJ Institute Administrator', 'admin', 'Department of Paediatrics', true);

-- Insert sample triage nurses
-- Password for all: Nurse123! (hashed with bcrypt)
INSERT INTO users (username, password_hash, full_name, role, department, is_active) VALUES
('nurse_priya', '$2b$12$8Hw6TkrNuT7wjHqBVaHtUeQnm9WPLlkjGt.L/f5Q9FtaCMnCzqhCy', 'Priya Sharma', 'triage_nurse', 'Department of Paediatrics', true),
('nurse_rajesh', '$2b$12$8Hw6TkrNuT7wjHqBVaHtUeQnm9WPLlkjGt.L/f5Q9FtaCMnCzqhCy', 'Rajesh Kumar', 'triage_nurse', 'Department of Paediatrics', true),
('nurse_anita', '$2b$12$8Hw6TkrNuT7wjHqBVaHtUeQnm9WPLlkjGt.L/f5Q9FtaCMnCzqhCy', 'Anita Menon', 'triage_nurse', 'Department of Paediatrics', true),
('nurse_suresh', '$2b$12$8Hw6TkrNuT7wjHqBVaHtUeQnm9WPLlkjGt.L/f5Q9FtaCMnCzqhCy', 'Suresh Nair', 'triage_nurse', 'Department of Paediatrics', true);

-- Insert sample consultants
-- Password for all: Consultant123! (hashed with bcrypt)
INSERT INTO users (username, password_hash, full_name, role, department, is_active) VALUES
('dr_krishna', '$2b$12$9Ij7UlsOqV8xkHrCWbIuVfRqo0XQZmNkLt.M/g6R0GuDbNoCerqDz', 'Dr. Krishna Murthy', 'consultant', 'Department of Paediatrics', true),
('dr_lakshmi', '$2b$12$9Ij7UlsOqV8xkHrCWbIuVfRqo0XQZmNkLt.M/g6R0GuDbNoCerqDz', 'Dr. Lakshmi Devi', 'consultant', 'Department of Paediatrics', true),
('dr_ravi', '$2b$12$9Ij7UlsOqV8xkHrCWbIuVfRqo0XQZmNkLt.M/g6R0GuDbNoCerqDz', 'Dr. Ravi Chandran', 'consultant', 'Department of Paediatrics', true);

-- Create audit log entry for initial setup
INSERT INTO audit_log (user_id, action, details, ip_address) VALUES
(1, 'SYSTEM_SETUP', '{"message": "Initial user accounts created", "users_created": 8}', '127.0.0.1');

-- Display created users for reference
SELECT 
    username,
    full_name,
    role,
    CASE 
        WHEN role = 'admin' THEN 'AJTriage2024!'
        WHEN role = 'triage_nurse' THEN 'Nurse123!'
        WHEN role = 'consultant' THEN 'Consultant123!'
    END as default_password,
    is_active
FROM users
ORDER BY role, username;