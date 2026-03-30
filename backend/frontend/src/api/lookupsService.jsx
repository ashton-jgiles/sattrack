// import get for the lookup services
import { get } from "./api";

// get interfaces for satellite owners, launch vehicles, launch sites and communication stations
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
