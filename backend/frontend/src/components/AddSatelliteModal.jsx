// react imports
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";

// icon imports
import CloseIcon from "@mui/icons-material/Close";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SaveIcon from "@mui/icons-material/Save";
import CheckIcon from "@mui/icons-material/Check";

// style imports
import styles from "../styles/AddSatelliteModal.module.css";

// Step Indicator
const STEPS = [
  { number: 1, label: "Dataset" },
  { number: 2, label: "Satellite" },
  { number: 3, label: "Details" },
];

function StepBar({ currentStep }) {
  return (
    <div className={styles.stepBar}>
      {STEPS.map((step, index) => {
        const isDone = currentStep > step.number;
        const isActive = currentStep === step.number;
        return (
          <React.Fragment key={step.number}>
            <div className={styles.step}>
              <div
                className={`
                ${styles.stepCircle}
                ${isActive ? styles.stepCircleActive : ""}
                ${isDone ? styles.stepCircleDone : ""}
              `}
              >
                {isDone ? <CheckIcon sx={{ fontSize: 14 }} /> : step.number}
              </div>
              <span
                className={`
                ${styles.stepLabel}
                ${isActive ? styles.stepLabelActive : ""}
                ${isDone ? styles.stepLabelDone : ""}
              `}
              >
                {step.label}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div
                className={`
                ${styles.stepConnector}
                ${isDone ? styles.stepConnectorDone : ""}
              `}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

// Step 1: Dataset Selection
function StepDataset({ datasets, selectedDataset, onSelect }) {
  return (
    <div>
      <h3 className={styles.stepTitle}>Select a Dataset</h3>
      <p className={styles.stepSubtitle}>
        Choose the dataset to import a new satellite from.
      </p>
      {datasets.length === 0 ? (
        <div className={styles.emptyState}>No datasets available</div>
      ) : (
        <div className={styles.selectList}>
          {datasets.map((ds) => (
            <button
              key={ds.dataset_id}
              className={`${styles.selectItem} ${selectedDataset?.dataset_id === ds.dataset_id ? styles.selectItemActive : ""}`}
              onClick={() => onSelect(ds)}
            >
              <div>
                <div className={styles.selectItemName}>{ds.name}</div>
                <div className={styles.selectItemMeta}>{ds.description}</div>
              </div>
              <span className={styles.selectItemBadge}>{ds.source}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Step 2: Satellite Selection
function StepSatellite({ satellites, loading, selectedSatellite, onSelect }) {
  if (loading) {
    return <div className={styles.emptyState}>Loading satellites...</div>;
  }

  return (
    <div>
      <h3 className={styles.stepTitle}>Select a Satellite</h3>
      <p className={styles.stepSubtitle}>
        These satellites are in the dataset but not yet in the database.
      </p>
      {satellites.length === 0 ? (
        <div className={styles.emptyState}>
          All satellites in this dataset are already in the database
        </div>
      ) : (
        <div className={styles.selectList}>
          {satellites.map((sat) => (
            <button
              key={sat.norad_id}
              className={`${styles.selectItem} ${selectedSatellite?.norad_id === sat.norad_id ? styles.selectItemActive : ""}`}
              onClick={() => onSelect(sat)}
            >
              <div>
                <div className={styles.selectItemName}>{sat.name}</div>
                <div className={styles.selectItemMeta}>
                  NORAD {sat.norad_id} · {sat.object_id}
                </div>
              </div>
              <span className={styles.selectItemBadge}>
                {sat.orbit_type ?? "LEO"}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Step 3: Details Form (placeholder for now)
function StepDetails({ formData, setFormData, selectedSatellite }) {
  return (
    <div>
      <h3 className={styles.stepTitle}>Fill In Details</h3>
      <p className={styles.stepSubtitle}>
        Complete the satellite information before saving.
      </p>
      {/* Tabs and form fields will be built out next */}
      <div className={styles.emptyState}>
        Form fields coming next — selected: {selectedSatellite?.name}
      </div>
    </div>
  );
}

// Main Modal
export default function AddSatelliteModal({
  data: datasets = [],
  onClose,
  onSave,
}) {
  const [step, setStep] = useState(1);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [satellites, setSatellites] = useState([]);
  const [satLoading, setSatLoading] = useState(false);
  const [selectedSatellite, setSelectedSatellite] = useState(null);
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState([]);
  const [isSaving, setIsSaving] = useState(false);

  // Fetch new satellites when dataset is selected and user moves to step 2
  const loadSatellitesForDataset = async (dataset) => {
    setSatLoading(true);
    setSatellites([]);
    setSelectedSatellite(null);
    try {
      // API call will be wired in next step
      // const data = await getNewSatellitesFromDataset(dataset.dataset_id);
      // setSatellites(data);
      setSatellites([]); // placeholder
    } catch (err) {
      console.error("Failed to load satellites:", err);
    } finally {
      setSatLoading(false);
    }
  };

  // Handle next button
  const handleNext = async () => {
    setErrors([]);
    if (step === 1) {
      if (!selectedDataset) {
        setErrors(["Please select a dataset to continue."]);
        return;
      }
      await loadSatellitesForDataset(selectedDataset);
      setStep(2);
    } else if (step === 2) {
      if (!selectedSatellite) {
        setErrors(["Please select a satellite to continue."]);
        return;
      }
      setStep(3);
    }
  };

  // Handle back button
  const handleBack = () => {
    setErrors([]);
    setStep((prev) => prev - 1);
  };

  // Handle save
  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave({ satellite: selectedSatellite, ...formData });
      onClose();
    } catch (err) {
      console.error("Failed to save:", err);
      setErrors(["Failed to add satellite. Please try again."]);
    } finally {
      setIsSaving(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <StepDataset
            datasets={datasets}
            selectedDataset={selectedDataset}
            onSelect={setSelectedDataset}
          />
        );
      case 2:
        return (
          <StepSatellite
            satellites={satellites}
            loading={satLoading}
            selectedSatellite={selectedSatellite}
            onSelect={setSelectedSatellite}
          />
        );
      case 3:
        return (
          <StepDetails
            formData={formData}
            setFormData={setFormData}
            selectedSatellite={selectedSatellite}
          />
        );
      default:
        return null;
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
          <span className={styles.modalTitle}>Add Satellite</span>
          <button className={styles.closeButton} onClick={onClose}>
            <CloseIcon sx={{ fontSize: 18 }} />
          </button>
        </div>

        {/* Step Bar */}
        <StepBar currentStep={step} />

        {/* Step Content */}
        <div className={styles.stepContent}>{renderStep()}</div>

        {/* Errors */}
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
          {step > 1 ? (
            <button className={styles.backButton} onClick={handleBack}>
              <ArrowBackIcon sx={{ fontSize: 16 }} />
              Back
            </button>
          ) : (
            <button className={styles.cancelButton} onClick={onClose}>
              Cancel
            </button>
          )}

          {step < 3 ? (
            <button
              className={styles.nextButton}
              onClick={handleNext}
              disabled={step === 1 ? !selectedDataset : !selectedSatellite}
            >
              Next
              <ArrowForwardIcon sx={{ fontSize: 16 }} />
            </button>
          ) : (
            <button
              className={styles.saveButton}
              onClick={handleSave}
              disabled={isSaving}
            >
              <SaveIcon sx={{ fontSize: 16 }} />
              {isSaving ? "Saving..." : "Add Satellite"}
            </button>
          )}
        </div>
      </div>
    </div>,
    document.body,
  );
}
