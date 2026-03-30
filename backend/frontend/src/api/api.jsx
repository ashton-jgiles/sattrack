// all backend endpoints are prefixed by /api
const BASE_URL = "/api";

// helper to get auth headers
const getAuthHeaders = () => {
  const token = sessionStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// get method for sending get requests to the backend
export const get = (endpoint) => {
  return fetch(`${BASE_URL}${endpoint}`, {
    headers: {
      ...getAuthHeaders(),
    },
  }).then((res) => {
    if (!res.ok) throw new Error(`HTTP error status: ${res.status}`);
    return res.json();
  });
};
// post method for sending post requests to the backend
export const post = (endpoint, body) => {
  return fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(body),
  }).then(async (res) => {
    let data;
    try {
      data = await res.json();
    } catch {
      data = {};
    }
    if (!res.ok) {
      throw new Error(data.error || `HTTP error status: ${res.status}`);
    }
    return data;
  });
};
// del method for sending delete requests to the backend
export const del = (endpoint) => {
  return fetch(`${BASE_URL}${endpoint}`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(),
    },
  }).then(async (res) => {
    let data;
    try {
      data = await res.json();
    } catch {
      data = {};
    }
    if (!res.ok) {
      throw new Error(data.error || `HTTP error status: ${res.status}`);
    }
    return data;
  });
};
