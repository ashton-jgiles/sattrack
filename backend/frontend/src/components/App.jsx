import React, { Component } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Landing from "../pages/Landing";
import LoginPage from "../pages/LoginPage";
import { Dashboard } from "../pages/Dashboard";
import ProtectedRoute from "../auth/ProtectedRoute";

export default class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<LoginPage />} />
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
