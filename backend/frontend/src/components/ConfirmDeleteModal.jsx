// react imports
import React from "react";
import ReactDOM from "react-dom";

// icon imports
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

// style imports
import styles from "../styles/satellite/SatelliteProfileModal.module.css";

// confirm delete modal for general pop confirms for deleting elements
export default function ConfirmDeleteModal({
  title = "Confirm Delete",
  message,
  itemName,
  confirmLabel = "Delete",
  onConfirm,
  onCancel,
}) {
  // create the react dom modal
  return ReactDOM.createPortal(
    <div className={styles.confirmBackdrop}>
      <div className={styles.confirmModal}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <WarningAmberIcon sx={{ fontSize: 22, color: "#ef4444" }} />
          <span className={styles.confirmTitle}>{title}</span>
        </div>
        <p className={styles.confirmMessage}>
          {message ?? (
            <>
              Are you sure you want to delete{" "}
              <span className={styles.confirmName}>{itemName}</span>? This
              action cannot be undone.
            </>
          )}
        </p>
        <div className={styles.confirmActions}>
          <button className={styles.cancelButton} onClick={onCancel}>
            Cancel
          </button>
          <button className={styles.confirmDeleteButton} onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
