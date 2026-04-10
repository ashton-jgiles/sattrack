// react and api imports
import React, { createContext, useContext, useState, useEffect } from "react";
import { post, refreshAccessToken } from "../api/api";

// creating the auth context
const AuthContext = createContext(null);

// export the auth provider function
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, restore user metadata from sessionStorage.
  // Proactively refresh the access token so it is always present, the browser
  // silently deletes expired http only cookies, which would cause AllowAny
  // endpoints to treat the user as anonymous without ever returning a 401.
  useEffect(() => {
    const storedUser = sessionStorage.getItem("user");
    if (storedUser) {
      refreshAccessToken()
        .then(() => setUser(JSON.parse(storedUser)))
        .catch(() => sessionStorage.removeItem("user"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // Listen for session expiry events dispatched by the api layer when token refresh fails
  useEffect(() => {
    const handleExpired = () => {
      setUser(null);
      sessionStorage.removeItem("user");
    };
    window.addEventListener("auth:expired", handleExpired);
    return () => window.removeEventListener("auth:expired", handleExpired);
  }, []);

  // login backend sets httpOnly cookies; we only receive non-sensitive user metadata
  const login = async (username, password) => {
    const data = await post("/auth/login/", { username, password });
    const { username: uname, full_name, role, level_access } = data;

    const userData = { username: uname, full_name, role, level_access };
    setUser(userData);
    sessionStorage.setItem("user", JSON.stringify(userData));

    return userData;
  };

  // patch the in-memory user object and sessionStorage (e.g. after profile update)
  const updateUser = (updates) => {
    const updated = { ...user, ...updates };
    setUser(updated);
    sessionStorage.setItem("user", JSON.stringify(updated));
  };

  // logout ask the backend to clear the httpOnly cookies, then clear local state
  const logout = async () => {
    try {
      await post("/auth/logout/", {});
    } catch {
      // even if the request fails, clear local state so the UI reflects logged-out
    }
    setUser(null);
    sessionStorage.removeItem("user");
  };

  // return the auth context
  return (
    <AuthContext.Provider value={{ user, login, logout, updateUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// export user auth function
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
