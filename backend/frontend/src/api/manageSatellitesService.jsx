// import get post and del for all our interfaces
import { get, post, del } from "./api";

// delete satellites interface to call the delete satellite endpoint
export const deleteSatellite = async (id) => {
  return await del(`/manage/satellite/${id}/delete/`);
};

// modify satellite interface to call the modify satellite endpoint
export const modifySatellite = async (payload) => {
  return await post(`/manage/satellite/modify/`, payload);
};

// get new satellites from dataset interface to get the satellites from celestrak not in our database
export const getNewSatellitesFromDataset = async (
  datasetId,
  search = "",
  page = 1,
  limit = 50,
) => {
  const params = new URLSearchParams({ search, page, limit });
  return await get(`/manage/satellite/dataset/${datasetId}/new/?${params}`);
};

export const createSatellite = async (payload) => {
  return await post("/manage/satellite/create/", payload);
};
