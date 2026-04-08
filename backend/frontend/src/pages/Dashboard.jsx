// react imports
import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";

// auth import
import { useAuth } from "../hooks/useAuth";

// page imports
import ManageSatellites from "./ManageSatellites";
import ManageDatasets from "./ManageDatasets";
import Datasets from "./Datasets";
import UserProfile from "./UserProfile";
import Settings from "./Settings";
import Reviews from "./Reviews";

// icon imports
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import LogoutIcon from "@mui/icons-material/Logout";
import DashboardIcon from "@mui/icons-material/Dashboard";
import EqualizerIcon from "@mui/icons-material/Equalizer";
import StorageIcon from "@mui/icons-material/Storage";
import RateReviewIcon from "@mui/icons-material/RateReview";
import ManageSearchIcon from "@mui/icons-material/ManageSearch";
import SettingsIcon from "@mui/icons-material/Settings";
import PublicIcon from "@mui/icons-material/Public";
import DatasetIcon from "@mui/icons-material/Dataset";
import WavesIcon from "@mui/icons-material/Waves";
import ExploreIcon from "@mui/icons-material/Explore";
import WifiIcon from "@mui/icons-material/Wifi";
import ScienceIcon from "@mui/icons-material/Science";
import AirIcon from "@mui/icons-material/Air";
import CloseIcon from "@mui/icons-material/Close";
import SearchIcon from "@mui/icons-material/Search";
import PersonIcon from "@mui/icons-material/Person";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import FullscreenIcon from "@mui/icons-material/Fullscreen";
import FullscreenExitIcon from "@mui/icons-material/FullscreenExit";
import MyLocationIcon from "@mui/icons-material/MyLocation";

// component imports
import SatelliteGlobe from "../components/SatelliteGlobe";

// api imports
import {
  getSatelliteCounts,
  getAllSatellites,
  getSatelliteProfile,
} from "../api/satelliteService";
import { getTotalDatasets } from "../api/datasetService";

// style imports
import styles from "../styles/Dashboard.module.css";

function NumInput({ placeholder, value, onChange, step = 1000 }) {
  const adjust = (dir) => {
    const current = parseInt(value) || 0;
    const next = Math.max(0, current + dir * step);
    onChange(String(next));
  };
  return (
    <div className={styles.numberInputWrapper}>
      <input
        className={styles.numberInput}
        type="text"
        inputMode="numeric"
        placeholder={placeholder}
        value={value}
        onChange={(e) => {
          if (e.target.value === "" || /^\d*$/.test(e.target.value)) onChange(e.target.value);
        }}
      />
      <div className={styles.numberInputSpinners}>
        <button className={styles.spinnerBtn} onClick={() => adjust(1)} tabIndex={-1}>
          <KeyboardArrowUpIcon sx={{ fontSize: 12 }} />
        </button>
        <button className={styles.spinnerBtn} onClick={() => adjust(-1)} tabIndex={-1}>
          <KeyboardArrowDownIcon sx={{ fontSize: 12 }} />
        </button>
      </div>
    </div>
  );
}

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
      {
        id: "userProfile",
        label: "User Profile",
        icon: <PersonIcon sx={{ fontSize: 18 }} />,
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
        minLevel: 2,
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
        id: "settings",
        label: "Settings",
        icon: <SettingsIcon sx={{ fontSize: 18 }} />,
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
function SatelliteInfoPanel({ satelliteId, onClose, minimized, onToggleMinimized }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!satelliteId) return;
    setLoading(true);
    setError(null);
    getSatelliteProfile(satelliteId)
      .then((data) => setProfile(data))
      .catch((err) => {
        console.error("Failed to load satellite profile:", err);
        setError("Failed to load satellite data.");
      })
      .finally(() => setLoading(false));
  }, [satelliteId]);

  const panelClass = `${styles.infoPanel} ${minimized ? styles.infoPanelAbsolute : ""}`;

  if (loading && !profile) {
    return (
      <div className={panelClass}>
        <div className={styles.infoPanelLoading}>Loading satellite data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={panelClass}>
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
    <div className={panelClass}>
      <div className={styles.infoPanelHeader}>
        <div className={styles.infoPanelTitleGroup}>
          <SatelliteAltIcon sx={{ fontSize: 18, color: "#3b82f6", flexShrink: 0 }} />
          <div className={styles.infoPanelTitleStack}>
            <div className={styles.infoPanelTitleRow}>
              <span className={styles.infoPanelTitle}>
                {s.name ?? "Unknown Satellite"}
              </span>
              {s.orbit_type && (
                <span className={styles.infoPanelBadge}>{s.orbit_type}</span>
              )}
              {s.satellite_type && (
                <span className={styles.infoPanelBadgeAlt}>{s.satellite_type}</span>
              )}
              {s.description && (
                <span className={styles.infoPanelDescription}>{s.description}</span>
              )}
            </div>
            <div className={styles.infoPanelMeta}>
              {s.norad_id && <span>NORAD {s.norad_id}</span>}
              {o.owner_name && <span>{o.owner_name}</span>}
              {deployDate && <span>Launched {deployDate}</span>}
              {ls.site_name && <span>{ls.site_name}</span>}
            </div>
          </div>
        </div>
        <div className={styles.infoPanelActions}>
          <button className={styles.infoPanelClose} onClick={onToggleMinimized}>
            {minimized
              ? <KeyboardArrowDownIcon sx={{ fontSize: 16 }} />
              : <KeyboardArrowUpIcon sx={{ fontSize: 16 }} />
            }
          </button>
          <button className={styles.infoPanelClose} onClick={onClose}>
            <CloseIcon sx={{ fontSize: 16 }} />
          </button>
        </div>
      </div>

      {!minimized && (
        <div className={styles.infoPanelGrid}>
          <div className={styles.infoPanelSection}>
            <span className={styles.infoPanelSectionTitle}>Identification</span>
            <InfoField label="Name" value={s.name} />
            <InfoField label="NORAD ID" value={s.norad_id} />
            <InfoField label="Orbit Type" value={s.orbit_type} />
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
      )}
    </div>
  );
}

