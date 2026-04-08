// react imports
import React, { useEffect, useState, useMemo } from "react";

// recharts imports
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";

// api imports
import {
  getAllSatellites,
  getRecentDeployments,
} from "../api/satelliteService";

// style imports
import styles from "../styles/Visualizations.module.css";

//  Palette
const PALETTE = [
  "#3b82f6", // blue
  "#22c55e", // green
  "#f59e0b", // amber
  "#a855f7", // purple
  "#ef4444", // red
  "#06b6d4", // cyan
  "#f97316", // orange
  "#10b981", // emerald
];

// Global category color mapping
const CATEGORY_COLORS = {
  Navigation: "#3b82f6",
  Internet: "#22c55e",
  "Earth Science": "#f59e0b",
  Weather: "#a855f7",
  "Oceanic Science": "#ef4444",
  Research: "#06b6d4",
};

// Normalize + lookup helper
const normalize = (str) => str?.trim().toLowerCase();

const getColor = (name, index = 0) => {
  const key = Object.keys(CATEGORY_COLORS).find(
    (k) => normalize(k) === normalize(name),
  );
  return key ? CATEGORY_COLORS[key] : PALETTE[index % PALETTE.length];
};

//  Shared tooltip style
const tooltipStyle = {
  backgroundColor: "#0a1628",
  border: "1px solid #1e293b",
  borderRadius: "0.5rem",
  color: "#cbd5e1",
  fontSize: "0.8125rem",
  fontFamily: "var(--font-body)",
};

const labelStyle = { color: "#94a3b8", fontSize: "0.75rem" };

//  Chart card wrapper
function ChartCard({ title, subtitle, children }) {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.cardTitle}>{title}</span>
        {subtitle && <span className={styles.cardSubtitle}>{subtitle}</span>}
      </div>
      <div className={styles.cardBody}>{children}</div>
    </div>
  );
}

//  Custom pie label
function PieLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }) {
  if (percent < 0.04) return null;
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.55;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text
      x={x}
      y={y}
      fill="#fff"
      textAnchor="middle"
      dominantBaseline="central"
      style={{
        fontSize: "0.7rem",
        fontFamily: "var(--font-display)",
        fontWeight: 600,
      }}
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
}

//  Loading skeleton
function Skeleton() {
  return <div className={styles.skeleton} />;
}

