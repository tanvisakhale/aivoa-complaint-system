// Right panel: "AI Complaint Intake Assistant" — upload/paste, extraction
// progress, AI insights (completeness, risk, duplicates, root cause, CAPA,
// summary) and a free-form chat box.
// Created by Tanvi Sakhale
import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  startExtraction,
  applyExtractionResult,
  extractionFailed,
  addChatMessage,
} from "../store/complaintSlice";
import { extractComplaint, chatWithAssistant } from "../api/api";

export default function AICopilot() {
  const dispatch = useDispatch();
  const { isExtracting, extractionProgress, ai, chatMessages, form } = useSelector((s) => s.complaint);
  const [pastedText, setPastedText] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isChatLoading]);

  const runExtraction = async ({ file, text }) => {
    dispatch(startExtraction());
    try {
      const result = await extractComplaint({ file, text });
      dispatch(applyExtractionResult(result));
      dispatch(addChatMessage({
        role: "assistant",
        text: `Done — completeness ${result.completeness_score}%, risk classified as ${result.risk_classification}.`,
      }));
    } catch (e) {
      dispatch(extractionFailed());
      dispatch(addChatMessage({ role: "assistant", text: "Extraction failed. Please check the backend and try again." }));
    }
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) runExtraction({ file });
  };

  const handleFileBrowse = (e) => {
    const file = e.target.files?.[0];
    if (file) runExtraction({ file });
    e.target.value = "";
  };

  const handlePastedSubmit = () => {
    if (pastedText.trim()) runExtraction({ text: pastedText });
  };

  const handleChatSend = async () => {
    if (!chatInput.trim() || isChatLoading) return;
    const message = chatInput;
    dispatch(addChatMessage({ role: "user", text: message }));
    setChatInput("");
    setIsChatLoading(true);
    try {
      const fullContext = JSON.stringify({ complaint_fields: form, ai_insights: ai });
      const response = await chatWithAssistant({ message, context_text: fullContext });
      if (response.extraction) {
        // Bonus feature: auto-fill-from-chat — the message itself contained
        // complaint data, so populate the form same as file/paste extraction.
        dispatch(applyExtractionResult(response.extraction));
      }
      dispatch(addChatMessage({ role: "assistant", text: response.reply || "I didn't get a clear answer for that — could you rephrase?" }));
    } catch {
      dispatch(addChatMessage({ role: "assistant", text: "Sorry, I couldn't reach the assistant. Check that the backend is running." }));
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div className="copilot-card">
      <div className="copilot-header">
        <h3 className="copilot-title">✨ AI Complaint Intake Assistant</h3>
        <span className="copilot-badge">BETA</span>
      </div>

      <div
        className={`copilot-dropzone${isDragOver ? " copilot-dropzone--active" : ""}`}
        onDrop={handleFileDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onClick={() => fileInputRef.current?.click()}
      >
        <div>⬆ Drag &amp; drop complaint document here</div>
        <div className="copilot-dropzone-sub">or click to browse</div>
        <input ref={fileInputRef} type="file" hidden onChange={handleFileBrowse} accept=".pdf,.docx,.txt,.eml" />
      </div>

      <div className="copilot-divider">OR</div>

      <textarea
        className="copilot-textarea"
        placeholder="Paste Complaint Text / Email"
        value={pastedText}
        onChange={(e) => setPastedText(e.target.value)}
        disabled={isExtracting}
      />
      <button
        className="copilot-btn-outline"
        onClick={handlePastedSubmit}
        disabled={isExtracting || !pastedText.trim()}
      >
        {isExtracting ? "Extracting..." : "Extract from pasted text"}
      </button>

      <div className="copilot-note">
        ⓘ Supported formats: PDF, DOCX, TXT, EML · Max file size: 10MB
      </div>

      <div className="copilot-progress-block">
        <div className="copilot-progress-label">
          <span>EXTRACTION PROGRESS</span><span>{extractionProgress}%</span>
        </div>
        <div className="copilot-progress-track">
          <div className="copilot-progress-fill" style={{ width: `${extractionProgress}%` }} />
        </div>
        {isExtracting && (
          <div className="copilot-progress-hint">
            <span className="copilot-spinner" aria-hidden="true" />
            Analyzing complaint content and extracting key details... this usually takes a few seconds.
          </div>
        )}
      </div>

      {ai.completeness_score !== null && (
        <div className="copilot-insights">
          <InsightRow label="Completeness" value={`${ai.completeness_score}%`} />
          <InsightRow label="Risk Classification" value={ai.risk_classification} highlight />
          {ai.duplicate_of && (
            <InsightRow
              label="Possible Duplicate"
              value={`of complaint ${ai.duplicate_of} (${Math.round((ai.duplicate_confidence || 0) * 100)}% confidence)`}
            />
          )}
          {ai.summary && (
            <div className="copilot-insight-block">
              <div className="copilot-insight-heading">SUMMARY</div>
              <div>{ai.summary}</div>
            </div>
          )}
          {ai.root_cause_suggestions?.length > 0 && (
            <div className="copilot-insight-block">
              <div className="copilot-insight-heading">ROOT CAUSE SUGGESTIONS</div>
              <ul className="copilot-insight-list">
                {ai.root_cause_suggestions.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
          {ai.capa_suggestions?.length > 0 && (
            <div className="copilot-insight-block">
              <div className="copilot-insight-heading">CAPA RECOMMENDATIONS</div>
              <ul className="copilot-insight-list">
                {ai.capa_suggestions.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="copilot-chat">
        <div className="copilot-chat-heading">AI ASSISTANT</div>
        <div className="copilot-chat-messages">
          {chatMessages.map((m, i) => (
            <div key={i} className={`copilot-bubble copilot-bubble--${m.role}`}>
              {m.text}
            </div>
          ))}
          {isChatLoading && (
            <div className="copilot-bubble copilot-bubble--assistant copilot-bubble--typing">
              <span className="copilot-dot" />
              <span className="copilot-dot" />
              <span className="copilot-dot" />
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <div className="copilot-chat-input-row">
          <input
            className="copilot-chat-input"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleChatSend()}
            placeholder="Ask me anything about this complaint..."
            disabled={isChatLoading}
          />
          <button
            className="copilot-chat-send"
            onClick={handleChatSend}
            disabled={isChatLoading || !chatInput.trim()}
            aria-label="Send"
          >
            ➤
          </button>
        </div>
        <div className="copilot-disclaimer">AI responses may contain errors. Please verify information.</div>
      </div>
    </div>
  );
}

function InsightRow({ label, value, highlight }) {
  return (
    <div className="copilot-insight-row">
      <span className="copilot-insight-label">{label}</span>
      <span className={`copilot-insight-value${highlight ? " copilot-insight-value--highlight" : ""}`}>{value}</span>
    </div>
  );
}
