// import the get method
import { get } from "./api";

// get total distance creates a frontend interface to the total datasets endpoint
export const getTotalDatasets = async () => {
  const data = await get(`/dataset/totalDatasets/`);
  return data.total;
};

// get all datasets creates an interface to the all datasets endpoint
export const getAllDatasets = async () => {
  const data = await get(`/dataset/datasets/`);
  return data;
};
