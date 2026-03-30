// import get for our apis
import { get } from "./api";

// gets one page of satellite trajectory data for the globe visualization
export const getSatellitePositionsPage = async (page = 1, pageSize = 100) => {
  const data = await get(`/satellite/positions/?page=${page}&page_size=${pageSize}`);
  return data;
};
