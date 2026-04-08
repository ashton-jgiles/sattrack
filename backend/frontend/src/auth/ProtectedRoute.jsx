// react and router imports
import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

// guards a route behind authentication and an optional minimum access level
// usage: <ProtectedRoute minLevel={2}><Dashboard /></ProtectedRoute>
export default function ProtectedRoute({ children, minLevel = 1 }) {
  const { user, loading } = useAuth();

  // wait for session restore before making a redirect decision
  if (loading) return null;

  // redirect unauthenticated users to login
  if (!user) return <Navigate to="/login" replace />;

  // redirect users who lack the required access level
  if (user.level_access < minLevel) return <Navigate to="/login" replace />;

  return children;
}
