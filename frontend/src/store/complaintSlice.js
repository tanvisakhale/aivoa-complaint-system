// Redux slice for the complaint form + AI copilot state.
// Created by Tanvi Sakhale
import { createSlice } from "@reduxjs/toolkit";

const emptyForm = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength_grade: "",
  batch_lot_number: "",
  manufacturing_date: "",
  expiry_date: "",
  quantity_affected: "",
  complaint_type: "",
  complaint_date: "",
  detailed_complaint_description: "",
  initial_severity: "",
  priority: "",
};

const initialState = {
  form: emptyForm,
  status: "Pending Triage",
  extractionProgress: 0,
  isExtracting: false,
  ai: {
    completeness_score: null,
    missing_fields: [],
    risk_classification: null,
    root_cause_suggestions: [],
    capa_suggestions: [],
    summary: "",
    duplicate_of: null,
    duplicate_confidence: null,
  },
  chatMessages: [
    {
      role: "assistant",
      text: "Upload a complaint document or paste text above. I will automatically extract the details and populate the form for you.",
    },
  ],
};

const complaintSlice = createSlice({
  name: "complaint",
  initialState,
  reducers: {
    setField(state, action) {
      const { field, value } = action.payload;
      state.form[field] = value;
    },
    resetForm(state) {
      state.form = emptyForm;
      state.status = "Pending Triage";
      state.ai = initialState.ai;
      state.extractionProgress = 0;
    },
    startExtraction(state) {
      state.isExtracting = true;
      state.extractionProgress = 10;
    },
    setExtractionProgress(state, action) {
      state.extractionProgress = action.payload;
    },
    applyExtractionResult(state, action) {
      const result = action.payload;
      state.form = { ...state.form, ...result.fields };
      state.ai = {
        completeness_score: result.completeness_score,
        missing_fields: result.missing_fields,
        risk_classification: result.risk_classification,
        root_cause_suggestions: result.root_cause_suggestions,
        capa_suggestions: result.capa_suggestions,
        summary: result.summary,
        duplicate_of: result.duplicate_of,
        duplicate_confidence: result.duplicate_confidence,
      };
      state.status = "Extraction Complete";
      state.isExtracting = false;
      state.extractionProgress = 100;
    },
    extractionFailed(state) {
      state.isExtracting = false;
      state.extractionProgress = 0;
    },
    addChatMessage(state, action) {
      state.chatMessages.push(action.payload);
    },
  },
});

export const {
  setField,
  resetForm,
  startExtraction,
  setExtractionProgress,
  applyExtractionResult,
  extractionFailed,
  addChatMessage,
} = complaintSlice.actions;

export default complaintSlice.reducer;
