// react imports
import React from "react";
import ReactDOM from "react-dom";

// icon imports
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

// style imports
import styles from "../styles/SatelliteProfileModal.module.css";

export default function ConfirmDeleteModal({ satellite, onConfirm, onCancel }) {
  return ReactDOM.createPortal(
    <div className={styles.confirmBackdrop}>
      <div className={styles.confirmModal}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <WarningAmberIcon sx={{ fontSize: 22, color: "#ef4444" }} />
          <span className={styles.confirmTitle}>Delete Satellite</span>
        </div>
        <p className={styles.confirmMessage}>
          Are you sure you want to delete{" "}
          <span className={styles.confirmName}>{satellite?.name}</span>? This
          will permanently remove the satellite and all associated trajectory,
          communication, and type data. This action cannot be undone.
        </p>
        <div className={styles.confirmActions}>
          <button className={styles.cancelButton} onClick={onCancel}>
            Cancel
          </button>
          <button className={styles.confirmDeleteButton} onClick={onConfirm}>
            Delete Satellite
          </button>
        </div>
      </div>
    </div>,
    document.body, // ✅ renders outside all overflow:hidden parents
  );
}
