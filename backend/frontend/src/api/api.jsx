const BASE_URL = "/api";

export const get = (endpoint) => {
  return fetch(`${BASE_URL}${endpoint}`).then((res) => {
    if (!res.ok) {
      throw new Error(`HTTP error status: ${res.status}`);
    }
    return res.json();
  });
};
