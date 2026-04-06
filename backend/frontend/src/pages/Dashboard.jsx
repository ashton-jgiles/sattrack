// react imports
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// auth import
import { useAuth } from "../hooks/useAuth";

// page imports
import ManageSatellites from "./ManageSatellites";
import ManageDatasets from "./ManageDatasets";
import Datasets from "./Datasets";

// icon imports
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import LogoutIcon from "@mui/icons-material/Logout";
import DashboardIcon from "@mui/icons-material/Dashboard";
import EqualizerIcon from "@mui/icons-material/Equalizer";
import StorageIcon from "@mui/icons-material/Storage";
import RateReviewIcon from "@mui/icons-material/RateReview";
import ManageSearchIcon from "@mui/icons-material/ManageSearch";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import PublicIcon from "@mui/icons-material/Public";
import DatasetIcon from "@mui/icons-material/Dataset";
import WavesIcon from "@mui/icons-material/Waves";
import ExploreIcon from "@mui/icons-material/Explore";
import WifiIcon from "@mui/icons-material/Wifi";
import ScienceIcon from "@mui/icons-material/Science";
import AirIcon from "@mui/icons-material/Air";
import CloseIcon from "@mui/icons-material/Close";

// component imports
import SatelliteGlobe from "../components/SatelliteGlobe";
import SatelliteListModal from "../components/SatelliteListModal";

// api imports
import {
  getSatelliteCounts,
  getRecentDeployments,
  getAllSatellites,
  getSatelliteProfile,
} from "../api/satelliteService";
import { getTotalDatasets } from "../api/datasetService";

// style imports
import styles from "../styles/Dashboard.module.css";

// Sidebar nav config
const NAV_ITEMS = [
  {
    section: "General",
    items: [
      {
        id: "overview",
        label: "Overview",
        icon: <DashboardIcon sx={{ fontSize: 18 }} />,
        minLevel: 1,
      },
      {
        id: "datasets",
        label: "Datasets",
        icon: <StorageIcon sx={{ fontSize: 18 }} />,
        minLevel: 1,
      },
    ],
  },
  {
    section: "Scientific Analysis",
    items: [
      {
        id: "visualizations",
        label: "Visualizations",
        icon: <EqualizerIcon sx={{ fontSize: 18 }} />,
        minLevel: 1,
      },
    ],
  },
  {
    section: "Dataset Review",
    items: [
      {
        id: "reviews",
        label: "Reviews",
        icon: <RateReviewIcon sx={{ fontSize: 18 }} />,
        minLevel: 3,
      },
    ],
  },
  {
    section: "Admin",
    items: [
      {
        id: "manageSatellites",
        label: "Manage Satellites",
        icon: <ManageSearchIcon sx={{ fontSize: 18 }} />,
        minLevel: 4,
      },
      {
        id: "manageDatasets",
        label: "Manage Datasets",
        icon: <DatasetIcon sx={{ fontSize: 18 }} />,
        minLevel: 4,
      },
      {
        id: "admin",
        label: "Admin Panel",
        icon: <AdminPanelSettingsIcon sx={{ fontSize: 18 }} />,
        minLevel: 4,
      },
    ],
  },
];

// Stat Card
function StatCard({ label, value, icon, loading, onClick }) {
  return (
    <div
      className={`${styles.statCard} ${onClick ? styles.clickable : ""}`}
      onClick={onClick}
    >
      <div className={styles.statCardHeader}>
        <span className={styles.statCardLabel}>{label}</span>
        <span className={styles.statCardIcon}>{icon}</span>
      </div>
      <span className={styles.statCardValue}>
        {loading ? "—" : (value ?? "—")}
      </span>
    </div>
  );
}

// A single labelled field for the info panel
function InfoField({ label, value }) {
  return (
    <div className={styles.infoField}>
      <span className={styles.infoFieldLabel}>{label}</span>
      <span className={styles.infoFieldValue}>
        {value ?? <span style={{ color: "#334155" }}>—</span>}
      </span>
    </div>
  );
}

