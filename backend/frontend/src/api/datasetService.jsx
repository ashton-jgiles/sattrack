import { get } from "./api";

export const getTotalDatasets = async () => {
  const data = await get(`/dataset/totalDatasets/`);
  return data.total;
};
