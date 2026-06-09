import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DetailPasien from './pages/DetailPasien';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100 text-gray-800">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/detail/:id" element={<DetailPasien />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;