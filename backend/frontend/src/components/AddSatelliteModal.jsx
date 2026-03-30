// react imports
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";

// icon imports
import CloseIcon from "@mui/icons-material/Close";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SaveIcon from "@mui/icons-material/Save";
import CheckIcon from "@mui/icons-material/Check";

// api imports
import { getNewSatellitesFromDataset } from "../api/manageSatellitesService";
import {
  getAllOwners,
  getAllVehicles,
  getAllLaunchSites,
  getAllStations,
} from "../api/lookupsService";

// style imports
import styles from "../styles/AddSatelliteModal.module.css";

// Constants
const STEPS = [
  { number: 1, label: "Dataset" },
  { number: 2, label: "Satellite" },
  { number: 3, label: "Details" },
];

// tabs
const DETAIL_TABS = [
  { id: "info", label: "Satellite Info" },
  { id: "owner", label: "Owner" },
  { id: "launch", label: "Launch & Site" },
  { id: "comms", label: "Communication" },
  { id: "type", label: "Type Data" },
];

// subclass tabs
const SUBCLASS_TYPES = [
  "Earth Science",
  "Oceanic Science",
  "Weather",
  "Navigation",
  "Internet",
  "Research",
];

// type fields for each subclass
const TYPE_FIELDS = {
  "Earth Science": [
    "instrument",
    "data_measured",
    "wavelength_band",
    "resolution_m",
    "data_archive_url",
    "mission_status",
  ],
  "Oceanic Science": [
    "instrument",
    "data_measured",
    "wavelength_band",
    "resolution_m",
    "data_archive_url",
    "mission_status",
  ],
  Weather: [
    "instrument",
    "data_measured",
    "coverage_region",
    "imaging_channels",
    "repeat_cycle_min",
    "data_archive_url",
    "mission_status",
  ],
  Navigation: [
    "constellation",
    "signal_type",
    "accuracy_m",
    "orbital_slot",
    "clock_type",
  ],
  Internet: [
    "coverage",
    "frequency_band",
    "service_type",
    "throughput_gbps",
    "altitude_km",
  ],
  Research: [
    "instrument",
    "data_measured",
    "research_field",
    "wavelength_band",
    "data_archive_url",
    "mission_status",
  ],
};

