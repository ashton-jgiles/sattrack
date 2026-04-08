// react imports
import React, { useEffect, useState } from "react";

// icon imports
import StorageIcon from "@mui/icons-material/Storage";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";

// api imports
import {
  getAllDatasets,
  getSatellitesInDataset,
} from "../../api/datasetService";

// auth imports
import { useAuth } from "../../hooks/useAuth";

// style imports
import styles from "../styles/Datasets.module.css";

// status badge color map
const STATUS_COLORS = {
  approved: styles.statusApproved,
  pending: styles.statusPending,
  rejected: styles.statusRejected,
};

// dataset card component
function DatasetCard({ dataset, onViewDetails, showStatus }) {
  const [satellitesOpen, setSatellitesOpen] = useState(false);
  const [satellites, setSatellites] = useState([]);
  const [satellitesLoading, setSatellitesLoading] = useState(false);

  const statusClass =
    STATUS_COLORS[dataset.review_status] ?? styles.statusPending;

  return (
    <div className={styles.card}>
      {/* Card Header */}
      <div className={styles.cardHeader}>
        <div className={styles.cardIcon}>
          <StorageIcon sx={{ fontSize: 20 }} />
        </div>
        <div className={styles.cardMeta}>
          <h3 className={styles.cardTitle}>{dataset.dataset_name}</h3>
          <span className={styles.cardSource}>{dataset.source}</span>
        </div>
        {showStatus && (
          <span className={`${styles.statusBadge} ${statusClass}`}>
            {dataset.review_status}
          </span>
        )}
      </div>

      {/* Card Body */}
      <p className={styles.cardDescription}>
        {dataset.description ?? "No description provided."}
      </p>

      {/* Card Stats */}
      <div className={styles.cardStats}>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>File Size</span>
          <span className={styles.statValue}>{dataset.file_size ?? "—"}</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>Pull Frequency</span>
          <span className={styles.statValue}>
            {dataset.pull_frequency ?? "—"}
          </span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>Last Pulled</span>
          <span className={styles.statValue}>
            {dataset.last_pulled
              ? new Date(dataset.last_pulled).toLocaleDateString()
              : "—"}
          </span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>Created</span>
          <span className={styles.statValue}>
            {dataset.creation_date
              ? new Date(dataset.creation_date).toLocaleDateString()
              : "—"}
          </span>
        </div>
      </div>

      {/* Card Actions */}
      <div className={styles.cardActions}>
        <button
          className={styles.toggleButton}
          onClick={() => {
            if (!satellitesOpen && satellites.length === 0) {
              setSatellitesLoading(true);
              getSatellitesInDataset(dataset.dataset_id)
                .then((data) => setSatellites(data))
                .catch((err) =>
                  console.error("Failed to load satellites:", err),
                )
                .finally(() => setSatellitesLoading(false));
            }
            setSatellitesOpen((prev) => !prev);
          }}
        >
          {satellitesOpen ? (
            <ExpandLessIcon sx={{ fontSize: 16 }} />
          ) : (
            <ExpandMoreIcon sx={{ fontSize: 16 }} />
          )}
          View Satellites
        </button>
        <button
          className={styles.detailButton}
          onClick={() => onViewDetails(dataset)}
        >
          <OpenInNewIcon sx={{ fontSize: 16 }} />
          Details
        </button>
      </div>

      {/* Satellite Dropdown */}
      {satellitesOpen && (
        <div className={styles.satelliteDropdown}>
          {satellitesLoading ? (
            <p className={styles.comingSoon}>Loading...</p>
          ) : satellites.length === 0 ? (
            <p className={styles.comingSoon}>No satellites in this dataset</p>
          ) : (
            satellites.map((sat) => (
              <div key={sat.satellite_id} className={styles.satelliteRow}>
                <span className={styles.satelliteName}>{sat.name}</span>
                <span className={styles.satelliteMeta}>
                  {[sat.object_id, sat.orbit_type, sat.classification]
                    .filter(Boolean)
                    .join(" · ")}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

// datasets page
export default function Datasets() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const { user } = useAuth();
  const showStatus = user?.level_access >= 3;

  // load datasets on mount
  useEffect(() => {
    getAllDatasets()
      .then((data) => setDatasets(data))
      .catch((err) => console.error("Failed to load datasets:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className={styles.page}>
      {/* Page Header */}
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.pageTitle}>Datasets</h2>
          <p className={styles.pageSubtitle}>
            Browse available satellite datasets
          </p>
        </div>
      </div>

      {/* Dataset Grid */}
      {loading ? (
        <div className={styles.emptyState}>Loading datasets...</div>
      ) : datasets.length === 0 ? (
        <div className={styles.emptyState}>No datasets found</div>
      ) : (
        <div className={styles.grid}>
          {datasets.map((dataset) => (
            <DatasetCard
              key={dataset.dataset_id}
              dataset={dataset}
              onViewDetails={setSelectedDataset}
              showStatus={showStatus}
            />
          ))}
        </div>
      )}

      {/* Dataset Viewer Modal */}
      {selectedDataset && (
        <div
          className={styles.modalOverlay}
          onClick={() => setSelectedDataset(null)}
        >
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {selectedDataset.dataset_name}
              </h2>
              <button
                className={styles.modalClose}
                onClick={() => setSelectedDataset(null)}
              >
                ✕
              </button>
            </div>
            <div className={styles.modalBody}>
              <p className={styles.modalDescription}>
                {selectedDataset.description ?? "No description provided."}
              </p>
              <div className={styles.modalStats}>
                <div className={styles.modalStatRow}>
                  <span className={styles.modalStatLabel}>Source</span>
                  <span className={styles.modalStatValue}>
                    {selectedDataset.source}
                  </span>
                </div>
                <div className={styles.modalStatRow}>
                  <span className={styles.modalStatLabel}>Source URL</span>
                  <span className={styles.modalStatValue}>
                    {selectedDataset.source_url}
                  </span>
                </div>
                <div className={styles.modalStatRow}>
                  <span className={styles.modalStatLabel}>File Size</span>
                  <span className={styles.modalStatValue}>
                    {selectedDataset.file_size ?? "—"}
                  </span>
                </div>
                <div className={styles.modalStatRow}>
                  <span className={styles.modalStatLabel}>Pull Frequency</span>
                  <span className={styles.modalStatValue}>
                    {selectedDataset.pull_frequency ?? "—"}
                  </span>
                </div>
                <div className={styles.modalStatRow}>
                  <span className={styles.modalStatLabel}>Last Pulled</span>
                  <span className={styles.modalStatValue}>
                    {selectedDataset.last_pulled
                      ? new Date(selectedDataset.last_pulled).toLocaleString()
                      : "—"}
                  </span>
                </div>
                <div className={styles.modalStatRow}>
                  <span className={styles.modalStatLabel}>Created</span>
                  <span className={styles.modalStatValue}>
                    {selectedDataset.creation_date
                      ? new Date(
                          selectedDataset.creation_date,
                        ).toLocaleDateString()
                      : "—"}
                  </span>
                </div>
                <div className={styles.modalStatRow}>
                  <span className={styles.modalStatLabel}>Review Status</span>
                  <span className={styles.modalStatValue}>
                    {selectedDataset.review_status}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
