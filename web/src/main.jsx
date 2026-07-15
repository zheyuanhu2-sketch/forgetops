import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/fraunces/600.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import "@fontsource/ibm-plex-mono/600.css";
import "@fontsource/ibm-plex-sans-condensed/400.css";
import "@fontsource/ibm-plex-sans-condensed/500.css";
import "@fontsource/ibm-plex-sans-condensed/600.css";
import "@xyflow/react/dist/style.css";
import { App } from "./App.jsx";
import "./styles.css";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("ForgetOps root element is missing.");
}

createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
