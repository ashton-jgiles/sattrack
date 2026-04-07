// react imports
import React, { useState, useEffect, useMemo } from "react";
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
import SearchIcon from "@mui/icons-material/Search";

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

      <div className={styles.infoPanelGrid}>
        <div className={styles.infoPanelSection}>
          <span className={styles.infoPanelSectionTitle}>Identification</span>
          <InfoField label="Name" value={s.name} />
          <InfoField label="NORAD ID" value={s.norad_id} />
          <InfoField label="Orbit Type" value={s.orbit_type} />
          <InfoField label="Description" value={s.description} />
        </div>

        <div className={styles.infoPanelSection}>
          <span className={styles.infoPanelSectionTitle}>Owner</span>
          <InfoField label="Owner" value={o.owner_name} />
          <InfoField label="Operator" value={o.operator} />
          <InfoField label="Country" value={o.country} />
        </div>

        <div className={styles.infoPanelSection}>
          <span className={styles.infoPanelSectionTitle}>Launch</span>
          <InfoField label="Deploy Date" value={deployDate} />
          <InfoField label="Vehicle" value={l.vehicle_name} />
          <InfoField label="Launch Site" value={ls.site_name} />
        </div>

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
  const [allSatellites, setAllSatellites] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [categorySatellites, setCategorySatellites] = useState([]);
  const [highlightedSatellites, setHighlightedSatellites] = useState([]);
  const [selectedSatelliteId, setSelectedSatelliteId] = useState(null);

  // Filter state
  const [searchTerm, setSearchTerm] = useState("");
  const [satelliteTypeFilter, setSatelliteTypeFilter] = useState("");
  const [orbitTypeFilter, setOrbitTypeFilter] = useState("");
  const [minAltitude, setMinAltitude] = useState("");
  const [maxAltitude, setMaxAltitude] = useState("");
  const [minVelocity, setMinVelocity] = useState("");
  const [maxVelocity, setMaxVelocity] = useState("");

  // Derived option lists for the dropdowns
  const satelliteTypes = useMemo(
    () => [
      ...new Set(allSatellites.map((s) => s.satellite_type).filter(Boolean)),
    ],
    [allSatellites],
  );
  const orbitTypes = useMemo(
    () => [...new Set(allSatellites.map((s) => s.orbit_type).filter(Boolean))],
    [allSatellites],
  );

  // Whether any filter is currently active
  const isFiltered =
    searchTerm.trim() !== "" ||
    satelliteTypeFilter !== "" ||
    orbitTypeFilter !== "" ||
    minAltitude !== "" ||
    maxAltitude !== "" ||
    minVelocity !== "" ||
    maxVelocity !== "";

  // The set of satellite IDs that pass current filters.
  // null means "show all" (no filter active).
  const visibleSatelliteIds = useMemo(() => {
    if (!isFiltered) return null;

    const search = searchTerm.trim().toLowerCase();
    const minAlt = parseFloat(minAltitude);
    const maxAlt = parseFloat(maxAltitude);
    const minVel = parseFloat(minVelocity);
    const maxVel = parseFloat(maxVelocity);

    const filtered = allSatellites.filter((sat) => {
      if (search) {
        const matchesSearch =
          sat.name.toLowerCase().includes(search) ||
          (sat.norad_id && sat.norad_id.toString().includes(search));
        if (!matchesSearch) return false;
      }

      if (satelliteTypeFilter && sat.satellite_type !== satelliteTypeFilter)
        return false;
      if (orbitTypeFilter && sat.orbit_type !== orbitTypeFilter) return false;

      const altitude = Number(sat.altitude);
      if (!isNaN(minAlt) && !isNaN(altitude) && altitude < minAlt) return false;
      if (!isNaN(maxAlt) && !isNaN(altitude) && altitude > maxAlt) return false;
      if (!isNaN(minAlt) && isNaN(altitude) && minAltitude !== "") return false;
      if (!isNaN(maxAlt) && isNaN(altitude) && maxAltitude !== "") return false;

      const velocity = Number(sat.velocity);
      if (!isNaN(minVel) && !isNaN(velocity) && velocity < minVel) return false;
      if (!isNaN(maxVel) && !isNaN(velocity) && velocity > maxVel) return false;
      if (!isNaN(minVel) && isNaN(velocity) && minVelocity !== "") return false;
      if (!isNaN(maxVel) && isNaN(velocity) && maxVelocity !== "") return false;

      return true;
    });

    return new Set(filtered.map((s) => s.satellite_id));
  }, [
    isFiltered,
    allSatellites,
    searchTerm,
    satelliteTypeFilter,
    orbitTypeFilter,
    minAltitude,
    maxAltitude,
    minVelocity,
    maxVelocity,
  ]);

  const clearFilters = () => {
    setSearchTerm("");
    setSatelliteTypeFilter("");
    setOrbitTypeFilter("");
    setMinAltitude("");
    setMaxAltitude("");
    setMinVelocity("");
    setMaxVelocity("");
  };

  const handleStatClick = async (category) => {
    setSelectedCategory(category);
    setLoading(true);
    try {
      const typeMap = {
        earth: "Earth Science",
        oceanic: "Oceanic Science",
        navigation: "Navigation",
        internet: "Internet",
        research: "Research",
        weather: "Weather",
      };
      const filtered =
        category === "total"
          ? allSatellites
          : allSatellites.filter(
              (sat) => sat.satellite_type === typeMap[category],
            );
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
        const [counts, datasets, recentDeployments, satellites] =
          await Promise.all([
            getSatelliteCounts(),
            getTotalDatasets(),
            getRecentDeployments(),
            getAllSatellites(),
          ]);

        setAllSatellites(satellites);
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

  const inputStyle = {
    padding: "0.45rem 0.75rem",
    border: "1px solid #1e293b",
    borderRadius: "0.375rem",
    backgroundColor: "#0a1628",
    color: "#cbd5e1",
    fontSize: "0.8125rem",
    fontFamily: "inherit",
    outline: "none",
    width: "100%",
  };

  const visibleCount =
    visibleSatelliteIds === null
      ? allSatellites.length
      : visibleSatelliteIds.size;

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

      {/* Filter bar */}
      <div className={styles.filterBar}>
        {/* Search */}
        <div className={styles.filterSearch}>
          <SearchIcon sx={{ fontSize: 16, color: "#475569", flexShrink: 0 }} />
          <input
            type="text"
            placeholder="Search by name or NORAD ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ ...inputStyle, paddingLeft: "0.25rem" }}
          />
        </div>

        {/* Category dropdown */}
        <select
          value={satelliteTypeFilter}
          onChange={(e) => setSatelliteTypeFilter(e.target.value)}
          style={inputStyle}
          className={styles.filterSelect}
        >
          <option value="">All Categories</option>
          {satelliteTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>

        {/* Orbit dropdown */}
        <select
          value={orbitTypeFilter}
          onChange={(e) => setOrbitTypeFilter(e.target.value)}
          style={inputStyle}
          className={styles.filterSelect}
        >
          <option value="">All Orbits</option>
          {orbitTypes.map((orbit) => (
            <option key={orbit} value={orbit}>
              {orbit}
            </option>
          ))}
        </select>

        {/* Altitude range */}
        <input
          type="number"
          placeholder="Min altitude"
          value={minAltitude}
          onChange={(e) => setMinAltitude(e.target.value)}
          style={inputStyle}
          className={styles.filterInput}
        />
        <input
          type="number"
          placeholder="Max altitude"
          value={maxAltitude}
          onChange={(e) => setMaxAltitude(e.target.value)}
          style={inputStyle}
          className={styles.filterInput}
        />

        {/* Velocity range */}
        <input
          type="number"
          placeholder="Min velocity"
          value={minVelocity}
          onChange={(e) => setMinVelocity(e.target.value)}
          style={inputStyle}
          className={styles.filterInput}
        />
        <input
          type="number"
          placeholder="Max velocity"
          value={maxVelocity}
          onChange={(e) => setMaxVelocity(e.target.value)}
          style={inputStyle}
          className={styles.filterInput}
        />

        {/* Clear + count */}
        <div className={styles.filterActions}>
          {isFiltered && (
            <button className={styles.filterClear} onClick={clearFilters}>
              <CloseIcon sx={{ fontSize: 14 }} /> Clear
            </button>
          )}
          <span className={styles.filterCount}>
            {visibleCount} / {allSatellites.length}
          </span>
        </div>
      </div>

      {/* Satellite info panel */}
      {selectedSatelliteId && (
        <SatelliteInfoPanel
          satelliteId={selectedSatelliteId}
          onClose={() => setSelectedSatelliteId(null)}
        />
      )}

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
            <SatelliteGlobe
              highlightedSatellites={highlightedSatellites}
              visibleSatelliteIds={visibleSatelliteIds}
            />
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
                      {sat.object_id} · {sat.orbit_type} · {sat.classification}
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

// Placeholder pages
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

      <div className={styles.body}>
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

        <main className={styles.main}>{renderPage()}</main>
      </div>
    </div>
  );
}
