import { get } from "./api";

export const getAllSatellites = async () => {
  const data = await get(`/satellite/satellites/`);
  return data;
};

export const getOneSatellite = async (id) => {
  const data = await get(`/satellite/${id}/`);
  return data;
};

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
