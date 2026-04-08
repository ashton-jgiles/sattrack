// all backend endpoints are prefixed by /api
const BASE_URL = "/api";

// attempt to refresh the access token using the httpOnly refresh cookie
const refreshAccessToken = async () => {
  const res = await fetch(`${BASE_URL}/auth/refresh/`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) throw new Error("Session expired");
};

// core fetch wrapper — sends credentials (cookies) automatically,
// retries once after a 401 by attempting a token refresh
const fetchWithAuth = async (url, options = {}) => {
  const res = await fetch(url, { ...options, credentials: "include" });

  if (res.status === 401) {
    try {
      await refreshAccessToken();
      // replay the original request with the fresh access cookie
      return fetch(url, { ...options, credentials: "include" });
    } catch {
      // refresh failed — notify the app so it can clear auth state
      window.dispatchEvent(new Event("auth:expired"));
      throw new Error("Session expired. Please log in again.");
    }
  }

  return res;
};

// get method for sending get requests to the backend
export const get = (endpoint) => {
  return fetchWithAuth(`${BASE_URL}${endpoint}`).then(async (res) => {
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

// post method for sending post requests to the backend
export const post = (endpoint, body) => {
  return fetchWithAuth(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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
  return fetchWithAuth(`${BASE_URL}${endpoint}`, {
    method: "DELETE",
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
