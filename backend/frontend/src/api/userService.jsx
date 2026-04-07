// import post for registering new users
import { get, post, del } from "./api";

// get all users
export const getUsers = async () => {
  const data = await get(`/auth/users/`);
  return data;
};

// get specific user
export const getUserProfile = async (username) => {
  const data = await get(`/auth/${username}/userProfile/`);
  return data;
};

// modify a user
export const modifyUser = async (payload) => {
  return await post(`/auth/user/modify/`, payload);
};

// delete a user
export const deleteUser = async (username) => {
  return await del(`/auth/user/${username}/delete/`);
};

// update the current user's own profile (full_name + subtype data)
export const updateOwnProfile = async (payload) => {
  return await post(`/auth/me/update/`, payload);
};

// change the current user's password
export const changePassword = async (payload) => {
  return await post(`/auth/me/password/`, payload);
};

// register user method to create a new user in the database
export const registerUser = async (username, fullName, password) => {
  return await post(`/auth/register/`, {
    username,
    full_name: fullName,
    password,
  });
};
