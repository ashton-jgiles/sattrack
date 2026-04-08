// react imports
import React, { useState } from "react";
import ReactDOM from "react-dom";

// icon imports
import CloseIcon from "@mui/icons-material/Close";
import SaveIcon from "@mui/icons-material/Save";

// style imports
import styles from "../../styles/satellite/SatelliteProfileModal.module.css";

const STATUS_OPTIONS = [
  { value: "pending", label: "Pending" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
];

const STATUS_STYLES = {
  approved: { backgroundColor: "#14532d", color: "#4ade80" },
  pending: { backgroundColor: "#1c1917", color: "#f59e0b" },
  rejected: { backgroundColor: "#450a0a", color: "#f87171" },
};

function Field({ label, value }) {
  return (
    <div className={styles.field}>
      <span className={styles.fieldLabel}>{label}</span>
      <span className={styles.fieldValue}>{value ?? "—"}</span>
    </div>
  );
}

function EditField({ label, value, onChange, full }) {
  return (
    <div className={`${styles.field} ${full ? styles.fieldFull : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <input
        type="text"
        className={styles.fieldInput}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default function DatasetProfileModal({ data, onClose, onSave }) {
  const [editData, setEditData] = useState({
    description: data.description ?? "",
    pull_frequency: data.pull_frequency ?? "",
    review_status: data.review_status ?? "pending",
  });
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState([]);

  const handleChange = (field, value) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setErrors([]);
    try {
      await onSave(editData);
      onClose();
    } catch (err) {
      console.error("Failed to save:", err);
      setErrors(["Failed to save changes. Please try again."]);
    } finally {
      setIsSaving(false);
    }
  };

  return ReactDOM.createPortal(
    <div
      className={styles.backdrop}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <div>
            <div className={styles.modalTitle}>{data.dataset_name}</div>
            <div className={styles.modalSubtitle}>{data.source}</div>
          </div>
          <button className={styles.closeButton} onClick={onClose}>
            <CloseIcon sx={{ fontSize: 18 }} />
          </button>
        </div>

        {/* Fields */}
        <div className={styles.tabContent}>
          <div className={styles.fieldGrid}>
            <Field label="Dataset ID" value={data.dataset_id} />
            <Field label="File Size" value={data.file_size} />
            <Field label="Source URL" value={data.source_url} />
            <Field
              label="Creation Date"
              value={
                data.creation_date
                  ? new Date(data.creation_date).toLocaleDateString()
                  : null
              }
            />
            <Field
              label="Last Pulled"
              value={
                data.last_pulled
                  ? new Date(data.last_pulled).toLocaleString()
                  : null
              }
            />
            <div className={styles.field}>
              <span className={styles.fieldLabel}>Review Status</span>
              <select
                className={styles.fieldInput}
                value={editData.review_status}
                onChange={(e) => handleChange("review_status", e.target.value)}
                style={STATUS_STYLES[editData.review_status] ?? {}}
              >
                {STATUS_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <EditField
              label="Pull Frequency"
              value={editData.pull_frequency}
              onChange={(v) => handleChange("pull_frequency", v)}
            />
            <EditField
              label="Description"
              value={editData.description}
              onChange={(v) => handleChange("description", v)}
              full
            />
          </div>
        </div>

        {/* Validation Errors */}
        {errors.length > 0 && (
          <div className={styles.errorBanner}>
            {errors.map((e, i) => (
              <span key={i} className={styles.errorItem}>
                • {e}
              </span>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className={styles.modalFooter}>
          <button className={styles.cancelButton} onClick={onClose}>
            Cancel
          </button>
          <button
            className={styles.saveButton}
            onClick={handleSave}
            disabled={isSaving}
          >
            <SaveIcon sx={{ fontSize: 16 }} />
            {isSaving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
