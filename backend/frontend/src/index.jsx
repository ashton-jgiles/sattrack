// import react, auth, and the main react app
import React from "react";
import { createRoot } from "react-dom/client";
import { AuthProvider } from "./auth/AuthContext";
import App from "./components/App";

// link the container and create the root
const container = document.getElementById("app");
const root = createRoot(container);

// redner the app inside of auth provider to enforce authentication
root.render(
  <AuthProvider>
    <App />
  </AuthProvider>,
);
