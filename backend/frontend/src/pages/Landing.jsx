// react imports
import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";

// icon imports
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import PublicIcon from "@mui/icons-material/Public";
import WavesIcon from "@mui/icons-material/Waves";
import ExploreIcon from "@mui/icons-material/Explore";
import WifiIcon from "@mui/icons-material/Wifi";
import ScienceIcon from "@mui/icons-material/Science";
import AirIcon from "@mui/icons-material/Air";

// component imports
import SatelliteGlobe from "../components/satellite/SatelliteGlobe";

// style imports
import styles from "../styles/Landing.module.css";

// api imports
import { getSatelliteCounts, getAllSatellites } from "../api/satelliteService";
import { getTotalDatasets } from "../api/datasetService";
import { SATELLITE_CATEGORY_COLORS } from "../constants/satelliteColors";

// stat card component
function StatCard({ label, value, icon, loading }) {
  return (
    <div className={styles.statCard}>
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

// default function
export default function Landing() {
  // component fields
  const navigate = useNavigate();
  const [counts, setCounts] = useState({});
  const [totalDatasets, setTotalDatasets] = useState(null);
  const [allSatellites, setAllSatellites] = useState([]);
  const [loading, setLoading] = useState(true);

  // use effect to get all the data in our frontend fields from the apis
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [satelliteCounts, datasets, satellites] = await Promise.all([
          getSatelliteCounts(),
          getTotalDatasets(),
          getAllSatellites(),
        ]);
        setCounts(satelliteCounts);
        setTotalDatasets(datasets);
        setAllSatellites(satellites);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const satelliteTypeById = useMemo(
    () =>
      Object.fromEntries(
        allSatellites.map((sat) => [
          String(sat.satellite_id),
          sat.satellite_type,
        ]),
      ),
    [allSatellites],
  );

  // stats list for stat cards on the landing page
  const stats = [
    {
      label: "Total Satellites",
      value: counts.total,
      icon: <SatelliteAltIcon sx={{ fontSize: "inherit" }} />,
    },
    {
      label: "Earth Satellites",
      value: counts.earth_science,
      icon: (
        <PublicIcon
          sx={{ fontSize: "inherit", color: SATELLITE_CATEGORY_COLORS["earth science"] }}
        />
      ),
    },
    {
      label: "Oceanic Satellites",
      value: counts.oceanic_science,
      icon: (
        <WavesIcon
          sx={{ fontSize: "inherit", color: SATELLITE_CATEGORY_COLORS["oceanic science"] }}
        />
      ),
    },
    {
      label: "Navigation",
      value: counts.navigation,
      icon: (
        <ExploreIcon
          sx={{ fontSize: "inherit", color: SATELLITE_CATEGORY_COLORS.navigation }}
        />
      ),
    },
    {
      label: "Internet Satellites",
      value: counts.internet,
      icon: (
        <WifiIcon
          sx={{ fontSize: "inherit", color: SATELLITE_CATEGORY_COLORS.internet }}
        />
      ),
    },
    {
      label: "Research Satellites",
      value: counts.research,
      icon: (
        <ScienceIcon
          sx={{ fontSize: "inherit", color: SATELLITE_CATEGORY_COLORS.research }}
        />
      ),
    },
    {
      label: "Weather Satellites",
      value: counts.weather,
      icon: (
        <AirIcon
          sx={{ fontSize: "inherit", color: SATELLITE_CATEGORY_COLORS.weather }}
        />
      ),
    },
  ];

  // main component structure
  return (
    <div className={styles.page}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.logo}>
            <SatelliteAltIcon
              sx={{ fontSize: 32 }}
              className={styles.logoIcon}
            />
            <h1 className={styles.logoText}>SatTrack</h1>
          </div>
          <div className={styles.headerActions}>
            <button
              onClick={() => navigate("/login")}
              className={styles.loginButton}
            >
              <LockOutlinedIcon sx={{ fontSize: 16 }} />
              Login
            </button>
          </div>
        </div>
      </header>

      {/* Two column layout */}
      <div className={styles.content}>
        {/* Left: Hero text + Globe */}
        <div className={styles.leftColumn}>
          <div>
            <h2 className={styles.heroTitle}>Real-Time Satellite Tracking</h2>
            <p className={styles.heroSubtitle}>
              Monitor global satellite networks with live position data,
              trajectory visualization, and comprehensive dataset management
              {totalDatasets ? ` featuring ${totalDatasets} datasets` : ""}
            </p>
          </div>
          <div className={styles.globeWrapper}>
            <SatelliteGlobe satelliteTypeById={satelliteTypeById} />
          </div>
        </div>

        {/* Right: Stats */}
        <div className={styles.rightColumn}>
          <h2 className={styles.statsTitle}>Satellite Statistics</h2>
          <div className={styles.statsGrid}>
            {stats.map((stat) => (
              <StatCard
                key={stat.label}
                label={stat.label}
                value={stat.value}
                icon={stat.icon}
                loading={loading}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
