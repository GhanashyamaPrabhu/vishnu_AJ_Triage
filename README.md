# SATS AI Co-Pilot — Paediatric Triage

**A.J. INSTITUTE OF MEDICAL SCIENCES AND RESEARCH CENTRE**  
Department of Paediatrics

Clinical Trial Data Collection System for Pediatric Triage using AI-assisted South African Triage System (SATS).

## 🏥 Overview

This is a production-ready web application designed for clinical trials studying the effectiveness of AI-assisted pediatric triage. The system combines traditional nursing assessment with AI-powered recommendations using Anthropic Claude, while maintaining strict safety protocols and ethics compliance.

### Key Features

- **🔐 Secure Authentication** - Role-based access control (Nurse, Consultant, Admin)
- **👶 Pediatric-Focused** - Age-appropriate vital signs and GCS assessment
- **🛡️ Hard Safety Rules** - Automatic RED category for critical conditions
- **🤖 AI Analysis** - Anthropic Claude-powered triage recommendations
- **🔒 PII Protection** - Automated detection of personally identifiable information
- **📊 Real-time Analytics** - Dashboard with agreement metrics and statistics
- **📋 Audit Trail** - Complete logging of all system actions
- **📤 Export Functionality** - CSV/Excel export for research analysis

## 🌐 Internet-Accessible Deployment

This application is designed to be accessible from anywhere in the world with an internet connection. No local setup required for clinical staff.

### Deployment Stack

- **Frontend**: Vercel (React + Tailwind CSS)
- **Backend**: Railway (FastAPI + Python)
- **Database**: Supabase (PostgreSQL)
- **AI Service**: Anthropic Claude API
- **Domain**: Custom domain with SSL

### Why This Stack?

✅ **Global Access**: Works from India, USA, or anywhere  
✅ **No Installation**: Just open a URL in any browser  
✅ **Mobile Friendly**: Works on phones, tablets, computers  
✅ **Always Online**: 99.9% uptime guarantee  
✅ **Free Tier**: No cost during clinical trial phase  
✅ **Secure**: HTTPS, encrypted data, audit logging  

## 🚀 Quick Start for Clinical Staff

### For Medical Staff (No Technical Setup Required)

1. **Open the Application**
   ```
   https://aj-sats-triage.vercel.app
   ```

2. **Login with Provided Credentials**
   - Username: `nurse_priya` (or assigned username)
   - Password: `Nurse123!` (will be changed after first login)

3. **Start Using the System**
   - Enter patient data
   - Submit triage assessment
   - View AI recommendations
   - Complete case documentation

### Default User Accounts

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Admin | `ajadmin` | `AJTriage2024!` | Full system access |
| Consultant | `dr_krishna` | `Consultant123!` | Review all cases, gold standard |
| Nurse | `nurse_priya` | `Nurse123!` | Submit cases, view own only |

## 🏗️ Technical Architecture

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Header.tsx       # AJ Institute branded header
│   │   ├── TriageForm.tsx   # Main case entry form
│   │   ├── GCSCalculator.tsx # Interactive GCS widget
│   │   ├── VitalsInput.tsx  # Vitals with normal ranges
│   │   ├── ResultCard.tsx   # AI result display
│   │   └── AdminDashboard.tsx # Analytics dashboard
│   ├── pages/               # Page components
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Utility functions
│   └── types/               # TypeScript definitions
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

### Backend (FastAPI + Python)
```
backend/
├── main.py                  # FastAPI application entry
├── hard_rules.py           # Safety rules (runs first)
├── ai_service.py           # Claude API integration
├── gcs_calculator.py       # GCS scoring logic
├── pii_scrubber.py         # PII detection
├── auth.py                 # JWT authentication
├── database.py             # Supabase connection
├── models.py               # Pydantic data models
└── requirements.txt
```

### Database (PostgreSQL)
```
database/
├── schema.sql              # Complete database schema
└── seed_users.sql          # Default user accounts
```

## 🔧 Development Setup

### Prerequisites
- Node.js 18+ and npm 9+
- Python 3.11+
- Git

### Environment Variables

