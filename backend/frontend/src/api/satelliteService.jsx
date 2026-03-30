// import get from api interface
import { get } from "./api";

// get all satellites to get the list of all satellites in the database
export const getAllSatellites = async () => {
  const data = await get(`/satellite/satellites/`);
  return data;
};

// get one satellite takes an id to get a single satellite
export const getOneSatellite = async (id) => {
  const data = await get(`/satellite/${id}/`);
  return data;
};

// get total satellites and each subclass satellites call the associated endpoits
export const getTotalSatellites = async () => {
  const data = await get(`/satellite/totalSatellites/`);
  return data.total;
};

export const getTotalEarthSatellites = async () => {
  const data = await get(`/satellite/totalEarthSatellites/`);
  return data.total;
};

export const getTotalOceanicSatellites = async () => {
  const data = await get(`/satellite/totalOceanicSatellites/`);
  return data.total;
};

export const getTotalNavigationSatellites = async () => {
  const data = await get(`/satellite/totalNavigationSatellites/`);
  return data.total;
};

export const getTotalInternetSatellites = async () => {
  const data = await get(`/satellite/totalInternetSatellites/`);
  return data.total;
};

export const getTotalWeatherSatellites = async () => {
  const data = await get(`/satellite/totalWeatherSatellites/`);
  return data.total;
};

export const getTotalResearchSatellites = async () => {
  const data = await get(`/satellite/totalResearchSatellites/`);
  return data.total;
};

// get recent deployments interface gets all satellites deployed in last 5 years
export const getRecentDeployments = async () => {
  const data = await get(`/satellite/recentDeployments/`);
  return data;
};

// get satellite profile gives one row of all sattelite info, owner, launch, vehicle, comm station for a satellite
export const getSatelliteProfile = async (id) => {
  const data = await get(`/satellite/${id}/profile/`);
  return data;
};
