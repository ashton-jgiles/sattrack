// react imports and router imports
import React, { Component } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// page imports
import Landing from "../pages/Landing";
import LoginPage from "../pages/LoginPage";
import CreateAccountPage from "../pages/CreateAccount";
import Dashboard from "../pages/Dashboard";

// auth imports
import ProtectedRoute from "../auth/ProtectedRoute";

export default class App extends Component {
  // create the app constructor
  constructor(props) {
    super(props);
  }

  // render method to create our app from index.jsx
  render() {
    // create the basic landing and login - register and protect dashboard all other route changes are handled in dashboard
    return (
      <Router>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<CreateAccountPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute minLevel={1}>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    );
  }
}
