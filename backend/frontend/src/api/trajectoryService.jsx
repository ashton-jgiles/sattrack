import { get } from "./api";

export const getAllSatellitePositions = async () => {
  const data = await get("/satellite/positions/");
  return data;
};
