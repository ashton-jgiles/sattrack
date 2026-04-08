// react imports
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// import authentication
import { useAuth } from "../../hooks/useAuth";

// icon imports
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";

// style imports
import styles from "../../styles/login/LoginPage.module.css";

export default function LoginPage() {
  // component fields
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // handle submit method to verify credentials on the backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const user = await login(username, password);
      navigate("/dashboard");
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  // main component structure
  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <SatelliteAltIcon className={styles.logoIcon} sx={{ fontSize: 40 }} />
          <h1 className={styles.logoText}>SatTrack</h1>
        </div>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <LockOutlinedIcon
              className={styles.cardHeaderIcon}
              sx={{ fontSize: 24 }}
            />
            <h2 className={styles.cardTitle}>Login</h2>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.field}>
              <label className={styles.label}>Username</label>
              <input
                type="text"
                className={styles.input}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Password</label>
              <input
                type="password"
                className={styles.input}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && (
              <div className={styles.error}>
                <ErrorOutlineOutlinedIcon
                  className={styles.errorIcon}
                  sx={{ fontSize: 20 }}
                />
                <span className={styles.errorText}>{error}</span>
              </div>
            )}

            <button type="submit" className={styles.submitButton}>
              Sign In
            </button>
          </form>

          <div className={styles.backWrapper}>
            <button
              className={styles.backButton}
              onClick={() => navigate("/register")}
            >
              Create Account
            </button>
            <button className={styles.backButton} onClick={() => navigate("/")}>
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
