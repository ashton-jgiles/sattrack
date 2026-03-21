import { get } from "./api";

export const getAllSatellites = () => get("/satellite/satellites/");

export const getOneSatellites = () => get("/satellite/${id}/");
