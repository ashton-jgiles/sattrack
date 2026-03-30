import { get } from "./api";

export const getAllOwners = async () => {
  const data = await get("/lookups/owners/");
  return data;
};
export const getAllVehicles = async () => {
  const data = await get("/lookups/vehicles/");
  return data;
};
export const getAllLaunchSites = async () => {
  const data = await get("/lookups/sites/");
  return data;
};
export const getAllStations = async () => {
  const data = await get("/lookups/stations/");
  return data;
};
