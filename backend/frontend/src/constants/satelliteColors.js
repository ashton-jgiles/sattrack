const SATELLITE_CATEGORY_COLORS = {
  "earth science": "#f59e0b",
  "oceanic science": "#a855f7",
  navigation: "#07b346",
  internet: "#ec4899",
  research: "#ef4444",
  weather: "#06bedf",
};

//   "earth science": "#07ae44",
//   "oceanic science": "#06bedf",
//   navigation: "#f59e0b",
//   internet: "#ec4899",
//   research: "#ef4444",
//   weather: "#a855f7",

const DEFAULT_SATELLITE_CATEGORY_COLOR = "#22c55e";

function getSatelliteCategoryColor(satelliteType) {
  const key = String(satelliteType ?? "")
    .trim()
    .toLowerCase();
  return SATELLITE_CATEGORY_COLORS[key] ?? DEFAULT_SATELLITE_CATEGORY_COLOR;
}

module.exports = {
  SATELLITE_CATEGORY_COLORS,
  DEFAULT_SATELLITE_CATEGORY_COLOR,
  getSatelliteCategoryColor,
};
