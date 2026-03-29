import { get, post, del } from "./api";

export const deleteSatellite = async (id) => {
  return await del(`/admin/satellite/${id}/delete/`);
};

export const modifySatellite = async (payload) => {
  return await post(`/admin/satellite/modify/`, payload);
};

export const getNewSatellitesFromDataset = async (
  datasetId,
  search = "",
  page = 1,
  limit = 50,
) => {
  const params = new URLSearchParams({ search, page, limit });
  return await get(`/admin/satellite/dataset/${datasetId}/new/?${params}`);
};