// Main page
export default function Visualizations() {
  const [satellites, setSatellites] = useState([]);
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([getAllSatellites(), getRecentDeployments()])
      .then(([sats, deps]) => {
        setSatellites(sats);
        setDeployments(deps);
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to load satellite data.");
      })
      .finally(() => setLoading(false));
  }, []);

  // Orbit type breakdown (LEO / MEO / GEO)
  const orbitData = useMemo(() => {
    const counts = {};
    satellites.forEach((s) => {
      const o = s.orbit_type || "Unknown";
      counts[o] = (counts[o] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [satellites]);

  // Satellite type breakdown
  const typeData = useMemo(() => {
    const counts = {};
    satellites.forEach((s) => {
      const t = s.satellite_type || "Unknown";
      counts[t] = (counts[t] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [satellites]);

  // Classification breakdown
  const classData = useMemo(() => {
    const map = { U: "Unclassified", C: "Classified", S: "Secret" };
    const counts = {};
    satellites.forEach((s) => {
      const label = map[s.classification] || s.classification || "Unknown";
      counts[label] = (counts[label] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [satellites]);

  // Altitude distribution buckets
  const altitudeData = useMemo(() => {
    const buckets = {
      "< 500 km": 0,
      "500–1000 km": 0,
      "1000–5000 km": 0,
      "5000–20000 km": 0,
      "> 20000 km": 0,
      Unknown: 0,
    };
    satellites.forEach((s) => {
      const alt = parseFloat(s.altitude);
      if (isNaN(alt)) {
        buckets["Unknown"]++;
        return;
      }
      if (alt < 500) buckets["< 500 km"]++;
      else if (alt < 1000) buckets["500–1000 km"]++;
      else if (alt < 5000) buckets["1000–5000 km"]++;
      else if (alt < 20000) buckets["5000–20000 km"]++;
      else buckets["> 20000 km"]++;
    });
    return Object.entries(buckets)
      .filter(([, v]) => v > 0)
      .map(([name, value]) => ({ name, value }));
  }, [satellites]);

  // Deployments per year (last 5 years from recentDeployments)
  const deploymentsByYear = useMemo(() => {
    const counts = {};
    deployments.forEach((d) => {
      if (!d.deploy_date_time) return;
      const year = new Date(d.deploy_date_time).getFullYear().toString();
      counts[year] = (counts[year] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([year, count]) => ({ year, count }))
      .sort((a, b) => a.year.localeCompare(b.year));
  }, [deployments]);

  // Satellite type vs orbit cross-breakdown
  const radarData = useMemo(() => {
    const orbitOrder = ["LEO", "MEO", "GEO", "HEO", "SSO"];
    const typeCounts = {};
    satellites.forEach((s) => {
      const orbit = s.orbit_type || "Other";
      const type = s.satellite_type || "Unknown";
      if (!typeCounts[orbit]) typeCounts[orbit] = {};
      typeCounts[orbit][type] = (typeCounts[orbit][type] || 0) + 1;
    });
    const allTypes = [
      ...new Set(satellites.map((s) => s.satellite_type || "Unknown")),
    ];
    return orbitOrder
      .filter((o) => typeCounts[o])
      .map((orbit) => {
        const row = { orbit };
        allTypes.forEach((t) => {
          row[t] = typeCounts[orbit]?.[t] || 0;
        });
        return row;
      });
  }, [satellites]);

  const radarTypes = useMemo(
    () => [...new Set(satellites.map((s) => s.satellite_type || "Unknown"))],
    [satellites],
  );

  if (error) {
    return (
      <div className={styles.errorState}>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <h2 className={styles.pageTitle}>Visualizations</h2>
        <p className={styles.pageSubtitle}>
          Charts derived from live satellite database data
          {!loading && ` · ${satellites.length} satellites`}
        </p>
      </div>

      <div className={styles.grid}>
        {/* 1. Orbit type pie */}
        <ChartCard
          title="Orbit Type Distribution"
          subtitle="LEO · MEO · GEO · other"
        >
          {loading ? (
            <Skeleton />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={orbitData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  labelLine={false}
                  label={PieLabel}
                >
                  {orbitData.map((entry, i) => (
                    <Cell key={i} fill={getColor(entry.name, i)} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} labelStyle={labelStyle} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "0.75rem", color: "#94a3b8" }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* 2. Satellite type bar */}
        <ChartCard
          title="Satellites by Type"
          subtitle="Count per mission category"
        >
          {loading ? (
            <Skeleton />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart
                data={typeData}
                margin={{ top: 4, right: 8, left: -16, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "#64748b", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  interval={0}
                  angle={-20}
                  textAnchor="end"
                  height={48}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  cursor={{ fill: "rgba(59,130,246,0.08)" }}
                />
                <Bar dataKey="value" name="Satellites" radius={[4, 4, 0, 0]}>
                  {typeData.map((entry, i) => (
                    <Cell key={i} fill={getColor(entry.name, i)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* 3. Classification donut */}
        <ChartCard
          title="Classification Breakdown"
          subtitle="Unclassified · Classified · Secret"
        >
          {loading ? (
            <Skeleton />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={classData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  labelLine={false}
                  label={PieLabel}
                >
                  {classData.map((entry, i) => (
                    <Cell key={i} fill={getColor(entry.name, i)} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "0.75rem", color: "#94a3b8" }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* 4. Altitude distribution bar */}
        <ChartCard
          title="Altitude Distribution"
          subtitle="Satellites grouped by orbital altitude (km)"
        >
          {loading ? (
            <Skeleton />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart
                data={altitudeData}
                margin={{ top: 4, right: 8, left: -16, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                  interval={0}
                  angle={-15}
                  textAnchor="end"
                  height={48}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  cursor={{ fill: "rgba(59,130,246,0.08)" }}
                />
                <Bar dataKey="value" name="Satellites" radius={[4, 4, 0, 0]}>
                  {altitudeData.map((entry, i) => (
                    <Cell key={i} fill={getColor(entry.name, i)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* 5. Deployments per year line chart */}
        <ChartCard
          title="Deployments Per Year"
          subtitle="Satellites launched in the last 5 years"
        >
          {loading ? (
            <Skeleton />
          ) : deploymentsByYear.length === 0 ? (
            <div className={styles.emptyState}>
              No deployment data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart
                data={deploymentsByYear}
                margin={{ top: 4, right: 16, left: -16, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="year"
                  tick={{ fill: "#64748b", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip contentStyle={tooltipStyle} />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="Deployments"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: "#3b82f6", r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* 6. Radar: orbit vs satellite type */}
        <ChartCard
          title="Orbit × Mission Type"
          subtitle="How mission types are distributed across orbits"
        >
          {loading ? (
            <Skeleton />
          ) : radarData.length === 0 ? (
            <div className={styles.emptyState}>Not enough data</div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={radarData} cx="50%" cy="50%" outerRadius={90}>
                <PolarGrid stroke="#1e293b" />
                <PolarAngleAxis
                  dataKey="orbit"
                  tick={{ fill: "#64748b", fontSize: 11 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  tick={{ fill: "#475569", fontSize: 9 }}
                  axisLine={false}
                  tickLine={false}
                />
                {radarTypes.map((type, i) => (
                  <Radar
                    key={type}
                    name={type}
                    dataKey={type}
                    stroke={getColor(type, i)}
                    fill={getColor(type, i)}
                    fillOpacity={0.15}
                    strokeWidth={1.5}
                  />
                ))}
                <Tooltip contentStyle={tooltipStyle} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "0.75rem", color: "#94a3b8" }}
                />
              </RadarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>
    </div>
  );
}