// Satellite info panel shown below the globe when a satellite is selected
function SatelliteInfoPanel({ satelliteId, onClose }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!satelliteId) return;
    setLoading(true);
    setError(null);
    setProfile(null);
    getSatelliteProfile(satelliteId)
      .then((data) => setProfile(data))
      .catch((err) => {
        console.error("Failed to load satellite profile:", err);
        setError("Failed to load satellite data.");
      })
      .finally(() => setLoading(false));
  }, [satelliteId]);

  if (loading) {
    return (
      <div className={styles.infoPanel}>
        <div className={styles.infoPanelLoading}>Loading satellite data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.infoPanel}>
        <div className={styles.infoPanelError}>{error}</div>
      </div>
    );
  }

  if (!profile) return null;

  const s = profile.satellite || {};
  const o = profile.owner || {};
  const l = profile.launch || {};
  const ls = profile.launch_site || {};
  const c = profile.communication || {};

  const deployDate = l.deploy_date_time
    ? new Date(l.deploy_date_time).toLocaleDateString()
    : null;

  return (
    <div className={styles.infoPanel}>
      {/* Header row */}
      <div className={styles.infoPanelHeader}>
        <div className={styles.infoPanelTitleGroup}>
          <SatelliteAltIcon sx={{ fontSize: 18, color: "#3b82f6" }} />
          <span className={styles.infoPanelTitle}>
            {s.name ?? "Unknown Satellite"}
          </span>
          {s.orbit_type && (
            <span className={styles.infoPanelBadge}>{s.orbit_type}</span>
          )}
          {s.satellite_type && (
            <span className={styles.infoPanelBadgeAlt}>{s.satellite_type}</span>
          )}
        </div>
        <button className={styles.infoPanelClose} onClick={onClose}>
          <CloseIcon sx={{ fontSize: 16 }} />
        </button>
      </div>

      {/* Fields grid */}
      <div className={styles.infoPanelGrid}>
        {/* Column 1: Identification */}
        <div className={styles.infoPanelSection}>
          <span className={styles.infoPanelSectionTitle}>Identification</span>
          <InfoField label="Name" value={s.name} />
          <InfoField label="NORAD ID" value={s.norad_id} />
          <InfoField label="Orbit Type" value={s.orbit_type} />
          <InfoField label="Description" value={s.description} />
        </div>

        {/* Column 2: Owner */}
        <div className={styles.infoPanelSection}>
          <span className={styles.infoPanelSectionTitle}>Owner</span>
          <InfoField label="Owner" value={o.owner_name} />
          <InfoField label="Operator" value={o.operator} />
          <InfoField label="Country" value={o.country} />
        </div>

        {/* Column 3: Launch */}
        <div className={styles.infoPanelSection}>
          <span className={styles.infoPanelSectionTitle}>Launch</span>
          <InfoField label="Deploy Date" value={deployDate} />
          <InfoField label="Vehicle" value={l.vehicle_name} />
          <InfoField label="Launch Site" value={ls.site_name} />
        </div>

        {/* Column 4: Communications */}
        <div className={styles.infoPanelSection}>
          <span className={styles.infoPanelSectionTitle}>Communications</span>
          <InfoField label="Station" value={c.station_name} />
          <InfoField label="Frequency" value={c.communication_frequency} />
          <InfoField label="Satellite Type" value={s.satellite_type} />
        </div>
      </div>
    </div>
  );
}

