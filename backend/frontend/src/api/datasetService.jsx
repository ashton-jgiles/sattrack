// import the get, post, and del methods
import { get, post, del } from "./api";

// get total distance creates a frontend interface to the total datasets endpoint
export const getTotalDatasets = async () => {
  const data = await get(`/dataset/total_datasets/`);
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

// get dataset sources returns available CelesTrak groups not yet in the database
export const getDatasetSources = async () => {
  return await get(`/manage/dataset/sources/`);
};

// add dataset creates a new dataset from a CelesTrak group
export const addDataset = async (payload) => {
  return await post(`/manage/dataset/add/`, payload);
};

// get review datasets returns datasets for the reviews page
export const getReviewDatasets = async (showClosed = false) => {
  return await get(`/manage/dataset/reviews/?closed=${showClosed}`);
};

// review dataset approves or rejects a dataset with an optional comment
export const reviewDataset = async (datasetId, payload) => {
  return await post(`/manage/dataset/${datasetId}/review/`, payload);
};
