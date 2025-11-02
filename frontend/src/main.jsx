import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './index.css';

function MainPage() {
  return (
    <div>
      <h1>Welcome to AsyncFlow</h1>
      <p>Your one-stop solution for managing orders and billing.</p>
      <Link to="/auth/signin">
        <button>Sign In</button>
      </Link>
    </div>
  );
}

function AppRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/auth/signin" element={<div>Sign In Page</div>} />
      </Routes>
    </Router>
  );
}

ReactDOM.render(<AppRouter />, document.getElementById('root'));
