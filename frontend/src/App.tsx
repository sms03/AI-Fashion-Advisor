import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import './styles.scss';
import FashionAdvisor from './components/FashionAdvisor';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Router>
        <Routes>
          <Route path="/" element={<FashionAdvisor />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
