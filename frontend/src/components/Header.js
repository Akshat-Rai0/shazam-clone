import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Music, Upload, Library, BarChart3 } from 'lucide-react';
import './Header.css';

const Header = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Recognize', icon: Music },
    { path: '/upload', label: 'Upload', icon: Upload },
    { path: '/library', label: 'Library', icon: Library },
    { path: '/stats', label: 'Stats', icon: BarChart3 },
  ];

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <Music className="logo-icon" />
          <span className="logo-text">Shazam Clone</span>
        </Link>
        
        <nav className="nav">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`nav-link ${location.pathname === path ? 'active' : ''}`}
            >
              <Icon className="nav-icon" />
              <span className="nav-text">{label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
};

export default Header;