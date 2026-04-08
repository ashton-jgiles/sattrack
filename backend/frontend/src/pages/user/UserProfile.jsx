// react imports
import React, { useEffect, useState } from "react";

// icon imports
import SaveIcon from "@mui/icons-material/Save";
import LockIcon from "@mui/icons-material/Lock";

// component imports
import PopupMessage from "../../components/PopupMessage";

// hooks
import usePopupMessage from "../../hooks/usePopupMessage";
import { useAuth } from "../../hooks/useAuth";
import { useNavigate } from "react-router-dom";

// api imports
import {
  getUserProfile,
  updateOwnProfile,
  changePassword,
} from "../../api/userService";

// style imports
import styles from "../../styles/user/UserProfile.module.css";

// default user profile component
export default function UserProfile() {
  // component fields
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Profile form
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [subtypeData, setSubtypeData] = useState({});
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileError, setProfileError] = useState("");

  // Password form
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordError, setPasswordError] = useState("");

  // create the message popup
  const { message, messageFading, messageVisible, showPopupMessage } =
    usePopupMessage();

  // on mount load all the data
  useEffect(() => {
    if (!user?.username) return;
    getUserProfile(user.username)
      .then((data) => {
        setProfile(data);
        setFullName(data.full_name || "");
        setUsername(data.username || "");
        setSubtypeData(data.subtype_data || {});
      })
      .catch((err) => console.error("Failed to load profile:", err))
      .finally(() => setLoading(false));
  }, [user?.username]);

  // on save save the users profile
  const handleProfileSave = async () => {
    setProfileError("");
    if (!fullName.trim()) {
      setProfileError("Full name is required.");
      return;
    }
    if (!username.trim()) {
      setProfileError("Username is required.");
      return;
    }
    setProfileSaving(true);
    try {
      const res = await updateOwnProfile({
        full_name: fullName.trim(),
        username: username.trim(),
        subtype_data: subtypeData,
      });
      if (res.username_changed) {
        showPopupMessage("Username changed — redirecting to login...");
        setTimeout(() => {
          logout();
          navigate("/login");
        }, 3000);
      } else {
        updateUser({ full_name: res.full_name });
        showPopupMessage("Profile updated successfully");
      }
    } catch (err) {
      setProfileError(err.message || "Failed to update profile.");
    } finally {
      setProfileSaving(false);
    }
  };

  // on password change handle the password logic
  const handlePasswordChange = async () => {
    setPasswordError("");
    if (!oldPassword || !newPassword || !confirmPassword) {
      setPasswordError("All password fields are required.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters.");
      return;
    }
    setPasswordSaving(true);
    try {
      await changePassword({
        old_password: oldPassword,
        new_password: newPassword,
      });
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      showPopupMessage("Password changed successfully");
    } catch (err) {
      setPasswordError(err.message || "Failed to change password.");
    } finally {
      setPasswordSaving(false);
    }
  };

  // render subtype fields based on user subtype
  const renderSubtypeFields = () => {
    if (!profile) return null;
    const type = profile.user_type;

    if (type === "Amateur") {
      return (
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Interests</label>
          <textarea
            className={`${styles.fieldInput} ${styles.fieldTextarea}`}
            value={subtypeData.interests || ""}
            onChange={(e) =>
              setSubtypeData({ ...subtypeData, interests: e.target.value })
            }
            placeholder="Describe your interests..."
          />
        </div>
      );
    }
    if (type === "Scientist") {
      return (
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Profession</label>
          <input
            type="text"
            className={styles.fieldInput}
            value={subtypeData.profession || ""}
            onChange={(e) =>
              setSubtypeData({ ...subtypeData, profession: e.target.value })
            }
            placeholder="Your profession..."
          />
        </div>
      );
    }
    if (type === "Administrator" || type === "Data Analyst") {
      return (
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Employee ID</label>
          <input
            type="number"
            className={styles.fieldInput}
            value={subtypeData.employee_id ?? ""}
            disabled
          />
        </div>
      );
    }
    return null;
  };

  const initials = profile?.full_name
    ? profile.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "?";

  return (
    <div className={styles.page}>
      {/* Page Header */}
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.pageTitle}>User Profile</h2>
          <p className={styles.pageSubtitle}>
            Manage your account information and preferences
          </p>
        </div>
      </div>

      {loading ? (
        <div className={styles.loadingState}>Loading profile...</div>
      ) : (
        <div className={styles.contentGrid}>
          {/* Account Info Card */}
          <div className={styles.card}>
            <span className={styles.cardTitle}>Account Information</span>

            {/* Identity row */}
            <div className={styles.identityRow}>
              <div className={styles.avatar}>{initials}</div>
              <div className={styles.identityInfo}>
                <span className={styles.identityUsername}>
                  @{username || profile?.username}
                </span>
                <div className={styles.badgeRow}>
                  <span className={styles.badge}>
                    Level {profile?.level_access}
                  </span>
                  <span className={`${styles.badge} ${styles.badgeGreen}`}>
                    {profile?.user_type}
                  </span>
                </div>
              </div>
            </div>

            <hr className={styles.divider} />

            {/* Editable fields */}
            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel}>Full Name</label>
              <input
                type="text"
                className={styles.fieldInput}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your full name"
              />
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel}>Username</label>
              <input
                type="text"
                className={styles.fieldInput}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
              />
            </div>

            {profile?.user_type && profile.user_type !== "Unknown" && (
              <>
                <hr className={styles.divider} />
                <span className={styles.sectionHeader}>
                  {profile.user_type} Details
                </span>
                {renderSubtypeFields()}
              </>
            )}

            {profileError && (
              <span className={styles.fieldError}>{profileError}</span>
            )}

            <button
              className={styles.saveButton}
              onClick={handleProfileSave}
              disabled={profileSaving}
            >
              <SaveIcon sx={{ fontSize: 16 }} />
              {profileSaving ? "Saving..." : "Save Changes"}
            </button>
          </div>

          {/* Change Password Card */}
          <div className={styles.card}>
            <span className={styles.cardTitle}>Change Password</span>

            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel}>Current Password</label>
              <input
                type="password"
                className={styles.fieldInput}
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                placeholder="Enter current password"
              />
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel}>New Password</label>
              <input
                type="password"
                className={styles.fieldInput}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="At least 8 characters"
              />
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel}>Confirm New Password</label>
              <input
                type="password"
                className={styles.fieldInput}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Repeat new password"
              />
            </div>

            {passwordError && (
              <span className={styles.fieldError}>{passwordError}</span>
            )}

            <button
              className={styles.saveButton}
              onClick={handlePasswordChange}
              disabled={passwordSaving}
            >
              <LockIcon sx={{ fontSize: 16 }} />
              {passwordSaving ? "Updating..." : "Change Password"}
            </button>
          </div>
        </div>
      )}

      {message && (
        <PopupMessage
          message={message.message}
          type={message.type}
          fading={messageFading}
          visible={messageVisible}
        />
      )}
    </div>
  );
}
