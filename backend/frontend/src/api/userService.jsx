import { post } from "./api";

export const registerUser = async (username, fullName, password) => {
  return await post("/auth/register/", {
    username,
    full_name: fullName,
    password,
  });
};
