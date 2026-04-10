// import post for settings actions
import { post } from "./api";

// trigger a full trajectory update for all active satellites
export const updateTrajectories = async () => {
  return await post(`/settings/trajectory/update/`, {});
};