// Field Components
function Field({ label, value, full }) {
  return (
    <div className={`${styles.field} ${full ? styles.fieldFull : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <span className={styles.fieldValue}>{value ?? "—"}</span>
    </div>
  );
}

// edit field function for editable fields while adding new satellite
function EditField({
  label,
  value,
  onChange,
  full,
  type = "text",
  placeholder,
}) {
  return (
    <div className={`${styles.field} ${full ? styles.fieldFull : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <input
        type={type}
        className={styles.fieldInput}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}

// select field function for when a field is selected
function SelectField({ label, value, onChange, options, full, placeholder }) {
  return (
    <div className={`${styles.field} ${full ? styles.fieldFull : ""}`}>
      <span className={styles.fieldLabel}>{label}</span>
      <select
        className={styles.fieldInput}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">{placeholder || "Select..."}</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

// Select or Create Component
function SelectOrCreate({
  label,
  items,
  selectedId,
  onSelectId,
  isNew,
  onToggleNew,
  renderFields,
  displayKey,
  valueKey,
}) {
  return (
    <div>
      <div className={styles.toggleRow}>
        <button
          className={`${styles.toggleButton} ${!isNew ? styles.toggleButtonActive : ""}`}
          onClick={() => onToggleNew(false)}
        >
          Use Existing
        </button>
        <button
          className={`${styles.toggleButton} ${isNew ? styles.toggleButtonActive : ""}`}
          onClick={() => onToggleNew(true)}
        >
          + Create New
        </button>
      </div>

      {!isNew ? (
        <div className={styles.field}>
          <span className={styles.fieldLabel}>{label}</span>
          <select
            className={styles.fieldInput}
            value={selectedId ?? ""}
            onChange={(e) => onSelectId(e.target.value)}
          >
            <option value="">Select {label}...</option>
            {items.map((item) => (
              <option key={item[valueKey]} value={item[valueKey]}>
                {item[displayKey]}
              </option>
            ))}
          </select>
        </div>
      ) : (
        renderFields()
      )}
    </div>
  );
}

// Step Bar at the top of our modal
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
                className={`${styles.stepCircle} ${isActive ? styles.stepCircleActive : ""} ${isDone ? styles.stepCircleDone : ""}`}
              >
                {isDone ? <CheckIcon sx={{ fontSize: 14 }} /> : step.number}
              </div>
              <span
                className={`${styles.stepLabel} ${isActive ? styles.stepLabelActive : ""} ${isDone ? styles.stepLabelDone : ""}`}
              >
                {step.label}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div
                className={`${styles.stepConnector} ${isDone ? styles.stepConnectorDone : ""}`}
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
function StepSatellite({
  satellites,
  loading,
  selectedSatellite,
  onSelect,
  search,
  onSearch,
  page,
  pages,
  total,
  onPageChange,
}) {
  return (
    <div>
      <h3 className={styles.stepTitle}>Select a Satellite</h3>
      <p className={styles.stepSubtitle}>
        Showing satellites in this dataset not yet in the database.
      </p>
      <input
        className={styles.searchInput}
        type="text"
        placeholder="Search by name or NORAD ID..."
        value={search}
        onChange={(e) => onSearch(e.target.value)}
      />
      {loading ? (
        <div className={styles.emptyState}>Loading satellites...</div>
      ) : satellites.length === 0 ? (
        <div className={styles.emptyState}>
          {search
            ? "No satellites match your search"
            : "All satellites in this dataset are already in the database"}
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
              <span className={styles.selectItemBadge}>{sat.orbit_type}</span>
            </button>
          ))}
        </div>
      )}
      {!loading && total > 0 && (
        <div className={styles.pagination}>
          <button
            className={styles.pageButton}
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
          >
            ‹
          </button>
          <span className={styles.pageInfo}>
            Page {page} of {pages} · {total} satellites
          </span>
          <button
            className={styles.pageButton}
            onClick={() => onPageChange(page + 1)}
            disabled={page >= pages}
          >
            ›
          </button>
        </div>
      )}
    </div>
  );
}

// Step 3: Details Form
function StepDetails({
  formData,
  onChange,
  selectedSatellite,
  selectedDataset,
  lookups,
}) {
  const [activeTab, setActiveTab] = useState("info");

  const renderTab = () => {
    switch (activeTab) {
      case "info":
        return (
          <TabInfo
            formData={formData}
            onChange={onChange}
            satellite={selectedSatellite}
          />
        );
      case "owner":
        return (
          <TabOwner
            formData={formData}
            onChange={onChange}
            owners={lookups.owners}
          />
        );
      case "launch":
        return (
          <TabLaunch
            formData={formData}
            onChange={onChange}
            vehicles={lookups.vehicles}
            sites={lookups.sites}
          />
        );
      case "comms":
        return (
          <TabComms
            formData={formData}
            onChange={onChange}
            stations={lookups.stations}
          />
        );
      case "type":
        return <TabType formData={formData} onChange={onChange} />;
      default:
        return null;
    }
  };

  return (
    <div>
      <h3 className={styles.stepTitle}>Satellite Details</h3>
      <p className={styles.stepSubtitle}>
        Fill in all required information before saving.
      </p>
      <div className={styles.tabs}>
        {DETAIL_TABS.map((tab) => (
          <button
            key={tab.id}
            className={`${styles.tab} ${activeTab === tab.id ? styles.tabActive : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {renderTab()}
    </div>
  );
}

// Tab: Satellite Info
function TabInfo({ formData, onChange, satellite }) {
  return (
    <div className={styles.fieldGrid}>
      <Field label="Name" value={satellite?.name} />
      <Field label="NORAD ID" value={satellite?.norad_id} />
      <Field label="Object ID" value={satellite?.object_id} />
      <SelectField
        label="Orbit Type"
        value={formData.satellite?.orbit_type}
        onChange={(v) => onChange("satellite", "orbit_type", v)}
        options={[
          { value: "LEO", label: "LEO — Low Earth Orbit" },
          { value: "MEO", label: "MEO — Medium Earth Orbit" },
          { value: "GEO", label: "GEO — Geostationary Orbit" },
          { value: "HEO", label: "HEO — Highly Elliptical Orbit" },
        ]}
      />
      <SelectField
        label="Classification"
        value={formData.satellite?.classification}
        onChange={(v) => onChange("satellite", "classification", v)}
        options={[
          { value: "U", label: "U — Unclassified" },
          { value: "C", label: "C — Classified" },
          { value: "S", label: "S — Secret" },
        ]}
      />
      <EditField
        label="Description"
        value={formData.satellite?.description}
        onChange={(v) => onChange("satellite", "description", v)}
        placeholder="Enter satellite description..."
        full
      />
    </div>
  );
}

// Tab: Owner
function TabOwner({ formData, onChange, owners }) {
  const isNew = formData.owner?.isNew || false;
  return (
    <div>
      <SelectOrCreate
        label="Owner"
        items={owners}
        selectedId={formData.owner?.owner_id}
        onSelectId={(v) => onChange("owner", "owner_id", v)}
        isNew={isNew}
        onToggleNew={(v) => onChange("owner", "isNew", v)}
        displayKey="owner_name"
        valueKey="owner_id"
        renderFields={() => (
          <div className={styles.fieldGrid}>
            <EditField
              label="Owner Name"
              value={formData.owner?.owner_name}
              onChange={(v) => onChange("owner", "owner_name", v)}
            />
            <EditField
              label="Country"
              value={formData.owner?.country}
              onChange={(v) => onChange("owner", "country", v)}
            />
            <EditField
              label="Operator"
              value={formData.owner?.operator}
              onChange={(v) => onChange("owner", "operator", v)}
            />
            <SelectField
              label="Owner Type"
              value={formData.owner?.owner_type}
              onChange={(v) => onChange("owner", "owner_type", v)}
              options={[
                { value: "government", label: "Government" },
                { value: "commercial", label: "Commercial" },
                { value: "military", label: "Military" },
                { value: "academic", label: "Academic" },
              ]}
            />
            <EditField
              label="Phone"
              value={formData.owner?.owner_phone}
              onChange={(v) => onChange("owner", "owner_phone", v)}
            />
            <EditField
              label="Address"
              value={formData.owner?.owner_address}
              onChange={(v) => onChange("owner", "owner_address", v)}
              full
            />
          </div>
        )}
      />
    </div>
  );
}

// Tab: Launch & Site
function TabLaunch({ formData, onChange, vehicles, sites }) {
  const vehicleIsNew = formData.launch?.vehicleIsNew || false;
  const siteIsNew = formData.launch?.siteIsNew || false;
  return (
    <div>
      {/* Deploy Date */}
      <div className={styles.fieldGrid} style={{ marginBottom: "1.5rem" }}>
        <EditField
          label="Deploy Date"
          type="date"
          value={formData.launch?.deploy_date_time}
          onChange={(v) => onChange("launch", "deploy_date_time", v)}
        />
      </div>

      {/* Vehicle */}
      <p className={styles.sectionDivider}>Launch Vehicle</p>
      <SelectOrCreate
        label="Vehicle"
        items={vehicles}
        selectedId={formData.launch?.vehicle_id}
        onSelectId={(v) => onChange("launch", "vehicle_id", v)}
        isNew={vehicleIsNew}
        onToggleNew={(v) => onChange("launch", "vehicleIsNew", v)}
        displayKey="vehicle_name"
        valueKey="vehicle_id"
        renderFields={() => (
          <div className={styles.fieldGrid}>
            <EditField
              label="Vehicle Name"
              value={formData.launch?.vehicle_name}
              onChange={(v) => onChange("launch", "vehicle_name", v)}
            />
            <EditField
              label="Manufacturer"
              value={formData.launch?.manufacturer}
              onChange={(v) => onChange("launch", "manufacturer", v)}
            />
            <EditField
              label="Country"
              value={formData.launch?.vehicle_country}
              onChange={(v) => onChange("launch", "vehicle_country", v)}
            />
            <EditField
              label="Payload Capacity"
              value={formData.launch?.payload_capacity}
              onChange={(v) => onChange("launch", "payload_capacity", v)}
            />
            <SelectField
              label="Reusable"
              value={formData.launch?.reusable}
              onChange={(v) => onChange("launch", "reusable", v)}
              options={[
                { value: "1", label: "Yes" },
                { value: "0", label: "No" },
              ]}
            />
          </div>
        )}
      />

      {/* Launch Site */}
      <p className={styles.sectionDivider}>Launch Site</p>
      <SelectOrCreate
        label="Launch Site"
        items={sites}
        selectedId={formData.launch?.site_name}
        onSelectId={(v) => onChange("launch", "site_name", v)}
        isNew={siteIsNew}
        onToggleNew={(v) => onChange("launch", "siteIsNew", v)}
        displayKey="site_name"
        valueKey="site_name"
        renderFields={() => (
          <div className={styles.fieldGrid}>
            <EditField
              label="Site Name"
              value={formData.launch?.site_name}
              onChange={(v) => onChange("launch", "site_name", v)}
            />
            <EditField
              label="Location"
              value={formData.launch?.site_location}
              onChange={(v) => onChange("launch", "site_location", v)}
            />
            <EditField
              label="Climate"
              value={formData.launch?.site_climate}
              onChange={(v) => onChange("launch", "site_climate", v)}
            />
            <EditField
              label="Country"
              value={formData.launch?.site_country}
              onChange={(v) => onChange("launch", "site_country", v)}
            />
          </div>
        )}
      />
    </div>
  );
}

// Tab: Communication
function TabComms({ formData, onChange, stations }) {
  const isNew = formData.communication?.stationIsNew || false;
  return (
    <div>
      <SelectOrCreate
        label="Communication Station"
        items={stations}
        selectedId={formData.communication?.station_location}
        onSelectId={(v) => onChange("communication", "station_location", v)}
        isNew={isNew}
        onToggleNew={(v) => onChange("communication", "stationIsNew", v)}
        displayKey="name"
        valueKey="location"
        renderFields={() => (
          <div className={styles.fieldGrid}>
            <EditField
              label="Station Name"
              value={formData.communication?.station_name}
              onChange={(v) => onChange("communication", "station_name", v)}
            />
            <EditField
              label="Location"
              value={formData.communication?.station_location}
              onChange={(v) => onChange("communication", "station_location", v)}
            />
          </div>
        )}
      />
      <div className={styles.fieldGrid} style={{ marginTop: "1rem" }}>
        <EditField
          label="Communication Frequency"
          value={formData.communication?.communication_frequency}
          onChange={(v) =>
            onChange("communication", "communication_frequency", v)
          }
          placeholder="e.g. Continuous, Once per orbit..."
          full
        />
      </div>
    </div>
  );
}

// Tab: Type Data
function TabType({ formData, onChange }) {
  const selectedType = formData.type?.subclass || null;
  const fields = selectedType ? TYPE_FIELDS[selectedType] || [] : [];

  return (
    <div>
      {/* Subclass selector */}
      <span className={styles.fieldLabel}>Satellite Type</span>
      <div className={styles.typeSelectGrid}>
        {SUBCLASS_TYPES.map((type) => (
          <button
            key={type}
            className={`${styles.typeOption} ${selectedType === type ? styles.typeOptionActive : ""}`}
            onClick={() => onChange("type", "subclass", type)}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Type-specific fields */}
      {selectedType && (
        <div className={styles.fieldGrid}>
          {fields.map((field) => (
            <EditField
              key={field}
              label={field.replace(/_/g, " ")}
              value={formData.type?.[field]}
              onChange={(v) => onChange("type", field, v)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Main Modal
export default function AddSatelliteModal({
  data: datasets = [],
  onClose,
  onSave,
}) {
  // modal functions and variables
  const [step, setStep] = useState(1);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [satellites, setSatellites] = useState([]);
  const [satLoading, setSatLoading] = useState(false);
  const [selectedSatellite, setSelectedSatellite] = useState(null);
  const [errors, setErrors] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [search, setSearch] = useState("");
  const [satPage, setSatPage] = useState(1);
  const [satTotal, setSatTotal] = useState(0);
  const [satPages, setSatPages] = useState(1);

  // Lookup data
  const [lookups, setLookups] = useState({
    owners: [],
    vehicles: [],
    sites: [],
    stations: [],
  });

  // Form data for step 3
  const [formData, setFormData] = useState({
    satellite: {},
    owner: { isNew: false },
    launch: { vehicleIsNew: false, siteIsNew: false },
    communication: { stationIsNew: false },
    type: { subclass: null },
  });

  // Load lookup data once
  useEffect(() => {
    Promise.all([
      getAllOwners(),
      getAllVehicles(),
      getAllLaunchSites(),
      getAllStations(),
    ])
      .then(([owners, vehicles, sites, stations]) => {
        setLookups({ owners, vehicles, sites, stations });
      })
      .catch((err) => console.error("Failed to load lookups:", err));
  }, []);

  // Pre-fill satellite info when satellite is selected
  useEffect(() => {
    if (!selectedSatellite) return;
    setFormData((prev) => ({
      ...prev,
      satellite: {
        name: selectedSatellite.name,
        norad_id: selectedSatellite.norad_id,
        object_id: selectedSatellite.object_id,
        classification: selectedSatellite.classification,
        orbit_type: selectedSatellite.orbit_type,
        description: "",
        dataset_id: selectedDataset?.dataset_id,
        inclination: selectedSatellite.inclination,
        eccentricity: selectedSatellite.eccentricity,
        mean_motion: selectedSatellite.mean_motion,
        epoch: selectedSatellite.epoch,
        ra_of_asc_node: selectedSatellite.ra_of_asc_node,
        arg_of_pericenter: selectedSatellite.arg_of_pericenter,
        mean_anomaly: selectedSatellite.mean_anomaly,
        bstar: selectedSatellite.bstar,
      },
    }));
  }, [selectedSatellite]);

  // Debounced search
  useEffect(() => {
    if (!selectedDataset) return;
    const timeout = setTimeout(() => {
      loadSatellitesForDataset(selectedDataset, 1, search);
    }, 300);
    return () => clearTimeout(timeout);
  }, [search]);

  // Single change handler for all form sections
  const handleChange = (section, field, value) => {
    setFormData((prev) => ({
      ...prev,
      [section]: { ...prev[section], [field]: value },
    }));
  };

  // load satelites when a dataset is selected
  const loadSatellitesForDataset = async (
    dataset,
    page = 1,
    searchTerm = "",
  ) => {
    if (!dataset) return;
    setSatLoading(true);
    setSatellites([]);
    setSelectedSatellite(null);
    try {
      const data = await getNewSatellitesFromDataset(
        dataset.dataset_id,
        searchTerm,
        page,
      );
      setSatellites(data.results);
      setSatTotal(data.total);
      setSatPages(data.pages);
      setSatPage(data.page);
    } catch (err) {
      console.error("Failed to load satellites:", err);
    } finally {
      setSatLoading(false);
    }
  };

  // when next button is clicked
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

  // when back button is clicked
  const handleBack = () => {
    setErrors([]);
    setStep((prev) => prev - 1);
  };

  // Validate step 3 before saving
  const validate = () => {
    const errs = [];
    if (!formData.satellite?.orbit_type) errs.push("Orbit type is required.");
    if (!formData.satellite?.classification)
      errs.push("Classification is required.");
    if (!formData.launch?.deploy_date_time)
      errs.push("Deploy date is required.");
    if (!formData.owner?.isNew && !formData.owner?.owner_id)
      errs.push("Please select or create an owner.");
    if (!formData.launch?.vehicleIsNew && !formData.launch?.vehicle_id)
      errs.push("Please select or create a launch vehicle.");
    if (!formData.launch?.siteIsNew && !formData.launch?.site_name)
      errs.push("Please select or create a launch site.");
    if (
      !formData.communication?.stationIsNew &&
      !formData.communication?.station_location
    )
      errs.push("Please select or create a communication station.");
    if (!formData.communication?.communication_frequency)
      errs.push("Communication frequency is required.");
    if (!formData.type?.subclass) errs.push("Please select a satellite type.");
    return errs;
  };

  // save button to add satellite to database
  const handleSave = async () => {
    const errs = validate();
    if (errs.length > 0) {
      setErrors(errs);
      return;
    }
    setIsSaving(true);
    try {
      await onSave(formData);
      onClose();
    } catch (err) {
      console.error("Failed to save:", err);
      setErrors(["Failed to add satellite. Please try again."]);
    } finally {
      setIsSaving(false);
    }
  };

  // render method for all tabs and steps
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
            search={search}
            onSearch={setSearch}
            page={satPage}
            pages={satPages}
            total={satTotal}
            onPageChange={(p) => {
              setSatPage(p);
              loadSatellitesForDataset(selectedDataset, p, search);
            }}
          />
        );
      case 3:
        return (
          <StepDetails
            formData={formData}
            onChange={handleChange}
            selectedSatellite={selectedSatellite}
            selectedDataset={selectedDataset}
            lookups={lookups}
          />
        );
      default:
        return null;
    }
  };

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
              <ArrowBackIcon sx={{ fontSize: 16 }} /> Back
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
              Next <ArrowForwardIcon sx={{ fontSize: 16 }} />
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
