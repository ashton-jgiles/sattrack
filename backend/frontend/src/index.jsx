import React from "react";
import { createRoot } from "react-dom/client";
import { AuthProvider } from "./auth/AuthContext";
import App from "./components/App";

const container = document.getElementById("app");
const root = createRoot(container);

root.render(
  <AuthProvider>
    <App />
  </AuthProvider>,
);