// Page: Overview
function OverviewPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [allSatellites, setAllSatellites] = useState([]);
  const [highlightedSatellites, setHighlightedSatellites] = useState([]);
  const [selectedSatelliteId, setSelectedSatelliteId] = useState(null);
  const [infoPanelMinimized, setInfoPanelMinimized] = useState(false);
  const [globeExpanded, setGlobeExpanded] = useState(false);
  const globeControlsRef = React.useRef(null);

  // Search — list only, never affects globe
  const [searchTerm, setSearchTerm] = useState("");

  // Filters — affect both list and globe
  const [showFilters, setShowFilters] = useState(false);
  const [satelliteTypeFilter, setSatelliteTypeFilter] = useState("");
  const [orbitTypeFilter, setOrbitTypeFilter] = useState("");
  const [minNoradId, setMinNoradId] = useState("");
  const [maxNoradId, setMaxNoradId] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [keywordInput, setKeywordInput] = useState("");

  // Derived option lists
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

  const isFiltered =
    satelliteTypeFilter !== "" ||
    orbitTypeFilter !== "" ||
    minNoradId !== "" ||
    maxNoradId !== "" ||
    keywords.length > 0;

  const activeFilterCount =
    [satelliteTypeFilter, orbitTypeFilter, minNoradId, maxNoradId].filter(Boolean).length + keywords.length;

  const addKeyword = (e) => {
    if (e.key === "Enter" && keywordInput.trim()) {
      const kw = keywordInput.trim().toLowerCase();
      if (!keywords.includes(kw)) setKeywords((prev) => [...prev, kw]);
      setKeywordInput("");
    }
  };

  const removeKeyword = (kw) =>
    setKeywords((prev) => prev.filter((k) => k !== kw));

  const matchesKeywords = (sat) => {
    if (keywords.length === 0) return true;
    const fields = [
      sat.name,
      sat.satellite_type,
      sat.orbit_type,
      sat.norad_id,
      sat.object_id,
    ].map((f) => String(f ?? "").toLowerCase());
    return keywords.every((kw) => fields.some((f) => f.includes(kw)));
  };

  // Applies only filter values (no search) — used for globe visibility
  const globeFilteredIds = useMemo(() => {
    if (!isFiltered) return null;
    const minId = parseInt(minNoradId);
    const maxId = parseInt(maxNoradId);
    return new Set(
      allSatellites
        .filter((sat) => {
          if (satelliteTypeFilter && sat.satellite_type !== satelliteTypeFilter)
            return false;
          if (orbitTypeFilter && sat.orbit_type !== orbitTypeFilter)
            return false;
          const noradId = parseInt(sat.norad_id);
          if (
            minNoradId !== "" &&
            !isNaN(minId) &&
            (isNaN(noradId) || noradId < minId)
          )
            return false;
          if (
            maxNoradId !== "" &&
            !isNaN(maxId) &&
            (isNaN(noradId) || noradId > maxId)
          )
            return false;
          if (!matchesKeywords(sat)) return false;
          return true;
        })
        .map((s) => s.satellite_id),
    );
  }, [
    isFiltered,
    allSatellites,
    satelliteTypeFilter,
    orbitTypeFilter,
    minNoradId,
    maxNoradId,
    keywords,
  ]);

  // Applies both search and filters — used for the satellite list
  const filteredSatellites = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();
    return allSatellites.filter((sat) => {
      if (search) {
        const matchesSearch =
          sat.name.toLowerCase().includes(search) ||
          (sat.norad_id && sat.norad_id.toString().includes(search));
        if (!matchesSearch) return false;
      }
      if (globeFilteredIds !== null && !globeFilteredIds.has(sat.satellite_id))
        return false;
      return true;
    });
  }, [allSatellites, searchTerm, globeFilteredIds]);

  const clearFilters = () => {
    setSatelliteTypeFilter("");
    setOrbitTypeFilter("");
    setMinNoradId("");
    setMaxNoradId("");
    setKeywords([]);
    setKeywordInput("");
  };

  const handleSelectSatellite = (satelliteId) => {
    setHighlightedSatellites([satelliteId]);
    setSelectedSatelliteId(satelliteId);
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [counts, datasets, satellites] = await Promise.all([
          getSatelliteCounts(),
          getTotalDatasets(),
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
        });
      } catch (err) {
        console.error("Failed to fetch stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const selectStyle = {
    padding: "0.4rem 0.6rem",
    border: "1px solid #1e293b",
    borderRadius: "0.375rem",
    backgroundColor: "#0a1628",
    color: "#cbd5e1",
    fontSize: "0.8125rem",
    fontFamily: "inherit",
    outline: "none",
    width: "100%",
  };

  return (
    <div className={styles.overviewLayout}>
      {/* Stats row (always rendered for sizing) + Info Panel overlay */}
      <div className={styles.statsRowWrapper}>
        <div className={styles.statsRow} style={selectedSatelliteId && !infoPanelMinimized ? { visibility: "hidden", height: 0, overflow: "hidden", gap: 0 } : selectedSatelliteId ? { visibility: "hidden" } : undefined}>
          <StatCard
            label="Total Satellites"
            value={stats.total}
            icon={<SatelliteAltIcon sx={{ fontSize: 20 }} />}
            loading={loading}
          />
          <StatCard
            label="Earth Satellites"
            value={stats.earth}
            icon={<PublicIcon sx={{ fontSize: 20 }} />}
            loading={loading}
          />
          <StatCard
            label="Oceanic Satellites"
            value={stats.oceanic}
            icon={<WavesIcon sx={{ fontSize: 20 }} />}
            loading={loading}
          />
          <StatCard
            label="Navigation Satellites"
            value={stats.navigation}
            icon={<ExploreIcon sx={{ fontSize: 20 }} />}
            loading={loading}
          />
          <StatCard
            label="Internet Satellites"
            value={stats.internet}
            icon={<WifiIcon sx={{ fontSize: 20 }} />}
            loading={loading}
          />
          <StatCard
            label="Research Satellites"
            value={stats.research}
            icon={<ScienceIcon sx={{ fontSize: 20 }} />}
            loading={loading}
          />
          <StatCard
            label="Weather Satellites"
            value={stats.weather}
            icon={<AirIcon sx={{ fontSize: 20 }} />}
            loading={loading}
          />
        </div>
        {selectedSatelliteId && (
          <SatelliteInfoPanel
            satelliteId={selectedSatelliteId}
            minimized={infoPanelMinimized}
            onToggleMinimized={() => setInfoPanelMinimized((m) => !m)}
            onClose={() => {
              setSelectedSatelliteId(null);
              setHighlightedSatellites([]);
            }}
          />
        )}
      </div>

      {/* Globe + Satellite Panel */}
      <div className={styles.globeRow}>
        {/* Left: Globe */}
        <div className={`${styles.globeCard} ${globeExpanded ? styles.globeCardExpanded : ""}`}>
          <div className={styles.globeCardBody}>
            <SatelliteGlobe
              highlightedSatellites={highlightedSatellites}
              visibleSatelliteIds={globeFilteredIds}
              onReady={(controls) => { globeControlsRef.current = controls; }}
            />
            <div className={styles.globeControls}>
              <button
                className={styles.globeControlBtn}
                onClick={() => globeControlsRef.current?.resetCamera()}
                title="Reset view"
              >
                <MyLocationIcon sx={{ fontSize: 16 }} />
              </button>
              <button
                className={styles.globeControlBtn}
                onClick={() => setGlobeExpanded((e) => !e)}
                title={globeExpanded ? "Exit fullscreen" : "Expand"}
              >
                {globeExpanded
                  ? <FullscreenExitIcon sx={{ fontSize: 16 }} />
                  : <FullscreenIcon sx={{ fontSize: 16 }} />
                }
              </button>
            </div>
          </div>
        </div>

        {/* Right: Satellite Search Panel */}
        <div className={styles.satellitePanel}>
          {/* Panel Header */}
          <div className={styles.satellitePanelHeader}>
            <span className={styles.satellitePanelTitle}>Satellites</span>
            <span className={styles.satellitePanelCount}>
              {filteredSatellites.length} / {allSatellites.length}
            </span>
          </div>

          {/* Search + Filter row */}
          <div className={styles.panelSearchWrapper}>
            <SearchIcon
              sx={{ fontSize: 15, color: "#475569", flexShrink: 0 }}
            />
            <input
              className={styles.panelSearchInput}
              type="text"
              placeholder="Search by name or NORAD ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button
              className={`${styles.filterToggleBtn} ${showFilters ? styles.filterToggleActive : ""}`}
              onClick={() => setShowFilters((p) => !p)}
            >
              Filters
              {activeFilterCount > 0 && (
                <span className={styles.filterBadge}>{activeFilterCount}</span>
              )}
            </button>
          </div>

          {/* Expandable Filters */}
          {showFilters && (
            <div className={styles.panelFilters}>
              <div className={styles.panelFiltersLabel}>
                <span>Filters — also apply to globe</span>
                <button
                  className={styles.panelFiltersClear}
                  onClick={clearFilters}
                  style={{ visibility: isFiltered ? "visible" : "hidden" }}
                >
                  <CloseIcon sx={{ fontSize: 12 }} /> Clear
                </button>
              </div>
              <div className={styles.panelFiltersRow}>
                <select
                  value={satelliteTypeFilter}
                  onChange={(e) => setSatelliteTypeFilter(e.target.value)}
                  style={selectStyle}
                >
                  <option value="">All Categories</option>
                  {satelliteTypes.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
                <select
                  value={orbitTypeFilter}
                  onChange={(e) => setOrbitTypeFilter(e.target.value)}
                  style={selectStyle}
                >
                  <option value="">All Orbits</option>
                  {orbitTypes.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </div>
              <div className={styles.panelFiltersRow}>
                <NumInput placeholder="Min NORAD ID" value={minNoradId} onChange={setMinNoradId} />
                <NumInput placeholder="Max NORAD ID" value={maxNoradId} onChange={setMaxNoradId} />
              </div>
              <div className={styles.keywordRow}>
                {keywords.map((kw) => (
                  <span key={kw} className={styles.keywordTag}>
                    {kw}
                    <button
                      className={styles.keywordTagRemove}
                      onClick={() => removeKeyword(kw)}
                    >
                      <CloseIcon sx={{ fontSize: 10 }} />
                    </button>
                  </span>
                ))}
                <input
                  className={styles.keywordInput}
                  type="text"
                  placeholder={
                    keywords.length === 0
                      ? "Filter by keyword, press Enter to add..."
                      : "Add another..."
                  }
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  onKeyDown={addKeyword}
                />
              </div>
            </div>
          )}

          {/* Satellite List */}
          <div className={styles.satelliteList}>
            {loading ? (
              <div className={styles.satelliteListEmpty}>
                Loading satellites...
              </div>
            ) : filteredSatellites.length === 0 ? (
              <div className={styles.satelliteListEmpty}>
                No satellites match filters
              </div>
            ) : (
              filteredSatellites.map((sat) => (
                <div
                  key={sat.satellite_id}
                  className={`${styles.satelliteItem} ${selectedSatelliteId === sat.satellite_id ? styles.satelliteItemSelected : ""}`}
                  onClick={() => handleSelectSatellite(sat.satellite_id)}
                >
                  <div
                    className={styles.satelliteItemDot}
                    style={
                      user?.level_access >= 3 && sat.review_status === "pending"
                        ? { backgroundColor: "#f59e0b" }
                        : undefined
                    }
                  />
                  <div className={styles.satelliteItemInfo}>
                    <span className={styles.satelliteItemName}>{sat.name}</span>
                    <span className={styles.satelliteItemMeta}>
                      {sat.satellite_type} · {sat.norad_id}
                    </span>
                  </div>
                  <span className={styles.satelliteItemOrbit}>
                    {sat.orbit_type}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
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
      case "datasets":
        return <Datasets />;
      case "userProfile":
        return <UserProfile />;
      case "visualizations":
        return <PlaceholderPage title="Visualizations" />;
      case "reviews":
        return <Reviews />;
      case "manageSatellites":
        return <ManageSatellites />;
      case "manageDatasets":
        return <ManageDatasets />;
      case "settings":
        return <Settings />;
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
