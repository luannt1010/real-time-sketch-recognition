import React, { useRef, useState, useEffect } from "react";
import mapping from "./mapping.json";
import FeedbackForm from "./FeedbackForm";
import { motion } from "framer-motion";
import { recognizeImage } from "../services/recognitionService";

export default function CanvasRecognition() {
  const canvasRef = useRef(null);
  const [prediction, setPrediction] = useState(null);
  const [predictedClass, setPredictedClass] = useState("");
  const [confidence, setConfidence] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);

  const classLabels = Object.fromEntries(
    Object.entries(mapping).map(([label, idx]) => [idx, label])
  );

  // Khởi tạo nền trắng khi render
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }, []);

  // Bắt đầu vẽ
  const startDrawing = (e) => {
    const ctx = canvasRef.current.getContext("2d");
    ctx.lineWidth = 20;
    ctx.lineCap = "round";
    ctx.strokeStyle = "#000";
    ctx.beginPath();
    ctx.moveTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    setShowFeedback(false);
    setPrediction(null);
  };

  // Vẽ liên tục
  const draw = (e) => {
    if (e.buttons !== 1) return;
    const ctx = canvasRef.current.getContext("2d");
    ctx.lineTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    ctx.stroke();
  };

  // Dự đoán
  const handlePredict = async () => {
  const dataUrl = canvasRef.current.toDataURL("image/png");
  const data = await recognizeImage(dataUrl);

  if (data.label) {
    setPredictedClass(data.label);
    setConfidence(data.confidence);

    setPrediction({
      label: data.label,
      confidence: data.confidence,
      inference_time: data.inference_time,
    });

    setShowFeedback(true);
  } else {
    setPrediction({
      label: "No valid prediction.",
      confidence: null,
    });
  }
};

  // Xóa canvas
  const handleClear = () => {
    const ctx = canvasRef.current.getContext("2d");
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    setPrediction(null);
    setShowFeedback(false);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Hand Drawing Recognition</h2>

      {/* Canvas */}
      <div style={styles.canvasWrapper}>
        <canvas
          ref={canvasRef}
          width={940}
          height={440}
          style={styles.canvas}
          onMouseDown={startDrawing}
          onMouseMove={draw}
        />
      </div>

      {/* Buttons */}
      <div style={styles.buttonGroup}>
        <motion.button
          onClick={handlePredict}
          style={{ ...styles.button, ...styles.predictButton }}
          whileHover={{ scale: 1.08, boxShadow: "0 0 10px rgba(33,150,243,0.4)" }}
          whileTap={{ scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className="ripple"
        >
          Predict
        </motion.button>
        <motion.button
          onClick={handleClear}
          style={{ ...styles.button, ...styles.clearButton }}
          whileHover={{ scale: 1.08, boxShadow: "0 0 10px rgba(100,181,246,0.4)" }}
          whileTap={{ scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className="ripple"
        >
          Clear
        </motion.button>
      </div>

      {/* Prediction Box */}
      {prediction && (
        <div
          style={{
            ...styles.predictionBox,
            animation: "fadeIn 0.4s ease-in-out",
          }}
        >
          <h3 style={{ margin: 0, color: "#0D47A1" }}>Prediction Result</h3>
          <p style={{ fontSize: "20px", marginTop: "10px" }}>
            <b style={{ color: "#2E7D32" }}>{prediction.label}</b>
            {prediction.confidence && (
              <span style={{ color: "#555" }}>
                {" "}
                — {prediction.confidence}% confidence
              </span>
            )}
          </p>
        </div>
      )}

      {/* Feedback */}
      {showFeedback && (
        <FeedbackForm
          imageData={canvasRef.current.toDataURL("image/png")}
          predictedClass={predictedClass}
          mapping={mapping}
          inferenceTime={prediction?.inference_time}
          drawBy="Canvas"
          onSubmitted={() => setShowFeedback(false)}
        />
      )}

      {/* CSS animation + ripple */}
      <style>{`
        .ripple {
          position: relative;
          overflow: hidden;
          transition: transform 0.2s ease;
        }
        .ripple:active {
          transform: scale(0.97);
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}


const styles = {
  container: {
    textAlign: "center",
    fontFamily: "'Poppins', sans-serif",
    background: "linear-gradient(180deg, #E3F2FD, #FFFFFF)",
    minHeight: "100vh",
    padding: "40px",
    borderRadius: "12px",
  },
  title: {
    color: "#1565C0",
    fontWeight: "700",
    fontSize: "28px",
    marginBottom: "25px",
  },
  canvasWrapper: {
    display: "flex",
    justifyContent: "center",
  },
  canvas: {
    border: "3px solid #1976D2",
    borderRadius: "12px",
    backgroundColor: "white",
    cursor: "crosshair",
    boxShadow: "0 4px 16px rgba(25, 118, 210, 0.25)",
  },
  buttonGroup: {
    marginTop: "25px",
  },
  button: {
    border: "none",
    color: "white",
    padding: "12px 40px",
    borderRadius: "8px",
    fontSize: "18px",
    fontWeight: "bold",
    cursor: "pointer",
    margin: "0 10px",
    transition: "all 0.3s ease",
  },
  predictButton: {
    backgroundColor: "#2196F3",
    boxShadow: "0 4px 10px rgba(33,150,243,0.4)",
  },
  clearButton: {
    backgroundColor: "#64B5F6",
    boxShadow: "0 4px 10px rgba(100,181,246,0.4)",
  },
  predictionBox: {
    marginTop: "30px",
    backgroundColor: "linear-gradient(180deg, #E3F2FD, #FFFFFF)",
    borderRadius: "12px",
    padding: "20px",
    width: "420px",
    margin: "25px auto",
    boxShadow: "0 4px 15px rgba(0,0,0,0.15)",
    border: "2px solid #BBDEFB",
  },
};

