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

// get satellite counts returns total and per-type counts in a single request
// { total, earth_science, oceanic_science, weather, navigation, internet, research }
export const getSatelliteCounts = async () => {
  const data = await get(`/satellite/counts/`);
  return data;
};

// get recent deployments interface gets all satellites deployed in last 5 years
export const getRecentDeployments = async () => {
  const data = await get(`/satellite/recent_deployments/`);
  return data;
};

// get satellite profile gives one row of all sattelite info, owner, launch, vehicle, comm station for a satellite
export const getSatelliteProfile = async (id) => {
  const data = await get(`/satellite/${id}/profile/`);
  return data;
};

// get one page of satellite trajectory data for the globe visualization
export const getSatellitePositionsPage = async (page = 1, pageSize = 100) => {
  const data = await get(`/satellite/positions/?page=${page}&page_size=${pageSize}`);
  return data;
};
