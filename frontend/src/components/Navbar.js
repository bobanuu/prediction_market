import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <span className="font-bold text-xl">PrediX</span>
        <span className="text-sm opacity-80 ml-2">Markets</span>
      </Link>
      
      {user ? (
        <div className="navbar-nav">
          <Link to="/" className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Dashboard
          </Link>
          <Link to="/markets" className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Markets
          </Link>
          <Link to="/portfolio" className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            Portfolio
          </Link>
          <div className="navbar-user">
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-xs opacity-80">Welcome back</div>
                <div className="font-semibold">{user.username}</div>
              </div>
              <div className="text-right">
                <div className="text-xs opacity-80">Balance</div>
                <div className="font-mono font-bold text-green-400">
                  ${parseFloat(user.balance).toFixed(2)}
                </div>
              </div>
              <button 
                onClick={handleLogout} 
                className="logout-btn"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="navbar-nav">
          <Link to="/login" className="btn btn-outline text-sm px-4 py-2">
            Login
          </Link>
          <Link to="/register" className="btn btn-primary text-sm px-4 py-2">
            Get Started
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
