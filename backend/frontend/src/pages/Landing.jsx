// react imports
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// icon imports
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";

// component imports
import SatelliteGlobe from "../components/SatelliteGlobe";

// style imports
import styles from "../styles/Landing.module.css";

// api imports
import { getSatelliteCounts } from "../api/satelliteService";
import { getTotalDatasets } from "../api/datasetService";

// stat card component
function StatCard({ label, value, loading }) {
  return (
    <div className={styles.statCard}>
      <span className={styles.statLabel}>{label}</span>
      {loading ? (
        <span className={styles.statLoading}>Loading...</span>
      ) : (
        <span className={styles.statValue}>{value}</span>
      )}
    </div>
  );
}

// default function
export default function Landing() {
  // component fields
  const navigate = useNavigate();
  const [totalSatellites, setTotalSatellites] = useState(null);
  const [totalEarthSatellites, setTotalEarthSatellites] = useState(null);
  const [totalOceanicSatellites, setTotalOceanicSatellites] = useState(null);
  const [totalNavigationSatellites, setTotalNavigationSatellites] =
    useState(null);
  const [totalInternetSatellites, setTotalInternetSatellites] = useState(null);
  const [totalWeatherSatellites, setTotalWeatherSatellites] = useState(null);
  const [totalResearchSatellites, setTotalResearchSatellites] = useState(null);
  const [totalDatasets, setTotalDatasets] = useState(null);
  const [loading, setLoading] = useState(true);

  // use effect to get all the data in our frontend fields from the apis
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [counts, datasets] = await Promise.all([
          getSatelliteCounts(),
          getTotalDatasets(),
        ]);
        setTotalSatellites(counts.total);
        setTotalDatasets(datasets);
        setTotalEarthSatellites(counts.earth_science);
        setTotalOceanicSatellites(counts.oceanic_science);
        setTotalNavigationSatellites(counts.navigation);
        setTotalInternetSatellites(counts.internet);
        setTotalWeatherSatellites(counts.weather);
        setTotalResearchSatellites(counts.research);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  // stats list for stat cards on the landing page
  const stats = [
    { label: "Total Satellites", value: totalSatellites },
    { label: "Total Datasets", value: totalDatasets },
    { label: "Earth Satellites", value: totalEarthSatellites },
    { label: "Oceanic Satellites", value: totalOceanicSatellites },
    { label: "Navigation", value: totalNavigationSatellites },
    { label: "Internet Satellites", value: totalInternetSatellites },
    { label: "Research Satellites", value: totalResearchSatellites },
    { label: "Weather Satellites", value: totalWeatherSatellites },
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
            </p>
          </div>
          <div className={styles.globeWrapper}>
            <SatelliteGlobe />
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
                loading={loading}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
