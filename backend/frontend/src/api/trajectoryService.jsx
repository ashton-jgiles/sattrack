// import get for our apis
import { get, post } from "./api";

// gets one page of satellite trajectory data for the globe visualization
export const getSatellitePositionsPage = async (page = 1, pageSize = 100) => {
  const data = await get(
    `/satellite/positions/?page=${page}&page_size=${pageSize}`,
  );
  return data;
};

// trigger a full trajectory update for all active satellites
export const updateTrajectories = async () => {
  return await post(`/settings/trajectory/update/`, {});
};
