// react imports
import React, { useState } from "react";
import ReactDOM from "react-dom";

// icon imports
import CloseIcon from "@mui/icons-material/Close";
import SaveIcon from "@mui/icons-material/Save";

// style imports
import styles from "../styles/UserProfileModal.module.css";

// field components
function Field({ label, value, full }) {
  return (
    <div className={`${styles.field} ${full ? styles.fieldFull : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <span className={styles.fieldValue}>{value ?? "—"}</span>
    </div>
  );
}

// edit field component
function EditField({ label, value, onChange, full, type = "text" }) {
  return (
    <div className={`${styles.field} ${full ? styles.fieldFull : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <input
        type={type}
        className={styles.fieldInput}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

// select field component
function SelectField({ label, value, onChange, options, full }) {
  return (
    <div className={`${styles.field} ${full ? styles.fieldFull : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <select
        className={styles.fieldInput}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

const READ_ONLY_TYPE_FIELDS = new Set(["full_name"]);

export default function UserProfileModal({ data, onClose, onSave }) {
  const [form, setForm] = useState({
    username: data.username ?? "",
    level_access: String(data.level_access ?? "1"),
    user_type: data.user_type ?? "Amateur",
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({ ...form, original_username: data.username });
      onClose();
    } finally {
      setSaving(false);
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
            <span className={styles.modalTitle}>Edit User</span>
            <p className={styles.modalSubtitle}>{data.full_name}</p>
          </div>
          <button className={styles.closeButton} onClick={onClose}>
            <CloseIcon sx={{ fontSize: 18 }} />
          </button>
        </div>

        {/* Fields */}
        <div className={styles.fieldContent}>
          <div className={styles.fieldGrid}>
            <Field label="Full Name" value={data.full_name} />
            <EditField
              label="Username"
              value={form.username}
              onChange={(v) => handleChange("username", v)}
            />
            <SelectField
              label="Access Level"
              value={form.level_access}
              onChange={(v) => handleChange("level_access", v)}
              options={[
                { value: "1", label: "1 — Amateur" },
                { value: "2", label: "2 — Scientist" },
                { value: "3", label: "3 — Data Analyst" },
                { value: "4", label: "4 — Administrator" },
              ]}
            />
            <SelectField
              label="User Type"
              value={form.user_type}
              onChange={(v) => handleChange("user_type", v)}
              options={[
                { value: "Amateur", label: "Amateur" },
                { value: "Scientist", label: "Scientist" },
                { value: "Data Analyst", label: "Data Analyst" },
                { value: "Administrator", label: "Administrator" },
              ]}
            />
          </div>
        </div>

        {/* Footer */}
        <div className={styles.modalFooter}>
          <button className={styles.cancelButton} onClick={onClose}>
            Cancel
          </button>
          <button
            className={styles.saveButton}
            onClick={handleSave}
            disabled={saving}
          >
            <SaveIcon sx={{ fontSize: 16 }} />
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
