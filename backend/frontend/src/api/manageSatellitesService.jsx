import { get, post, del } from "./api";

export const deleteSatellite = async (id) => {
  return await del(`/manage/satellite/${id}/delete/`);
};

export const modifySatellite = async (payload) => {
  return await post(`/manage/satellite/modify/`, payload);
};

export const getNewSatellitesFromDataset = async (
  datasetId,
  search = "",
  page = 1,
  limit = 50,
) => {
  const params = new URLSearchParams({ search, page, limit });
  return await get(`/manage/satellite/dataset/${datasetId}/new/?${params}`);
};
