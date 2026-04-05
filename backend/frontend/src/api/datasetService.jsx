// import the get, post, and del methods
import { get, post, del } from "./api";

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

// get satellites in dataset returns all satellites belonging to a given dataset
export const getSatellitesInDataset = async (datasetId) => {
  const data = await get(`/dataset/${datasetId}/satellites/`);
  return data;
};

// modify dataset updates description, pull_frequency, and review_status
export const modifyDataset = async (datasetId, payload) => {
  return await post(`/manage/dataset/${datasetId}/modify/`, payload);
};

// delete dataset removes a dataset from the database
export const deleteDataset = async (datasetId) => {
  return await del(`/manage/dataset/${datasetId}/delete/`);
};
