import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import TriageForm from './components/TriageForm';
import AdminDashboard from './components/AdminDashboard';
import CaseHistory from './components/CaseHistory';
import AgreementBanner from './components/AgreementBanner';

function App() {
  // Mock user for components that need it
  const mockUser = {
    id: 1,
    username: 'nurse',
    full_name: 'Triage Nurse',
    role: 'triage_nurse'
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header user={mockUser} onLogout={() => {}} />
        <AgreementBanner />
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<TriageForm user={mockUser} />} />
            <Route path="/admin" element={<AdminDashboard user={mockUser} />} />
            <Route path="/history" element={<CaseHistory user={mockUser} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;