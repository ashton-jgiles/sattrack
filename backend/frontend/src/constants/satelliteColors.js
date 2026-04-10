const SATELLITE_CATEGORY_COLORS = {
  "earth science": "#ffc35b",
  "oceanic science": "#a855f7",
  navigation: "#07b346",
  internet: "#ff7cbe",
  research: "#e11b1b",
  weather: "#38d7f3",
};

// default satellite color
const DEFAULT_SATELLITE_CATEGORY_COLOR = "#22c55e";

// function to get the satellite color based off the type
function getSatelliteCategoryColor(satelliteType) {
  const key = String(satelliteType ?? "")
    .trim()
    .toLowerCase();
  return SATELLITE_CATEGORY_COLORS[key] ?? DEFAULT_SATELLITE_CATEGORY_COLOR;
}

// export the constants and function
module.exports = {
  SATELLITE_CATEGORY_COLORS,
  DEFAULT_SATELLITE_CATEGORY_COLOR,
  getSatelliteCategoryColor,
};