// Page: Overview
function OverviewPage() {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [categorySatellites, setCategorySatellites] = useState([]);
  const [highlightedSatellites, setHighlightedSatellites] = useState([]);
  const [selectedSatelliteId, setSelectedSatelliteId] = useState(null);

  const handleStatClick = async (category) => {
    setSelectedCategory(category);
    setLoading(true);
    try {
      const allSatellites = await getAllSatellites();
      let filtered = [];
      if (category === "total") {
        filtered = allSatellites;
      } else {
        const typeMap = {
          earth: "Earth Science",
          oceanic: "Oceanic Science",
          navigation: "Navigation",
          internet: "Internet",
          research: "Research",
          weather: "Weather",
        };
        filtered = allSatellites.filter(
          (sat) => sat.satellite_type === typeMap[category],
        );
      }
      setCategorySatellites(filtered);
      setShowModal(true);
    } catch (err) {
      console.error("Failed to load satellites:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [counts, datasets, recentDeployments] = await Promise.all([
          getSatelliteCounts(),
          getTotalDatasets(),
          getRecentDeployments(),
        ]);

        setStats({
          total: counts.total,
          datasets,
          earth: counts.earth_science,
          oceanic: counts.oceanic_science,
          navigation: counts.navigation,
          internet: counts.internet,
          research: counts.research,
          weather: counts.weather,
          recentDeployments,
        });
      } catch (err) {
        console.error("Failed to fetch stats:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className={styles.content}>
      <div>
        <h2 className={styles.pageTitle}>Dashboard Overview</h2>
        <p className={styles.pageSubtitle}>
          Real-time satellite tracking and monitoring
          {stats.datasets ? ` with ${stats.datasets} datasets available` : ""}
        </p>
      </div>

      {/* Stats row */}
      <div className={styles.statsRow}>
        <StatCard
          label="Total Satellites"
          value={stats.total}
          icon={<SatelliteAltIcon sx={{ fontSize: 20 }} />}
          loading={loading}
          onClick={() => handleStatClick("total")}
        />
        <StatCard
          label="Earth Satellites"
          value={stats.earth}
          icon={<PublicIcon sx={{ fontSize: 20 }} />}
          loading={loading}
          onClick={() => handleStatClick("earth")}
        />
        <StatCard
          label="Oceanic Satellites"
          value={stats.oceanic}
          icon={<WavesIcon sx={{ fontSize: 20 }} />}
          loading={loading}
          onClick={() => handleStatClick("oceanic")}
        />
        <StatCard
          label="Navigation Satellites"
          value={stats.navigation}
          icon={<ExploreIcon sx={{ fontSize: 20 }} />}
          loading={loading}
          onClick={() => handleStatClick("navigation")}
        />
        <StatCard
          label="Internet Satellites"
          value={stats.internet}
          icon={<WifiIcon sx={{ fontSize: 20 }} />}
          loading={loading}
          onClick={() => handleStatClick("internet")}
        />
        <StatCard
          label="Research Satellites"
          value={stats.research}
          icon={<ScienceIcon sx={{ fontSize: 20 }} />}
          loading={loading}
          onClick={() => handleStatClick("research")}
        />
        <StatCard
          label="Weather Satellites"
          value={stats.weather}
          icon={<AirIcon sx={{ fontSize: 20 }} />}
          loading={loading}
          onClick={() => handleStatClick("weather")}
        />
      </div>

      {/* Globe + Deployments side by side */}
      <div className={styles.globeRow}>
        {/* Left: Globe */}
        <div className={styles.globeCard}>
          <div className={styles.globeCardHeader}>
            <span className={styles.globeCardTitle}>
              Live Satellite Positions
            </span>
          </div>
          <div className={styles.globeCardBody}>
            <SatelliteGlobe highlightedSatellites={highlightedSatellites} />
          </div>
        </div>

        {/* Right: Recent Deployments */}
        <div className={styles.deploymentCard}>
          <div className={styles.deploymentCardHeader}>
            <span className={styles.deploymentCardTitle}>
              Satellites Deployed in the Last 5 Years
            </span>
          </div>
          <div className={styles.deploymentList}>
            {loading ? (
              <div className={styles.deploymentItem}>
                <span className={styles.deploymentMeta}>Loading...</span>
              </div>
            ) : stats.recentDeployments?.length === 0 ? (
              <div className={styles.deploymentItem}>
                <span className={styles.deploymentMeta}>
                  No recent deployments
                </span>
              </div>
            ) : (
              stats.recentDeployments?.map((sat) => (
                <div key={sat.satellite_id} className={styles.deploymentItem}>
                  <div className={styles.deploymentDot} />
                  <div className={styles.deploymentInfo}>
                    <span className={styles.deploymentName}>
                      {sat.satellite_type} - {sat.name} - {sat.norad_id}
                    </span>
                    <span className={styles.deploymentMeta}>
                      {sat.object_id} · {sat.orbit_type} ·{" "}
                      {sat.classification}{" "}
                    </span>
                  </div>
                  <span className={styles.deploymentDate}>
                    Deploy Date:{" "}
                    {new Date(sat.deploy_date_time).toLocaleDateString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Satellite info panel — appears below globe row when a satellite is selected */}
      {selectedSatelliteId && (
        <SatelliteInfoPanel
          satelliteId={selectedSatelliteId}
          onClose={() => setSelectedSatelliteId(null)}
        />
      )}

      {/* Satellite List Modal */}
      {showModal && (
        <SatelliteListModal
          category={selectedCategory}
          satellites={categorySatellites}
          onClose={() => setShowModal(false)}
          onSatelliteClick={(satelliteId) => {
            setHighlightedSatellites([satelliteId]);
            setSelectedSatelliteId(satelliteId);
            setShowModal(false);
          }}
        />
      )}
    </div>
  );
}

// Placeholder pages (remove when all pages are done)
function PlaceholderPage({ title }) {
  return (
    <>
      <div>
        <h2 className={styles.pageTitle}>{title}</h2>
        <p className={styles.pageSubtitle}>Coming soon</p>
      </div>
      <div className={styles.placeholder}>{title} — under construction</div>
    </>
  );
}

// Dashboard
export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activePage, setActivePage] = useState("overview");

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Filter nav items by user's level_access
  const visibleNav = NAV_ITEMS.map((section) => ({
    ...section,
    items: section.items.filter((item) => user?.level_access >= item.minLevel),
  })).filter((section) => section.items.length > 0);

  const renderPage = () => {
    switch (activePage) {
      case "overview":
        return <OverviewPage />;
      case "satellites":
        return <PlaceholderPage title="Satellites" />;
      case "datasets":
        return <Datasets />;
      case "visualizations":
        return <PlaceholderPage title="Visualizations" />;
      case "reviews":
        return <PlaceholderPage title="Reviews" />;
      case "manageSatellites":
        return <ManageSatellites />;
      case "manageDatasets":
        return <ManageDatasets />;
      case "admin":
        return <PlaceholderPage title="Admin Panel" />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <div className={styles.page}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.logo}>
            <SatelliteAltIcon
              sx={{ fontSize: 28 }}
              className={styles.logoIcon}
            />
            <h1 className={styles.logoText}>SatTrack Dashboard</h1>
          </div>
          <div className={styles.headerRight}>
            <span className={styles.username}>{user?.full_name}</span>
            <button onClick={handleLogout} className={styles.logoutButton}>
              <LogoutIcon sx={{ fontSize: 16 }} />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Body */}
      <div className={styles.body}>
        {/* Sidebar */}
        <aside className={styles.sidebar}>
          {visibleNav.map((section, i) => (
            <div key={section.section} className={styles.sidebarSection}>
              {i > 0 && <div className={styles.sidebarDivider} />}
              <p className={styles.sidebarLabel}>{section.section}</p>
              {section.items.map((item) => (
                <button
                  key={item.id}
                  className={`${styles.sidebarItem} ${activePage === item.id ? styles.sidebarItemActive : ""}`}
                  onClick={() => setActivePage(item.id)}
                >
                  {item.icon}
                  {item.label}
                </button>
              ))}
            </div>
          ))}
        </aside>

        {/* Main content */}
        <main className={styles.main}>{renderPage()}</main>
      </div>
    </div>
  );
}
