// react imports
import React, { useEffect, useState } from "react";

// icon imports
import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";

// api imports
import {
  getAllDatasets,
  modifyDataset,
  addDataset,
  getDatasetSources,
  deleteDataset,
} from "../api/datasetService";

// component imports
import DatasetProfileModal from "../components/DatasetProfileModal";
import AddDatasetModal from "../components/AddDatasetModal";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal";
import PopupMessage from "../components/PopupMessage";

// hooks
import usePopupMessage from "../hooks/usePopupMessage";

// style imports
import styles from "../styles/ManageDatasets.module.css";

const STATUS_STYLES = {
  approved: { backgroundColor: "#14532d", color: "#4ade80" },
  pending: { backgroundColor: "#1c1917", color: "#f59e0b" },
  rejected: { backgroundColor: "#450a0a", color: "#f87171" },
};

export default function ManageDatasets() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editTarget, setEditTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [sources, setSources] = useState([]);

  const { message, messageFading, messageVisible, showPopupMessage } =
    usePopupMessage();

  // load datasets on mount
  useEffect(() => {
    getAllDatasets()
      .then((data) => setDatasets(data))
      .catch((err) => console.error("Failed to load datasets:", err))
      .finally(() => setLoading(false));
  }, []);

  // handle save from edit modal
  const handleSave = async (payload) => {
    await modifyDataset(editTarget.dataset_id, payload);
    setDatasets((prev) =>
      prev.map((d) =>
        d.dataset_id === editTarget.dataset_id ? { ...d, ...payload } : d,
      ),
    );
    showPopupMessage("Dataset updated successfully");
  };

  // handle add dataset
  const handleAdd = async (payload) => {
    const result = await addDataset(payload);
    const updated = await getAllDatasets();
    setDatasets(updated);
    showPopupMessage(result.message ?? "Dataset created successfully");
    return result;
  };

  // handle delete dataset
  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      await deleteDataset(deleteTarget.dataset_id);
      setDatasets((prev) =>
        prev.filter((d) => d.dataset_id !== deleteTarget.dataset_id),
      );
      setDeleteTarget(null);
      showPopupMessage("Dataset deleted successfully");
    } catch (err) {
      console.error("Failed to delete dataset:", err);
      showPopupMessage("Failed to delete dataset", "error");
    }
  };

  // main component structure
  return (
    <div className={styles.page}>
      {/* Page Header */}
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.pageTitle}>Manage Datasets</h2>
          <p className={styles.pageSubtitle}>
            Review and manage satellite datasets
          </p>
        </div>
        <button
          className={styles.addButton}
          onClick={() => {
            getDatasetSources()
              .then(setSources)
              .catch((err) => console.error("Failed to load sources:", err));
            setShowAddModal(true);
          }}
        >
          <AddIcon sx={{ fontSize: 18 }} />
          Add Dataset
        </button>
      </div>

      {/* Dataset Table */}
      <div className={styles.listCard}>
        <div className={styles.listHeader}>
          <span className={styles.listHeaderCell}>Name</span>
          <span className={styles.listHeaderCell}>Source</span>
          <span className={styles.listHeaderCell}>File Size</span>
          <span className={styles.listHeaderCell}>Last Pulled</span>
          <span className={styles.listHeaderCell}>Created</span>
          <span className={styles.listHeaderCell}>Review Status</span>
          <span className={styles.listHeaderCell}></span>
          <span className={styles.listHeaderCell}></span>
        </div>

        <div className={styles.listBody}>
          {loading ? (
            <div className={styles.emptyState}>Loading datasets...</div>
          ) : datasets.length === 0 ? (
            <div className={styles.emptyState}>No datasets found</div>
          ) : (
            datasets.map((dataset) => (
              <div key={dataset.dataset_id} className={styles.listRow}>
                <div className={styles.listRowName}>
                  <div className={styles.listDot} />
                  {dataset.dataset_name}
                </div>
                <div className={styles.listCell}>{dataset.source}</div>
                <div className={styles.listCell}>
                  {dataset.file_size ?? "—"}
                </div>
                <div className={styles.listCell}>
                  {dataset.last_pulled
                    ? new Date(dataset.last_pulled).toLocaleDateString()
                    : "—"}
                </div>
                <div className={styles.listCell}>
                  {dataset.creation_date
                    ? new Date(dataset.creation_date).toLocaleDateString()
                    : "—"}
                </div>
                <div className={styles.listCell}>
                  <span
                    className={styles.statusBadge}
                    style={STATUS_STYLES[dataset.review_status] ?? {}}
                  >
                    {dataset.review_status}
                  </span>
                </div>
                <button
                  className={styles.actionButton}
                  onClick={() => setEditTarget(dataset)}
                >
                  <EditIcon sx={{ fontSize: 18 }} />
                </button>
                <button
                  className={styles.deleteButton}
                  onClick={() => setDeleteTarget(dataset)}
                >
                  <DeleteOutlineIcon sx={{ fontSize: 18 }} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {editTarget && (
        <DatasetProfileModal
          data={editTarget}
          onClose={() => setEditTarget(null)}
          onSave={handleSave}
        />
      )}

      {/* Add Modal */}
      {showAddModal && (
        <AddDatasetModal
          sources={sources}
          onClose={() => setShowAddModal(false)}
          onSave={handleAdd}
        />
      )}

      {/* Confirm Delete Modal */}
      {deleteTarget && (
        <ConfirmDeleteModal
          title="Remove Dataset"
          message="Removing this dataset will also remove all associated satellites."
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
