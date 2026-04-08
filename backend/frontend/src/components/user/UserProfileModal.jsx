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

export default function UserProfileModal({ data, onClose, onSave }) {
  const [form, setForm] = useState({
    username: data.username ?? "",
    level_access: String(data.level_access ?? "1"),
    user_type: data.user_type ?? "Amateur",
  });
  // subtype fields — pre-populated from existing data
  const [subtypeForm, setSubtypeForm] = useState({
    employee_id: data.subtype_data?.employee_id ?? "",
    profession: data.subtype_data?.profession ?? "",
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleTypeChange = (value) => {
    // reset subtype fields when switching type
    setForm((prev) => ({ ...prev, user_type: value }));
    setSubtypeForm({ employee_id: "", profession: "" });
  };

  const buildSubtypeData = () => {
    if (form.user_type === "Administrator" || form.user_type === "Data Analyst") {
      return { employee_id: parseInt(subtypeForm.employee_id) || 0 };
    }
    if (form.user_type === "Scientist") {
      return { profession: subtypeForm.profession };
    }
    return {};
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({
        ...form,
        original_username: data.username,
        subtype_data: buildSubtypeData(),
      });
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
              onChange={handleTypeChange}
              options={[
                { value: "Amateur", label: "Amateur" },
                { value: "Scientist", label: "Scientist" },
                { value: "Data Analyst", label: "Data Analyst" },
                { value: "Administrator", label: "Administrator" },
              ]}
            />
            {(form.user_type === "Administrator" ||
              form.user_type === "Data Analyst") && (
              <EditField
                label="Employee ID"
                value={subtypeForm.employee_id}
                onChange={(v) =>
                  setSubtypeForm((prev) => ({ ...prev, employee_id: v }))
                }
                type="number"
              />
            )}
            {form.user_type === "Scientist" && (
              <EditField
                label="Profession"
                value={subtypeForm.profession}
                onChange={(v) =>
                  setSubtypeForm((prev) => ({ ...prev, profession: v }))
                }
              />
            )}
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
