// react imports
import React, { useEffect, useState } from "react";

// icon imports
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import StorageIcon from "@mui/icons-material/Storage";

// api imports
import { getReviewDatasets, reviewDataset } from "../../api/datasetService";
import { getSatellitesInDataset } from "../../api/datasetService";

// component imports
import PopupMessage from "../../components/PopupMessage";

// hooks
import usePopupMessage from "../../hooks/usePopupMessage";

// style imports
import styles from "../../styles/dataset/Reviews.module.css";

// status styles
const STATUS_STYLES = {
  approved: styles.statusApproved,
  pending: styles.statusPending,
  rejected: styles.statusRejected,
};

// single review card
function ReviewCard({ dataset, showClosed, onReview }) {
  // function fields
  const [satellitesOpen, setSatellitesOpen] = useState(false);
  const [satellites, setSatellites] = useState([]);
  const [satellitesLoading, setSatellitesLoading] = useState(false);

  // handle toggle satellites
  const handleToggleSatellites = () => {
    if (!satellitesOpen && satellites.length === 0) {
      setSatellitesLoading(true);
      getSatellitesInDataset(dataset.dataset_id)
        .then(setSatellites)
        .catch((err) => console.error("Failed to load satellites:", err))
        .finally(() => setSatellitesLoading(false));
    }
    setSatellitesOpen((prev) => !prev);
  };

  // main function components
  return (
    <div className={styles.card}>
      {/* Card Header */}
      <div className={styles.cardHeader}>
        <div className={styles.cardIcon}>
          <StorageIcon sx={{ fontSize: 20 }} />
        </div>
        <div className={styles.cardMeta}>
          <h3 className={styles.cardTitle}>{dataset.dataset_name}</h3>
        </div>
        <span
          className={`${styles.statusBadge} ${STATUS_STYLES[dataset.review_status] ?? ""}`}
        >
          {dataset.review_status}
        </span>
      </div>

      {/* Description */}
      <p className={styles.cardDescription}>
        {dataset.description ?? "No description provided."}
      </p>

      {/* Stats */}
      <div className={styles.cardStats}>
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
        <div className={styles.statItem}>
          <span className={styles.statLabel}>Pull Frequency</span>
          <span className={styles.statValue}>
            {dataset.pull_frequency ?? "—"}
          </span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>Satellites</span>
          <span className={styles.statValue}>
            {dataset.satellite_count ?? 0}
          </span>
        </div>
      </div>

      {/* Review Comment (closed only) */}
      {showClosed && dataset.review_comment && (
        <div className={styles.commentBlock}>
          <span className={styles.commentLabel}>Review note</span>
          <p className={styles.commentText}>{dataset.review_comment}</p>
        </div>
      )}

      {/* Card Actions */}
      <div className={styles.cardActions}>
        <button
          className={styles.satelliteToggle}
          onClick={handleToggleSatellites}
        >
          {satellitesOpen ? (
            <ExpandLessIcon sx={{ fontSize: 15 }} />
          ) : (
            <ExpandMoreIcon sx={{ fontSize: 15 }} />
          )}
          View Satellites
        </button>
        {!showClosed && (
          <div className={styles.actionGroup}>
            <button
              className={styles.approveButton}
              onClick={() => onReview(dataset, "approved")}
            >
              <CheckIcon sx={{ fontSize: 15 }} />
              Approve
            </button>
            <button
              className={styles.rejectButton}
              onClick={() => onReview(dataset, "rejected")}
            >
              <CloseIcon sx={{ fontSize: 15 }} />
              Reject
            </button>
          </div>
        )}
      </div>

      {/* Satellite Dropdown */}
      {satellitesOpen && (
        <div className={styles.satelliteDropdown}>
          {satellitesLoading ? (
            <p className={styles.satelliteEmpty}>Loading...</p>
          ) : satellites.length === 0 ? (
            <p className={styles.satelliteEmpty}>
              No satellites in this dataset
            </p>
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

// default reviews component
export default function Reviews() {
  // component fields
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showClosed, setShowClosed] = useState(false);
  const [reviewTarget, setReviewTarget] = useState(null);
  const [pendingAction, setPendingAction] = useState(null);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // create the message
  const { message, messageFading, messageVisible, showPopupMessage } =
    usePopupMessage();

  // load the datasets
  const loadDatasets = (closed) => {
    setLoading(true);
    getReviewDatasets(closed)
      .then(setDatasets)
      .catch((err) => console.error("Failed to load review datasets:", err))
      .finally(() => setLoading(false));
  };

  // on mount load the datasets
  useEffect(() => {
    loadDatasets(showClosed);
  }, [showClosed]);

  // open reviews
  const openReview = (dataset, action) => {
    setReviewTarget(dataset);
    setPendingAction(action);
    setComment("");
  };

  // close review
  const closeReview = () => {
    setReviewTarget(null);
    setPendingAction(null);
    setComment("");
  };

  // handle submit to update the database
  const handleSubmit = async () => {
    if (!reviewTarget || !pendingAction) return;
    setSubmitting(true);
    try {
      await reviewDataset(reviewTarget.dataset_id, {
        review_status: pendingAction,
        review_comment: comment,
      });
      showPopupMessage(
        `Dataset ${pendingAction === "approved" ? "approved" : "rejected"} successfully`,
      );
      closeReview();
      loadDatasets(showClosed);
    } catch (err) {
      console.error("Failed to submit review:", err);
      showPopupMessage("Failed to submit review", "error");
    } finally {
      setSubmitting(false);
    }
  };

  // main reviews page component
  return (
    <div className={styles.page}>
      {/* Page Header */}
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.pageTitle}>Reviews</h2>
          <p className={styles.pageSubtitle}>
            {showClosed ? "Closed reviews" : "Datasets pending review"}
          </p>
        </div>
        <button
          className={`${styles.toggleButton} ${showClosed ? styles.toggleActive : ""}`}
          onClick={() => setShowClosed((prev) => !prev)}
        >
          {showClosed ? "View Pending" : "View Closed"}
        </button>
      </div>

      {/* Card Grid */}
      {loading ? (
        <div className={styles.emptyState}>Loading...</div>
      ) : datasets.length === 0 ? (
        <div className={styles.emptyState}>
          {showClosed ? "No closed reviews" : "No datasets pending review"}
        </div>
      ) : (
        <div className={styles.grid}>
          {datasets.map((dataset) => (
            <ReviewCard
              key={dataset.dataset_id}
              dataset={dataset}
              showClosed={showClosed}
              onReview={openReview}
            />
          ))}
        </div>
      )}

      {/* Review Modal */}
      {reviewTarget && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>
                {pendingAction === "approved" ? "Approve" : "Reject"} Dataset
              </h3>
              <button className={styles.modalClose} onClick={closeReview}>
                <CloseIcon sx={{ fontSize: 18 }} />
              </button>
            </div>
            <div className={styles.modalBody}>
              <p className={styles.modalSubtitle}>
                {reviewTarget.dataset_name}
              </p>
              <label className={styles.commentLabel}>
                {pendingAction === "approved"
                  ? "Approval note (optional)"
                  : "Reason for rejection (optional)"}
              </label>
              <textarea
                className={styles.commentInput}
                placeholder="Add a comment..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={4}
              />
              <div className={styles.modalActions}>
                <button className={styles.cancelButton} onClick={closeReview}>
                  Cancel
                </button>
                <button
                  className={
                    pendingAction === "approved"
                      ? styles.confirmApproveButton
                      : styles.confirmRejectButton
                  }
                  onClick={handleSubmit}
                  disabled={submitting}
                >
                  {submitting
                    ? "Submitting..."
                    : pendingAction === "approved"
                      ? "Approve"
                      : "Reject"}
                </button>
              </div>
            </div>
          </div>
        </div>
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
