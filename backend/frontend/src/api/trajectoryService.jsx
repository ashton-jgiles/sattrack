// import get for our apis
import { get } from "./api";

// gets the postions of all satellites in trajectory table for the globe visualization
export const getAllSatellitePositions = async () => {
  const data = await get("/satellite/positions/");
  return data;
};
