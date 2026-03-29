// react imports
import React, { useEffect, useState } from "react";

// icon imports
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";

// component imports
import SatelliteProfileModal from "../components/SatelliteProfileModal";
import AddSatelliteModal from "../components/AddSatelliteModal";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal";
import PopupMessage from "../components/PopupMessage";

// hooks
import usePopupMessage from "../hooks/usePopupMessage";

// api imports
import {
  getAllSatellites,
  getSatelliteProfile,
  deleteSatellite,
  modifySatellite,
} from "../api/satelliteService";

import { getAllDatasets } from "../api/datasetService";

// style imports
import styles from "../styles/ManageSatellites.module.css";

// subclass filters array
const SUBCLASS_FILTERS = [
  { value: "all", label: "All Types" },
  { value: "Earth Science", label: "Earth Science" },
  { value: "Oceanic Science", label: "Oceanic Science" },
  { value: "Weather", label: "Weather" },
  { value: "Navigation", label: "Navigation" },
  { value: "Internet", label: "Internet" },
  { value: "Research", label: "Research" },
];

export default function ManageSatellites() {
  const [satellites, setSatellites] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [profileData, setProfileData] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const { message, messageFading, messageVisible, showPopupMessage } =
    usePopupMessage();

  // Load satellite list on mount
  useEffect(() => {
    getAllSatellites()
      .then((data) => setSatellites(data))
      .catch((err) => console.error("Failed to load satellites:", err))
      .finally(() => setLoading(false));
  }, []);

  // load datasets list on mount
  useEffect(() => {
    getAllDatasets()
      .then((data) => setDatasets(data))
      .catch((err) => console.error("Failed to load datasets:", err))
      .finally(() => setLoading(false));
  }, []);

  console.log(datasets);

  // filter satellites by subclass type
  const filtered =
    filter === "all"
      ? satellites
      : satellites.filter((s) => s.satellite_type === filter);
  // handle edit click
  const handleEditClick = async (satelliteID) => {
    setProfileLoading(true);
    try {
      const data = await getSatelliteProfile(satelliteID);
      setProfileData(data);
    } catch (err) {
      console.error("Failed to load satellite profile:", err);
    } finally {
      setProfileLoading(false);
    }
  };

  // handle delete satellite
  const handleDeleteConfirm = async () => {
    if (!deleteTarget) {
      return;
    }
    try {
      await deleteSatellite(deleteTarget.satellite_id);
      setSatellites((prev) =>
        prev.filter((s) => s.satellite_id !== deleteTarget.satellite_id),
      );
      setDeleteTarget(null);
      showPopupMessage("Satellite deleted successfully");
    } catch (err) {
      console.error("Failed to delete satellite:", err);
      showPopupMessage("Failed to delete satellite", "error");
    }
  };

  return (
    <div className={styles.page}>
      {/* Page Header */}
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.pageTitle}>Manage Satellites</h2>
          <p className={styles.pageSubtitle}>
            View, manage and remove satellites
          </p>
        </div>
        <button
          className={styles.addButton}
          onClick={() => setShowAddModal(true)}
        >
          <AddIcon sx={{ fontSize: 18 }} />
          Add Satellite
        </button>
      </div>

      {/* Filter Bar */}
      <div className={styles.filterBar}>
        <span className={styles.filterLabel}>Filter by type:</span>
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

      {/* Satellite List */}
      <div className={styles.listCard}>
        {/* List Header */}
        <div className={styles.listHeader}>
          <span className={styles.listHeaderCell}>Name</span>
          <span className={styles.listHeaderCell}>Type</span>
          <span className={styles.listHeaderCell}>Orbit</span>
          <span className={styles.listHeaderCell}>NORAD ID</span>
          <span className={styles.listHeaderCell}></span>
          <span className={styles.listHeaderCell}></span>
        </div>

        {/* List Body */}
        <div className={styles.listBody}>
          {loading ? (
            <div className={styles.emptyState}>Loading satellites...</div>
          ) : filtered.length === 0 ? (
            <div className={styles.emptyState}>No satellites found</div>
          ) : (
            filtered.map((sat) => (
              <div key={sat.satellite_id} className={styles.listRow}>
                <div className={styles.listRowName}>
                  <div className={styles.listDot} />
                  {sat.name} - {sat.object_id}
                </div>
                <div className={styles.listCell}>
                  <span className={styles.typeBadge}>
                    {sat.satellite_type ?? "Unknown"}
                  </span>
                </div>
                <div className={styles.listCell}>{sat.orbit_type}</div>
                <div className={styles.listCell}>{sat.norad_id}</div>
                <button
                  className={styles.deleteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEditClick(sat.satellite_id);
                  }}
                >
                  <EditIcon sx={{ fontSize: 18 }} />
                </button>
                <button
                  className={styles.deleteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteTarget(sat);
                  }}
                >
                  <DeleteOutlineIcon sx={{ fontSize: 18 }} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add Satellite Modal */}
      {showAddModal && (
        <AddSatelliteModal
          data={datasets}
          onClose={() => setShowAddModal(false)}
          onSave={async (payload) => {
            console.log(payload);
            showPopupMessage("New satellite successfully added");
          }}
        />
      )}

      {/* Profile Modal */}
      {profileData && (
        <SatelliteProfileModal
          data={profileData}
          onClose={() => setProfileData(null)}
          onSave={async (payload) => {
            modifySatellite(payload);
            showPopupMessage("Satellite updated sucessfully");
          }}
        />
      )}

      {/* Confirm Delete Modal */}
      {deleteTarget && (
        <ConfirmDeleteModal
          satellite={deleteTarget}
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
