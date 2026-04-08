// react imports
import React, { useEffect, useState } from "react";

// icon imports
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import RestoreIcon from "@mui/icons-material/Restore";

// component imports
import SatelliteProfileModal from "../components/satellite/SatelliteProfileModal";
import AddSatelliteModal from "../components/AddSatelliteModal";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal";
import PopupMessage from "../components/PopupMessage";

// hooks
import usePopupMessage from "../hooks/usePopupMessage";

// api imports
import { getAllSatellites, getSatelliteProfile } from "../api/satelliteService";
import {
  modifySatellite,
  deleteSatellite,
  getDeletedSatellites,
  recoverSatellite,
  createSatellite,
} from "../api/manageSatellitesService";
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
  // component fields
  const [satellites, setSatellites] = useState([]);
  const [deletedSatellites, setDeletedSatellites] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [tab, setTab] = useState("active");
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [deletedLoading, setDeletedLoading] = useState(false);
  const [profileData, setProfileData] = useState(null);
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

  // switch tabs load deleted list on first visit
  const handleTabChange = (next) => {
    setTab(next);
    if (next === "deleted" && deletedSatellites.length === 0) {
      setDeletedLoading(true);
      getDeletedSatellites()
        .then((data) => setDeletedSatellites(data))
        .catch((err) =>
          console.error("Failed to load recently deleted satellites:", err),
        )
        .finally(() => setDeletedLoading(false));
    }
  };

  // handle recover satellite
  const handleRecover = async (sat) => {
    try {
      await recoverSatellite(sat.satellite_id);
      setDeletedSatellites((prev) =>
        prev.filter((s) => s.satellite_id !== sat.satellite_id),
      );
      setSatellites((prev) => [...prev, sat]);
      showPopupMessage(`${sat.name} recovered successfully`);
    } catch (err) {
      console.error("Failed to recover satellite:", err);
      showPopupMessage("Failed to recover satellite", "error");
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
      // add to deleted list if it's already been loaded
      setDeletedSatellites((prev) =>
        prev.length > 0
          ? [{ ...deleteTarget, deleted_at: new Date().toISOString() }, ...prev]
          : prev,
      );
      setDeleteTarget(null);
      showPopupMessage("Satellite deleted successfully");
    } catch (err) {
      console.error("Failed to delete satellite:", err);
      showPopupMessage("Failed to delete satellite", "error");
    }
  };

  // main component structure
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

      {/* Tab Toggle */}
      <div className={styles.tabBar}>
        <button
          className={`${styles.tab} ${tab === "active" ? styles.tabActive : ""}`}
          onClick={() => handleTabChange("active")}
        >
          Active
        </button>
        <button
          className={`${styles.tab} ${tab === "deleted" ? styles.tabActive : ""}`}
          onClick={() => handleTabChange("deleted")}
        >
          Recently Deleted
        </button>
      </div>

      {/* Filter Bar — active tab only */}
      {tab === "active" && (
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
      )}

      {tab === "active" ? (
        /* Active Satellite List */
        <div className={styles.listCard}>
          <div className={styles.listHeader}>
            <span className={styles.listHeaderCell}>Name</span>
            <span className={styles.listHeaderCell}>Type</span>
            <span className={styles.listHeaderCell}>Orbit</span>
            <span className={styles.listHeaderCell}>NORAD ID</span>
            <span className={styles.listHeaderCell}></span>
            <span className={styles.listHeaderCell}></span>
          </div>
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
      ) : (
        /* Deleted Satellite List */
        <div className={styles.listCard}>
          <div className={`${styles.listHeader} ${styles.listHeaderDeleted}`}>
            <span className={styles.listHeaderCell}>Name</span>
            <span className={styles.listHeaderCell}>Type</span>
            <span className={styles.listHeaderCell}>Orbit</span>
            <span className={styles.listHeaderCell}>NORAD ID</span>
            <span className={styles.listHeaderCell}>Deleted</span>
            <span className={styles.listHeaderCell}></span>
          </div>
          <div className={styles.listBody}>
            {deletedLoading ? (
              <div className={styles.emptyState}>
                Loading deleted satellites...
              </div>
            ) : deletedSatellites.length === 0 ? (
              <div className={styles.emptyState}>No deleted satellites</div>
            ) : (
              deletedSatellites.map((sat) => (
                <div
                  key={sat.satellite_id}
                  className={`${styles.listRow} ${styles.listRowDeleted}`}
                >
                  <div className={styles.listRowName}>
                    <div className={styles.listDotDeleted} />
                    {sat.name} - {sat.object_id}
                  </div>
                  <div className={styles.listCell}>
                    <span className={styles.typeBadge}>
                      {sat.satellite_type ?? "Unknown"}
                    </span>
                  </div>
                  <div className={styles.listCell}>{sat.orbit_type}</div>
                  <div className={styles.listCell}>{sat.norad_id}</div>
                  <div className={styles.listCell}>
                    {sat.deleted_at
                      ? new Date(sat.deleted_at).toLocaleDateString()
                      : "—"}
                  </div>
                  <button
                    className={styles.restoreButton}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRecover(sat);
                    }}
                  >
                    <RestoreIcon sx={{ fontSize: 18 }} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Add Satellite Modal */}
      {showAddModal && (
        <AddSatelliteModal
          data={datasets}
          onClose={() => setShowAddModal(false)}
          onSave={async (payload) => {
            await createSatellite(payload);
            const data = await getAllSatellites();
            setSatellites(data);
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
          title="Remove Satellite"
          message="This satellite will be moved to Recently Deleted. It can be recovered within 30 days, after which it is permanently removed."
          confirmLabel="Delete"
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
