import React, { useState } from "react";
import { submitFeedback } from "../services/feedbackService";

export default function FeedbackForm({
  imageData,
  predictedClass,
  mapping = {},
  inferenceTime,
  drawBy,
  onSubmitted,
}) {
  const [name, setName] = useState("");
  const [isCorrect, setIsCorrect] = useState(null);
  const [actualLabel, setActualLabel] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmitFeedback = async () => {
    if (submitting) return;
    setSubmitting(true);

    const feedbackData = {
      name,
      is_correct: isCorrect,
      actual_label: isCorrect ? predictedClass : actualLabel,
      image: imageData,
      draw_by: drawBy || "Canvas",
      inference_time: inferenceTime
    };

    try {
      const data = await submitFeedback(feedbackData);
      alert(data.message || "Feedback sent successfully!");
      onSubmitted?.();
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Failed to send feedback. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.feedbackBox} className="fadeIn">
        <h4 style={styles.feedbackTitle}>Feedback Form📝</h4>

        <div style={{ textAlign: "left" }}>
          {/* Name input */}
          <label style={styles.label}>👤 Your name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name"
            style={styles.input}
          />

          {/* Correct or not */}
          <label style={styles.label}>Is the prediction correct?</label>
          <div style={styles.radioGroup}>
            <label style={styles.radioLabel}>
              <input
                type="radio"
                checked={isCorrect === true}
                onChange={() => setIsCorrect(true)}
              />{" "}
              <span style={styles.radioText}>Yes</span>
            </label>
            <label style={styles.radioLabel}>
              <input
                type="radio"
                checked={isCorrect === false}
                onChange={() => setIsCorrect(false)}
              />{" "}
              <span style={styles.radioText}>No</span>
            </label>
          </div>

          {/* If not correct → select correct label */}
          {!isCorrect && (
            <>
              <label style={styles.label}>Correct label</label>
              <select
                value={actualLabel}
                onChange={(e) => setActualLabel(e.target.value)}
                style={styles.select}
              >
                <option value="">-- Choose correct label --</option>
                {Object.keys(mapping || {}).map((label) => (
                  <option key={label} value={label}>
                    {label}
                  </option>
                ))}
              </select>
            </>
          )}

          {/* Submit button */}
          <button
            onClick={handleSubmitFeedback}
            disabled={
              submitting ||
              !name ||
              isCorrect === null ||
              (!isCorrect && !actualLabel)
            }
            style={{
              ...styles.submitButton,
              opacity:
                !name || isCorrect === null || (!isCorrect && !actualLabel)
                  ? 0.6
                  : 1,
              cursor:
                !name || isCorrect === null || (!isCorrect && !actualLabel)
                  ? "not-allowed"
                  : "pointer",
            }}
          >
            {submitting ? "Sending..." : "Submit Feedback"}
          </button>
        </div>
      </div>

      {/* CSS animations */}
      <style>{`
        .fadeIn {
          animation: fadeIn 0.6s ease-in-out;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        input[type="radio"] {
          accent-color: #2196F3;
          cursor: pointer;
        }
        select:focus, input:focus {
          border-color: #1976D2;
          box-shadow: 0 0 0 3px rgba(25,118,210,0.2);
          outline: none;
        }
        button:hover:not(:disabled) {
          transform: scale(1.02);
          box-shadow: 0 4px 15px rgba(67,160,71,0.4);
        }
      `}</style>
    </div>
  );
}

// --- STYLE DEFINITIONS ---
const styles = {
  wrapper: {
    display: "flex",
    justifyContent: "center",
    animation: "fadeIn 0.6s ease-in-out",
  },
  feedbackBox: {
    background: "linear-gradient(180deg, #E3F2FD, #FFFFFF)",
    width: "420px",
    margin: "30px auto",
    padding: "25px",
    borderRadius: "15px",
    boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
    border: "1px solid #BBDEFB",
  },
  feedbackTitle: {
    color: "#0D47A1",
    textAlign: "center",
    marginBottom: "15px",
    fontWeight: "700",
  },
  label: {
    display: "block",
    color: "#0D47A1",
    fontWeight: "500",
    marginBottom: "6px",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginBottom: "12px",
    borderRadius: "8px",
    border: "1px solid #90CAF9",
    outline: "none",
    transition: "all 0.2s ease",
  },
  select: {
    width: "100%",
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #90CAF9",
    outline: "none",
    marginBottom: "15px",
    transition: "all 0.2s ease",
  },
  radioGroup: {
    display: "flex",
    justifyContent: "space-between",
    width: "150px",
    marginBottom: "12px",
  },
  radioLabel: {
    display: "flex",
    alignItems: "center",
    cursor: "pointer",
  },
  radioText: {
    color: "#0D47A1",
    fontWeight: "500",
  },
  submitButton: {
    width: "100%",
    padding: "12px",
    backgroundColor: "#43A047",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontWeight: "bold",
    transition: "all 0.3s ease",
    boxShadow: "0 4px 10px rgba(67,160,71,0.4)",
  },
};
