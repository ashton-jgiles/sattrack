// react and post api imports
import React, { createContext, useContext, useState, useEffect } from "react";
import { post } from "../api/api";

// creating the auth context
const AuthContext = createContext(null);

export default function AuthProvider({ children }) {
  // function methods
  const [user, setUser] = useState(null); // { username, full_name, role, level_access }
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

  // login function
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

  // logout function
  const logout = () => {
    setAccessToken(null);
    setUser(null);
    sessionStorage.clear();
  };

  // return the auth context
  return (
    <AuthContext.Provider value={{ user, accessToken, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// export use auth function
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
