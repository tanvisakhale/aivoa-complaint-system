// Created by Tanvi Sakhale
import React from "react";
import ComplaintForm from "./components/ComplaintForm";
import AICopilot from "./components/AICopilot";

export default function App() {
  return (
    <div style={{ minHeight: "100vh", padding: "28px 32px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 24, maxWidth: 1280, margin: "0 auto" }}>
        <div style={{ minWidth: 0 }}>
          <ComplaintForm />
        </div>
        <div style={{ minWidth: 0 }}>
          <AICopilot />
        </div>
      </div>
      <div style={{ textAlign: "center", fontSize: 12, color: "#b0b4c0", marginTop: 24 }}>
        AIVOA.AI Customer Complaint Management System — Created by Tanvi Sakhale
      </div>
    </div>
  );
}
