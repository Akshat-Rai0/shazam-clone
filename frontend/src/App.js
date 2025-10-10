import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Library from './pages/Library';
import Stats from './pages/Stats';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);

  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home isLoading={isLoading} setIsLoading={setIsLoading} />} />
            <Route path="/upload" element={<Upload isLoading={isLoading} setIsLoading={setIsLoading} />} />
            <Route path="/library" element={<Library isLoading={isLoading} setIsLoading={setIsLoading} />} />
            <Route path="/stats" element={<Stats isLoading={isLoading} setIsLoading={setIsLoading} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;