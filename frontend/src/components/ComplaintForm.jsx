// Left panel: "Log Customer Complaint" form.
// Created by Tanvi Sakhale
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { setField, resetForm } from "../store/complaintSlice";
import { saveComplaint } from "../api/api";

const FIELD_STYLE = {
  width: "100%",
  padding: "9px 12px",
  border: "1px solid #d8dbe2",
  borderRadius: 8,
  fontSize: 14,
  marginTop: 4,
  background: "#fff",
};

const LABEL_STYLE = { fontSize: 12, fontWeight: 600, color: "#4a4f5c" };

function Field({ label, field, type = "text", options }) {
  const dispatch = useDispatch();
  const value = useSelector((s) => s.complaint.form[field]) || "";
  const missing = useSelector((s) => s.complaint.ai.missing_fields.includes(field));

  return (
    <div style={{ marginBottom: 14 }}>
      <label style={LABEL_STYLE}>
        {label} {missing && <span style={{ color: "#d64545" }}>•</span>}
      </label>
      {type === "select" ? (
        <select
          style={FIELD_STYLE}
          value={value}
          onChange={(e) => dispatch(setField({ field, value: e.target.value }))}
        >
          <option value="">Awaiting AI extraction...</option>
          {options.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      ) : type === "textarea" ? (
        <textarea
          style={{ ...FIELD_STYLE, minHeight: 70, resize: "vertical" }}
          placeholder="Awaiting AI extraction..."
          value={value}
          onChange={(e) => dispatch(setField({ field, value: e.target.value }))}
        />
      ) : (
        <input
          style={FIELD_STYLE}
          type={type}
          placeholder={type === "date" ? undefined : "Awaiting AI extraction..."}
          value={value}
          onChange={(e) => dispatch(setField({ field, value: e.target.value }))}
        />
      )}
    </div>
  );
}

function SectionTitle({ children }) {
  return (
    <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: 0.5, color: "#8a90a2", margin: "18px 0 10px" }}>
      {children}
    </div>
  );
}

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const form = useSelector((s) => s.complaint.form);
  const status = useSelector((s) => s.complaint.status);

  const handleSave = async () => {
    try {
      await saveComplaint(form);
      alert("Complaint saved.");
    } catch (e) {
      alert("Failed to save complaint. Is the backend running?");
    }
  };

  return (
    <div style={{ background: "#fff", borderRadius: 14, padding: 24, boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 19 }}>Log Customer Complaint</h2>
          <div style={{ fontSize: 12, color: "#8a90a2" }}>API &amp; FDF Quality Assurance Module</div>
        </div>
        <span style={{ background: "#fff4e0", color: "#b5720a", fontSize: 11, fontWeight: 700, padding: "4px 10px", borderRadius: 20 }}>
          {status}
        </span>
      </div>

      <SectionTitle>1. ORIGIN &amp; CUSTOMER DETAILS</SectionTitle>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <Field label="Complaint Source" field="complaint_source" />
        <Field label="Customer Name" field="customer_name" />
      </div>

      <SectionTitle>2. PRODUCT &amp; BATCH IDENTIFICATION</SectionTitle>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <Field label="Product Name" field="product_name" />
        <Field label="Product Strength/Grade" field="product_strength_grade" />
        <Field label="Batch/Lot Number" field="batch_lot_number" />
        <Field label="Manufacturing Date" field="manufacturing_date" type="date" />
        <Field label="Expiry Date" field="expiry_date" type="date" />
        <Field label="Quantity Affected" field="quantity_affected" />
      </div>

      <SectionTitle>3. COMPLAINT DETAILS</SectionTitle>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <Field label="Complaint Type" field="complaint_type" />
        <Field label="Complaint Date" field="complaint_date" type="date" />
      </div>
      <Field label="Detailed Complaint Description" field="detailed_complaint_description" type="textarea" />

      <SectionTitle>4. INITIAL ASSESSMENT &amp; PRIORITY</SectionTitle>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <Field label="Initial Severity" field="initial_severity" type="select" options={["Low", "Medium", "High", "Critical"]} />
        <Field label="Priority" field="priority" type="select" options={["Low", "Medium", "High", "Urgent"]} />
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 20 }}>
        <button
          onClick={() => dispatch(resetForm())}
          style={{ padding: "10px 16px", borderRadius: 8, border: "1px solid #d8dbe2", background: "#fff", cursor: "pointer" }}
        >
          ↺ Reset Form
        </button>
        <button
          onClick={handleSave}
          style={{ padding: "10px 18px", borderRadius: 8, border: "none", background: "#2f5bea", color: "#fff", fontWeight: 600, cursor: "pointer" }}
        >
          🖫 Save Complaint
        </button>
      </div>
    </div>
  );
}
