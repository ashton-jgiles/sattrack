// react imports
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

// api imports
import { registerUser } from "../../api/userService";

// icon imports
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";

// style imports
import styles from "../../styles/login/LoginPage.module.css";

export default function CreateAccountPage() {
  // component fields
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // handle submit method to verify credentials on the backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // check if the passwords match
    if (password !== password2) {
      setError("Passwords do not match");
    }

    // create the user
    try {
      await registerUser(username, fullName, password);
      setSuccess(true);
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.message);
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
            <h2 className={styles.cardTitle}>Create Account</h2>
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
              <label className={styles.label}>Full Name</label>
              <input
                type="text"
                className={styles.input}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
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

            <div className={styles.field}>
              <label className={styles.label}>Re-Enter Password</label>
              <input
                type="password"
                className={styles.input}
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
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

            {success && (
              <div className={styles.success}>
                <span className={styles.successText}>
                  Account created! Redirecting to login...
                </span>
              </div>
            )}

            <button type="submit" className={styles.submitButton}>
              Create Account
            </button>
          </form>

          <div className={styles.backWrapper}>
            <button className={styles.backButton} onClick={() => navigate("/")}>
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
