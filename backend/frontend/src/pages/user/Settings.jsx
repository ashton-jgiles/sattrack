// react imports
import React, { useEffect, useState } from "react";

// icon imports
import EditIcon from "@mui/icons-material/Edit";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import CachedIcon from "@mui/icons-material/Cached";

// component imports
import UserProfileModal from "../../components/user/UserProfileModal";
import ConfirmDeleteModal from "../../components/ConfirmDeleteModal";
import PopupMessage from "../../components/PopupMessage";

// hooks
import usePopupMessage from "../../hooks/usePopupMessage";

// api imports
import { updateTrajectories } from "../../api/settingsService";
import {
  getUsers,
  getUserProfile,
  modifyUser,
  deleteUser,
} from "../../api/userService";

// style imports
import styles from "../../styles/user/Settings.module.css";

// subclass filters array
const SUBCLASS_FILTERS = [
  { value: "all", label: "All Types" },
  { value: "Administrator", label: "Administrator" },
  { value: "Scientist", label: "Scientist" },
  { value: "Data Analyst", label: "Data Analyst" },
  { value: "Amateur", label: "Amateur" },
];

export default function Settings() {
  // component fields
  const [users, setUsers] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const [userLoading, setUserLoading] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [trajectoryUpdating, setTrajectoryUpdating] = useState(false);
  const { message, messageFading, messageVisible, showPopupMessage } =
    usePopupMessage();

  // Load user list on mount
  useEffect(() => {
    getUsers()
      .then((data) => setUsers(data))
      .catch((err) => console.error("Failed to load users:", err))
      .finally(() => setLoading(false));
  }, []);

  // filter users by subclass type
  const filtered =
    filter === "all" ? users : users.filter((u) => u.user_type === filter);

  // handle edit click
  const handleEditClick = async (username) => {
    setUserLoading(true);
    try {
      const data = await getUserProfile(username);
      setUserData(data);
    } catch (err) {
      console.error("Failed to load user profile:", err);
    } finally {
      setUserLoading(false);
    }
  };

  // handle delete satellite
  const handleDeleteConfirm = async () => {
    if (!deleteTarget) {
      return;
    }
    try {
      await deleteUser(deleteTarget.username);
      setUsers((prev) =>
        prev.filter((u) => u.username !== deleteTarget.username),
      );
      setDeleteTarget(null);
      showPopupMessage("User deleted successfully");
    } catch (err) {
      console.error("Failed to delete user:", err);
      showPopupMessage("Failed to delete user", "error");
    }
  };

  // handle update trajectory
  const handleUpdateTrajectory = async () => {
    setTrajectoryUpdating(true);
    try {
      await updateTrajectories();
      showPopupMessage("Trajectory update started");
    } catch (err) {
      console.error("Failed to start trajectory update:", err);
      showPopupMessage("Failed to start trajectory update", "error");
    } finally {
      setTrajectoryUpdating(false);
    }
  };

  return (
    <div className={styles.page}>
      {/* Page Header */}
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.pageTitle}>Settings</h2>
          <p className={styles.pageSubtitle}>
            View, Manage, Raise access level of users and update trajectory data
            of all current satellites
          </p>
        </div>
        <button
          className={styles.refreshButton}
          onClick={handleUpdateTrajectory}
          disabled={trajectoryUpdating}
        >
          <CachedIcon sx={{ fontSize: 18 }} />
          {trajectoryUpdating ? "Starting..." : "Refresh Satellite Trajectory"}
        </button>
      </div>

      {/* Filter Bar */}
      <div className={styles.filterBar}>
        <span className={styles.filterLabel}>Filter by user type:</span>
        <select
          className={styles.filterSelect}
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          {SUBCLASS_FILTERS.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>
      </div>

      {/* User List */}
      <div className={styles.listCard}>
        {/* List Header */}
        <div className={styles.listHeader}>
          <span className={styles.listHeaderCell}>Name</span>
          <span className={styles.listHeaderCell}>Username</span>
          <span className={styles.listHeaderCell}>Access Level</span>
          <span className={styles.listHeaderCell}>User Type</span>
          <span className={styles.listHeaderCell}></span>
          <span className={styles.listHeaderCell}></span>
        </div>

        {/* List Body */}
        <div className={styles.listBody}>
          {loading ? (
            <div className={styles.emptyState}>Loading users...</div>
          ) : filtered.length === 0 ? (
            <div className={styles.emptyState}>No users found</div>
          ) : (
            filtered.map((user) => (
              <div key={user.full_name} className={styles.listRow}>
                <div className={styles.listRowName}>
                  <div className={styles.listDot} />
                  {user.full_name}
                </div>
                <div className={styles.listCell}>{user.username}</div>
                <div className={styles.listCell}>{user.level_access}</div>
                <div className={styles.listCell}>
                  <span className={styles.typeBadge}>{user.user_type}</span>
                </div>
                <button
                  className={styles.deleteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEditClick(user.username);
                  }}
                >
                  <EditIcon sx={{ fontSize: 18 }} />
                </button>
                <button
                  className={styles.deleteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteTarget(user);
                  }}
                >
                  <DeleteOutlineIcon sx={{ fontSize: 18 }} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* User Profile Modal */}
      {userData && (
        <UserProfileModal
          data={userData}
          onClose={() => setUserData(null)}
          onSave={async (payload) => {
            await modifyUser(payload);
            showPopupMessage("User updated successfully");
          }}
        />
      )}

      {/* Confirm Delete Modal */}
      {deleteTarget && (
        <ConfirmDeleteModal
          title="Remove User"
          message="Removing this user will permanently remove it from the database."
          confirmLabel="Delete"
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteTarget(null)}
        />
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
