// all backend endpoints are prefixed by /api
const BASE_URL = "/api";

// get method for sending get requests to the backend
export const get = (endpoint) => {
  return fetch(`${BASE_URL}${endpoint}`).then((res) => {
    if (!res.ok) {
      throw new Error(`HTTP error status: ${res.status}`);
    }
    return res.json();
  });
};

// post method for sending post requests to the backend
export const post = (endpoint, body) => {
  return fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((res) => {
    if (!res.ok) throw new Error(`HTTP error status: ${res.status}`);
    return res.json();
  });
};