Create `.env` file in project root:
```bash
# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co/rest/v1/
SUPABASE_KEY=your-supabase-anon-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# AI Service
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Security
SECRET_KEY=your-secret-key-for-jwt-tokens
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
1. Create Supabase project at [supabase.com](https://supabase.com)
2. Run `database/schema.sql` in Supabase SQL editor
3. Run `database/seed_users.sql` to create default users
4. Update `.env` with your Supabase credentials

## 📊 Clinical Trial Features

### Triage Categories (SATS)
- **🔴 RED** - Immediate (life-threatening)
- **🟠 ORANGE** - Very urgent (≤10 minutes)
- **🟡 YELLOW** - Urgent (≤1 hour)
- **🟢 GREEN** - Routine

### Hard Safety Rules
Automatic RED assignment for:
- SpO2 < 90%
- GCS ≤ 8
- Critical vital signs (age-adjusted)
- Sick neonate indicators
- Severe neurological signs

### AI Analysis
- **Model**: Anthropic Claude Sonnet
- **Training**: 8 comprehensive pediatric examples
- **Context**: Indian healthcare setting
- **Safety**: Always over-triage vs under-triage
- **Transparency**: Full reasoning provided

### Data Collection
- **De-identified**: No patient names or identifiers
- **Structured**: Consistent data format for analysis
- **Timestamped**: Complete audit trail
- **Exportable**: CSV/Excel for statistical analysis

## 🔒 Security & Compliance

### Ethics Compliance
- ✅ No patient identifiers stored
- ✅ PII detection and warnings
- ✅ Audit trail for all actions
- ✅ Role-based access control
- ✅ Secure data transmission (HTTPS)

### Data Security
- JWT authentication with 12-hour expiry
- bcrypt password hashing
- Row-level security in database
- Rate limiting and input validation
- Comprehensive error handling

### HIPAA Considerations
- No PHI (Protected Health Information) stored
- Clinical data only (age, vitals, symptoms)
- Secure cloud infrastructure
- Audit logging for compliance

## 📈 Analytics & Reporting

### Dashboard Metrics
- Total cases processed
- Nurse-AI agreement rates
- Triage category distribution
- Cases requiring gold standard review
- Performance by shift/time

### Export Capabilities
- Complete case data (CSV/Excel)
- Date range filtering
- Statistical analysis ready
- Research publication format

## 🌍 Global Deployment Guide

### Step 1: Database Setup (Supabase)
1. Go to [supabase.com](https://supabase.com) → New Project
2. Project name: `aj-sats-triage`
3. Run SQL schema from `database/schema.sql`
4. Copy Project URL and anon key

### Step 2: AI Service Setup (Anthropic)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create API key
3. Add billing method (clinical trial: ~$5-10/month)

### Step 3: Backend Deployment (Railway)
1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project
3. Deploy from GitHub repository
4. Add environment variables:
   ```
   ANTHROPIC_API_KEY=your_key
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   SECRET_KEY=random_string
   ```
5. Copy Railway URL (e.g., `aj-sats-api.railway.app`)

### Step 4: Frontend Deployment (Vercel)
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import from GitHub
3. Add environment variable:
   ```
   VITE_API_URL=https://aj-sats-api.railway.app
   ```
4. Deploy → Copy URL

### Step 5: Share with Clinical Team
**Final URL**: `https://aj-sats-triage.vercel.app`

✅ **Works everywhere with internet**  
✅ **No installation required**  
✅ **Mobile and desktop compatible**  
✅ **Secure HTTPS connection**  

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing Checklist
- [ ] User authentication (all roles)
- [ ] Case creation and submission
- [ ] Hard safety rules triggering
- [ ] AI analysis generation
- [ ] PII detection warnings
- [ ] Export functionality
- [ ] Mobile responsiveness

## 📚 API Documentation

Once deployed, API documentation is available at:
- **Swagger UI**: `https://your-backend-url/docs`
- **ReDoc**: `https://your-backend-url/redoc`

### Key Endpoints
- `POST /login` - User authentication
- `POST /cases` - Create new triage case
- `POST /check-pii` - PII detection
- `POST /calculate-gcs` - GCS calculation
- `GET /health` - System health check

## 🤝 Support

### For Clinical Staff
- **Training**: 30-minute orientation session
- **Support**: Email support during trial period
- **Documentation**: User manual provided separately

### For Technical Issues
- **Backend**: Check Railway deployment logs
- **Frontend**: Check Vercel deployment status
- **Database**: Check Supabase dashboard
- **AI**: Verify Anthropic API key and billing

## 📄 License

**Proprietary - Clinical Trial Use Only**

This software is developed specifically for the clinical trial at A.J. Institute of Medical Sciences and Research Centre. Not for commercial distribution.

## 🏆 Acknowledgments

- **A.J. Institute of Medical Sciences** - Clinical expertise and requirements
- **Department of Paediatrics** - Medical validation and testing
- **Anthropic** - Claude AI model for triage analysis
- **Supabase** - Database infrastructure
- **Vercel & Railway** - Deployment platforms

---

**For questions or support, contact:**  
📧 info@ajims.edu.in  
🌐 https://ajims.edu.in  
📱 Clinical trial coordinator: [Contact details]