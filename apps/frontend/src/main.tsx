import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider } from "react-oidc-context";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import { oidcConfig } from "./auth/oidc";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider {...oidcConfig}>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
);
