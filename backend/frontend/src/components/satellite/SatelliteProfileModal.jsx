// react imports
import React, { useState } from "react";
import ReactDOM from "react-dom";

// icon imports
import CloseIcon from "@mui/icons-material/Close";
import SaveIcon from "@mui/icons-material/Save";

// style imports
import styles from "../../styles/satellite/SatelliteProfileModal.module.css";

// tab config
const TABS = [
  { id: "info", label: "Satellite Info" },
  { id: "owner", label: "Owner" },
  { id: "launch", label: "Launch & Site" },
  { id: "comms", label: "Communication" },
  { id: "type", label: "Instrument Data" },
];

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

// satellite info tab
function TabInfo({ editData, handleChange }) {
  const s = editData.satellite || {};
  return (
    <div className={styles.fieldGrid}>
      <Field label="Name" value={s.name} />
      <Field label="NORAD ID" value={s.norad_id} />
      <Field label="Object ID" value={s.object_id} />
      <Field label="Orbit Type" value={s.orbit_type} />
      <Field label="Satellite Type" value={s.satellite_type} />
      <Field label="Dataset ID" value={s.dataset_id} />
      <Field label="Last Contact" value={s.last_contact_time} />
      <SelectField
        label="Classification"
        value={s.classification}
        onChange={(v) => handleChange("satellite", "classification", v)}
        options={[
          { value: "U", label: "U — Unclassified" },
          { value: "C", label: "C — Classified" },
          { value: "S", label: "S — Secret" },
        ]}
      />
      <EditField
        label="Description"
        value={s.description}
        onChange={(v) => handleChange("satellite", "description", v)}
        full
      />
    </div>
  );
}

// owner tab
function TabOwner({ editData }) {
  const o = editData.owner || {};
  return (
    <div className={styles.fieldGrid}>
      <Field label="Owner Name" value={o.owner_name} />
      <Field label="Operator" value={o.operator} />
      <Field label="Owner Type" value={o.owner_type} />
      <Field label="Country" value={o.country} />
      <Field label="Phone" value={o.owner_phone} />
      <Field label="Address" value={o.owner_address} full />
    </div>
  );
}

// launch tab
function TabLaunch({ editData }) {
  const l = editData.launch || {};
  const ls = editData.launch_site || {};
  return (
    <div className={styles.fieldGrid}>
      <Field
        label="Deploy Date"
        value={
          l.deploy_date_time
            ? new Date(l.deploy_date_time).toLocaleDateString()
            : null
        }
      />
      <Field label="Vehicle" value={l.vehicle_name} />
      <Field label="Manufacturer" value={l.manufacturer} />
      <Field label="Reusable" value={l.reusable ? "Yes" : "No"} />
      <Field label="Payload Capacity" value={l.payload_capacity} />
      <Field label="Launch Site" value={ls.site_name} />
      <Field label="Location" value={ls.location} />
      <Field label="Climate" value={ls.climate} />
      <Field label="Site Country" value={ls.site_country} />
    </div>
  );
}

// communication tab
function TabComms({ editData, handleChange }) {
  const c = editData.communication || {};
  return (
    <div className={styles.fieldGrid}>
      <Field label="Station Name" value={c.station_name} />
      <Field label="Location" value={c.station_location} />
      <EditField
        label="Frequency"
        value={c.communication_frequency}
        onChange={(v) =>
          handleChange("communication", "communication_frequency", v)
        }
      />
    </div>
  );
}

// Fields that are physical hardware properties
const READ_ONLY_TYPE_FIELDS = new Set([
  "instrument",
  "data_measured",
  "wavelength_band",
  "resolution_m",
  "frequency_band",
  "constellation",
  "signal_type",
  "clock_type",
  "imaging_channels",
  "altitude_km",
]);

