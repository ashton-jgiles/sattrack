// react imports
import React, { useRef, useState } from "react";
import ReactDOM from "react-dom";

// icon imports
import CloseIcon from "@mui/icons-material/Close";
import AddIcon from "@mui/icons-material/Add";

// style imports
import styles from "../styles/SatelliteProfileModal.module.css";
import dropdownStyles from "../styles/AddDatasetModal.module.css";

function EditField({ label, value, onChange, placeholder }) {
  return (
    <div className={`${styles.field} ${styles.fieldFull}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <input
        type="text"
        className={styles.fieldInput}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder ?? ""}
      />
    </div>
  );
}

export default function AddDatasetModal({ sources = [], onClose, onSave }) {
  const [form, setForm] = useState({
    group: "",
    dataset_name: "",
    description: "",
    pull_frequency: "",
  });
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState([]);
  const inputRef = useRef(null);

  const filteredSources = sources.filter((s) =>
    s.group.toLowerCase().includes(form.group.toLowerCase()),
  );

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleGroupInput = (value) => {
    setForm((prev) => ({ ...prev, group: value }));
    setDropdownOpen(true);
  };

  const handleGroupSelect = (group) => {
    const match = sources.find((s) => s.group === group);
    if (match?.previously_deleted) {
      setForm({
        group,
        dataset_name: match.dataset_name ?? "",
        description: match.description ?? "",
        pull_frequency: match.pull_frequency ?? "6h",
      });
    } else {
      const namePart = group.charAt(0).toUpperCase() + group.slice(1);
      setForm((prev) => ({
        ...prev,
        group,
        dataset_name: `CelesTrak ${namePart} Satellites`,
        description: `TLE orbital elements for ${namePart} satellites`,
        pull_frequency: "6h",
      }));
    }
    setDropdownOpen(false);
  };

  const isRestore =
    sources.find((s) => s.group === form.group)?.previously_deleted ?? false;

  const handleSave = async () => {
    const errs = [];
    if (!form.group.trim()) errs.push("Group is required.");
    if (!form.dataset_name.trim()) errs.push("Dataset name is required.");
    if (errs.length) {
      setErrors(errs);
      return;
    }

    setIsSaving(true);
    setErrors([]);
    try {
      await onSave(form);
      onClose();
    } catch (err) {
      const msg =
        err?.response?.data?.error ??
        "Failed to create dataset. Please try again.";
      setErrors([msg]);
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
            <div className={styles.modalTitle}>
              {isRestore ? "Restore Dataset" : "Add Dataset"}
            </div>
            <div className={styles.modalSubtitle}>
              {isRestore
                ? "Restore a previously deleted CelesTrak dataset"
                : "Create a new CelesTrak dataset"}
            </div>
          </div>
          <button className={styles.closeButton} onClick={onClose}>
            <CloseIcon sx={{ fontSize: 18 }} />
          </button>
        </div>

        {/* Fields */}
        <div className={styles.tabContent}>
          <div className={styles.fieldGrid}>
            {/* Group with custom dropdown */}
            <div
              className={`${styles.field} ${styles.fieldFull} ${dropdownStyles.groupWrapper}`}
            >
              <span className={styles.fieldLabel}>CelesTrak Group</span>
              <input
                ref={inputRef}
                type="text"
                className={styles.fieldInput}
                value={form.group}
                onChange={(e) => handleGroupInput(e.target.value)}
                onFocus={() => setDropdownOpen(true)}
                onBlur={() => setTimeout(() => setDropdownOpen(false), 150)}
                placeholder="e.g. starlink, weather, gps-ops"
              />
              {dropdownOpen && filteredSources.length > 0 && (
                <div className={dropdownStyles.dropdown}>
                  {filteredSources.map((s) => (
                    <div
                      key={s.group}
                      className={dropdownStyles.dropdownItem}
                      onMouseDown={() => handleGroupSelect(s.group)}
                    >
                      {s.group}
                      {s.previously_deleted && (
                        <span
                          style={{
                            marginLeft: "0.5rem",
                            fontSize: "0.7rem",
                            color: "#a78bfa",
                          }}
                        >
                          restore
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <EditField
              label="Dataset Name"
              value={form.dataset_name}
              onChange={(v) => handleChange("dataset_name", v)}
              placeholder="e.g. CelesTrak Starlink Satellites"
            />
            <EditField
              label="Pull Frequency"
              value={form.pull_frequency}
              onChange={(v) => handleChange("pull_frequency", v)}
              placeholder="e.g. 6h"
            />
            <EditField
              label="Description"
              value={form.description}
              onChange={(v) => handleChange("description", v)}
              placeholder="Optional description"
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
            <AddIcon sx={{ fontSize: 16 }} />
            {isSaving
              ? isRestore
                ? "Restoring..."
                : "Creating..."
              : isRestore
                ? "Restore Dataset"
                : "Add Dataset"}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
