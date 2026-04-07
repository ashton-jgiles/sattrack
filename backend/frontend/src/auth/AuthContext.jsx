// react and api imports
import React, { createContext, useContext, useState, useEffect } from "react";
import { post } from "../api/api";

// creating the auth context
const AuthContext = createContext(null);

// export the auth provider function
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, restore session from sessionStorage
  useEffect(() => {
    const storedUser = sessionStorage.getItem("user");
    const storedToken = sessionStorage.getItem("access_token");
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setAccessToken(storedToken);
    }
    setLoading(false);
  }, []);

  // login method to call our login endpoint
  const login = async (username, password) => {
    const data = await post("/auth/login/", { username, password });
    const {
      access,
      refresh,
      username: uname,
      full_name,
      role,
      level_access,
    } = data;

    // store the user data
    const userData = { username: uname, full_name, role, level_access };

    // Store access token in memory and sessionStorage
    // Store refresh token in sessionStorage (use httpOnly cookie in production)
    setAccessToken(access);
    setUser(userData);
    sessionStorage.setItem("access_token", access);
    sessionStorage.setItem("refresh_token", refresh);
    sessionStorage.setItem("user", JSON.stringify(userData));

    return userData;
  };

  // patch the in-memory user object and sessionStorage (e.g. after profile update)
  const updateUser = (updates) => {
    const updated = { ...user, ...updates };
    setUser(updated);
    sessionStorage.setItem("user", JSON.stringify(updated));
  };

  // logout method
  const logout = () => {
    setAccessToken(null);
    setUser(null);
    sessionStorage.clear();
  };

  // return the auth context
  return (
    <AuthContext.Provider value={{ user, accessToken, login, logout, updateUser, loading }}>
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