// type tab
function TabType({ editData, handleChange }) {
  const t = editData.type_data || {};

  if (Object.keys(t).length === 0) {
    return (
      <div style={{ color: "#475569", fontSize: "0.875rem" }}>
        No instrument data available.
      </div>
    );
  }

  return (
    <div className={styles.fieldGrid}>
      {Object.entries(t).map(([key, value]) => {
        const label = key.replace(/_/g, " ");
        if (READ_ONLY_TYPE_FIELDS.has(key)) {
          return (
            <Field
              key={key}
              label={label}
              value={value !== null ? String(value) : null}
            />
          );
        }
        return (
          <EditField
            key={key}
            label={label}
            value={value !== null ? String(value) : ""}
            onChange={(v) => handleChange("type_data", key, v)}
          />
        );
      })}
    </div>
  );
}

// form validation
function validate(editData) {
  const errors = [];
  const s = editData.satellite || {};
  const t = editData.type_data || {};

  if (!s.classification) {
    errors.push("Classification is required.");
  }

  ["throughput_gbps", "accuracy_m", "repeat_cycle_min"].forEach((field) => {
    if (t[field] !== undefined && t[field] !== "" && isNaN(Number(t[field]))) {
      errors.push(`${field.replace(/_/g, " ")} must be a number.`);
    }
  });

  if (t.data_archive_url && !String(t.data_archive_url).startsWith("http")) {
    errors.push("Archive URL must start with http.");
  }

  return errors;
}

// modal component
export default function SatelliteProfileModal({ data, onClose, onSave }) {
  // functions and variables
  const [activeTab, setActiveTab] = useState("info");
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState([]);

  // edito data which is all the data returned from the profile endpoint
  const [editData, setEditData] = useState({
    satellite: { ...(data.satellite || {}) },
    owner: { ...(data.owner || {}) },
    launch: { ...(data.launch || {}) },
    launch_site: { ...(data.launch_site || {}) },
    communication: { ...(data.communication || {}) },
    type_data: { ...(data.type_data || {}) },
  });

  // Single update handler for all sections
  const handleChange = (section, field, value) => {
    setEditData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  // Validate then build payload and save
  const handleOnSave = async () => {
    const validationErrors = validate(editData);
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }
    setErrors([]);
    setIsSaving(true);
    try {
      const payload = {
        satellite: {
          satellite_id: editData.satellite.satellite_id,
          description: editData.satellite.description,
          classification: editData.satellite.classification,
        },
        communication: {
          communication_frequency:
            editData.communication.communication_frequency,
        },
        type_data: editData.type_data,
      };
      if (onSave) await onSave(payload);
      onClose();
    } catch (err) {
      console.error("Failed to save:", err);
      setErrors(["Failed to save changes. Please try again."]);
    } finally {
      setIsSaving(false);
    }
  };

  // render the current active tab
  const renderTab = () => {
    switch (activeTab) {
      case "info":
        return <TabInfo editData={editData} handleChange={handleChange} />;
      case "owner":
        return <TabOwner editData={editData} />;
      case "launch":
        return <TabLaunch editData={editData} />;
      case "comms":
        return <TabComms editData={editData} handleChange={handleChange} />;
      case "type":
        return <TabType editData={editData} handleChange={handleChange} />;
      default:
        return <TabInfo editData={editData} handleChange={handleChange} />;
    }
  };

  // create the satellite array from the edit data
  const satellite = editData.satellite || {};

  // create the react dom modal
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
            <div className={styles.modalTitle}>{satellite.name}</div>
            <div className={styles.modalSubtitle}>
              {satellite.satellite_type} · {satellite.orbit_type} · NORAD{" "}
              {satellite.norad_id}
            </div>
          </div>
          <button className={styles.closeButton} onClick={onClose}>
            <CloseIcon sx={{ fontSize: 18 }} />
          </button>
        </div>

        {/* Tabs */}
        <div className={styles.tabs}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`${styles.tab} ${activeTab === tab.id ? styles.tabActive : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className={styles.tabContent}>{renderTab()}</div>

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
            onClick={handleOnSave}
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
