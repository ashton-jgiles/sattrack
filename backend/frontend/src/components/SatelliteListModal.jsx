// react imports
import React, { useState, useMemo } from "react";
import ReactDOM from "react-dom";

// icon imports
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import SearchIcon from "@mui/icons-material/Search";

// style imports
import styles from "../styles/SatelliteProfileModal.module.css";

// satellite list modal for displaying satellites in a category
export default function SatelliteListModal({
  category,
  satellites,
  onClose,
  onSatelliteClick,
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [satelliteTypeFilter, setSatelliteTypeFilter] = useState("");
  const [orbitTypeFilter, setOrbitTypeFilter] = useState("");
  const [minAltitude, setMinAltitude] = useState("");
  const [maxAltitude, setMaxAltitude] = useState("");
  const [minVelocity, setMinVelocity] = useState("");
  const [maxVelocity, setMaxVelocity] = useState("");

  const categoryTitles = {
    total: "Total Satellites",
    earth: "Earth Satellites",
    oceanic: "Oceanic Satellites",
    navigation: "Navigation Satellites",
    internet: "Internet Satellites",
    research: "Research Satellites",
    weather: "Weather Satellites",
  };

  const title = categoryTitles[category] || "Satellites";

  const satelliteTypes = useMemo(
    () => [...new Set(satellites.map((sat) => sat.satellite_type).filter(Boolean))],
    [satellites],
  );

  const orbitTypes = useMemo(
    () => [...new Set(satellites.map((sat) => sat.orbit_type).filter(Boolean))],
    [satellites],
  );

  const filteredSatellites = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();
    const minAlt = parseFloat(minAltitude);
    const maxAlt = parseFloat(maxAltitude);
    const minVel = parseFloat(minVelocity);
    const maxVel = parseFloat(maxVelocity);

    return satellites.filter((sat) => {
      if (search) {
        const matchesSearch =
          sat.name.toLowerCase().includes(search) ||
          (sat.norad_id && sat.norad_id.toString().includes(search));
        if (!matchesSearch) return false;
      }

      if (satelliteTypeFilter && sat.satellite_type !== satelliteTypeFilter) {
        return false;
      }

      if (orbitTypeFilter && sat.orbit_type !== orbitTypeFilter) {
        return false;
      }

      const altitude = Number(sat.altitude);
      if (!Number.isNaN(minAlt) && !Number.isNaN(altitude) && altitude < minAlt) {
        return false;
      }
      if (!Number.isNaN(maxAlt) && !Number.isNaN(altitude) && altitude > maxAlt) {
        return false;
      }
      if (!Number.isNaN(minAlt) && Number.isNaN(altitude) && minAltitude !== "") {
        return false;
      }
      if (!Number.isNaN(maxAlt) && Number.isNaN(altitude) && maxAltitude !== "") {
        return false;
      }

      const velocity = Number(sat.velocity);
      if (!Number.isNaN(minVel) && !Number.isNaN(velocity) && velocity < minVel) {
        return false;
      }
      if (!Number.isNaN(maxVel) && !Number.isNaN(velocity) && velocity > maxVel) {
        return false;
      }
      if (!Number.isNaN(minVel) && Number.isNaN(velocity) && minVelocity !== "") {
        return false;
      }
      if (!Number.isNaN(maxVel) && Number.isNaN(velocity) && maxVelocity !== "") {
        return false;
      }

      return true;
    });
  }, [
    satellites,
    searchTerm,
    satelliteTypeFilter,
    orbitTypeFilter,
    minAltitude,
    maxAltitude,
    minVelocity,
    maxVelocity,
  ]);

  return ReactDOM.createPortal(
    <div className={styles.confirmBackdrop}>
      <div className={styles.confirmModal} style={{ maxWidth: "600px", maxHeight: "80vh", overflowY: "auto" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <SatelliteAltIcon sx={{ fontSize: 22, color: "#3b82f6" }} />
          <span className={styles.confirmTitle}>{title}</span>
        </div>

        {/* Search Input */}
        <div style={{ marginTop: "1rem", position: "relative" }}>
          <SearchIcon sx={{ position: "absolute", left: "0.5rem", top: "50%", transform: "translateY(-50%)", color: "#94a3b8" }} />
          <input
            type="text"
            placeholder="Search by name or NORAD ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem 0.5rem 0.5rem 2rem",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              color: "#ffffff",
              fontSize: "0.875rem",
            }}
          />
        </div>

        {/* Filters */}
        <div
          style={{
            marginTop: "1rem",
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "0.75rem",
          }}
        >
          <select
            value={satelliteTypeFilter}
            onChange={(e) => setSatelliteTypeFilter(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              color: "#ffffff",
            }}
          >
            <option value="">All Categories</option>
            {satelliteTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
          <select
            value={orbitTypeFilter}
            onChange={(e) => setOrbitTypeFilter(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              color: "#ffffff",
            }}
          >
            <option value="">All Orbits</option>
            {orbitTypes.map((orbit) => (
              <option key={orbit} value={orbit}>
                {orbit}
              </option>
            ))}
          </select>
        </div>

        <div
          style={{
            marginTop: "0.75rem",
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "0.75rem",
          }}
        >
          <input
            type="number"
            placeholder="Min altitude"
            value={minAltitude}
            onChange={(e) => setMinAltitude(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              color: "#ffffff",
            }}
          />
          <input
            type="number"
            placeholder="Max altitude"
            value={maxAltitude}
            onChange={(e) => setMaxAltitude(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              color: "#ffffff",
            }}
          />
        </div>

        <div
          style={{
            marginTop: "0.75rem",
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "0.75rem",
          }}
        >
          <input
            type="number"
            placeholder="Min velocity"
            value={minVelocity}
            onChange={(e) => setMinVelocity(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              color: "#ffffff",
            }}
          />
          <input
            type="number"
            placeholder="Max velocity"
            value={maxVelocity}
            onChange={(e) => setMaxVelocity(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              backgroundColor: "#0f172a",
              color: "#ffffff",
            }}
          />
        </div>

        <div style={{ marginTop: "1rem" }}>
          {filteredSatellites.length === 0 ? (
            <p>No satellites found{searchTerm ? " matching your search" : ""}.</p>
          ) : (
            <ul style={{ listStyle: "none", padding: 0 }}>
              {filteredSatellites.map((sat) => (
                <li
                  key={sat.satellite_id}
                  style={{
                    padding: "0.5rem 0",
                    borderBottom: "1px solid #e5e7eb",
                    cursor: "pointer",
                    transition: "background-color 0.2s",
                  }}
                  onClick={() => onSatelliteClick && onSatelliteClick(sat.satellite_id)}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#1e293b"}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                >
                  <strong>{sat.name}</strong> (NORAD: {sat.norad_id})
                  <br />
                  <small>
                    Status: {sat.status}, Orbit: {sat.orbit_type}
                    {sat.altitude ? `, Altitude: ${sat.altitude}` : ""}
                    {sat.velocity ? `, Velocity: ${sat.velocity}` : ""}
                  </small>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className={styles.confirmActions} style={{ marginTop: "1rem" }}>
          <button className={styles.cancelButton} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}