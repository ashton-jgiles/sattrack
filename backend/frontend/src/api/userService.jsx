// import post for registering new users
import { post } from "./api";

// register user method to create a new user in the database
export const registerUser = async (username, fullName, password) => {
  return await post("/auth/register/", {
    username,
    full_name: fullName,
    password,
  });
};
