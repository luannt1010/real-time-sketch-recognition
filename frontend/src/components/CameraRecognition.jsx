import React, { useState, useEffect } from "react";
import FeedbackForm from "./FeedbackForm";
import mapping from "./mapping";
import { motion } from "framer-motion";

import { startCamera, stopCamera, clearCamera, getFrame, getCanvas } from "../services/cameraService";

import { recognizeImage } from "../services/recognitionService";

export default function CameraRecognition() {
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [frameSrc, setFrameSrc] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [imageData, setImageData] = useState(null);

  // Start camera
  const handleStart = async () => {
    await startCamera();
    setIsCameraOn(true);
    setPrediction(null);
    setShowFeedback(false);
  };

  // Stop camera
  const handleStop = async () => {
    await stopCamera();
    setIsCameraOn(false);
    setFrameSrc(null);
    setPrediction(null);
    setShowFeedback(false);
  };

  // Clear canvas
  const handleClear = async () => {
    await clearCamera();
    setPrediction(null);
    setShowFeedback(false);
  };

  // Poll camera frame (auto-refresh)
  useEffect(() => {
    let interval;
    if (isCameraOn) {
      interval = setInterval(async () => {
        const data = await getFrame();
        if (data.frame) setFrameSrc("data:image/jpeg;base64," + data.frame);
      }, 300);
    }
    return () => clearInterval(interval);
  }, [isCameraOn]);

  // Predict from backend
  const handlePredict = async () => {
    try {
      const canvasData = await getCanvas();
      if (!canvasData.canvas) {
        alert(" There are no valid strokes to predict!");
        return;
      }

      const result = await recognizeImage(
      "data:image/jpeg;base64," + canvasData.canvas);
      if (result.label) {
        setPrediction({
          label: result.label,
          confidence: result.confidence,
          inference_time: result.inference_time,
        });
        setShowFeedback(true);
        setImageData("data:image/jpeg;base64," + canvasData.canvas);
      } else {
        alert("The drawing could not be recognized.");
      }
    } catch (err) {
      console.error("Error when predicting:", err);
      alert("Unable to connect to backend server.");
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Camera Drawing Recognition</h2>

      {/* --- CAMERA --- */}
      <div style={styles.cameraWrapper}>
        {isCameraOn && frameSrc ? (
          <img src={frameSrc} alt="Camera Feed" style={styles.video} />
        ) : (
          <div style={styles.videoPlaceholder}>
            Camera is turning off — push “Start Camera” to turn on 
          </div>
        )}
      </div>

      {/* --- BUTTONS --- */}
      <div style={styles.buttonGroup}>
        {!isCameraOn ? (
          <motion.button
            onClick={handleStart}
            style={{ ...styles.button, ...styles.startButton }}
            className="ripple"
            whileHover={{ scale: 1.08, boxShadow: "0 0 10px rgba(255,193,7,0.4)" }}
            whileTap={{ scale: 0.95 }}
            transition={{ duration: 0.2 }}
            disabled={false}
          >
            ▶️ Start Camera
          </motion.button>
        ) : (
          <motion.button
            onClick={handleStop}
            style={{ ...styles.button, ...styles.stopButton }}
            className="ripple"
            whileHover={{ scale: 1.08, boxShadow: "0 0 10px rgba(229,57,53,0.4)" }}
            whileTap={{ scale: 0.95 }}
            transition={{ duration: 0.2 }}
            disabled={false} 
          >
            ⏹️ Stop Camera
          </motion.button>
        )}

        <motion.button
          onClick={handlePredict}
          style={{ ...styles.button, ...styles.predictButton }}
          whileHover={{ scale: 1.08, boxShadow: "0 0 10px rgba(33,150,243,0.4)" }}
          whileTap={{ scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className="ripple"
          disabled={!isCameraOn}
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
          disabled={!isCameraOn}
        >
          Clear 
        </motion.button>
      </div>

      {/* --- PREDICTION BOX --- */}
      {prediction && (
        <div
          style={{
            ...styles.predictionBox,
            animation: "fadeIn 0.4s ease-in-out",
          }}
        >
          <h3 style={{margin: 0, color: "#0D47A1" }}>Prediction Result</h3>
          <p style={{ fontSize: "20px", marginTop: "10px" }}>
            <b style={{ color: "#2E7D32" }}>{prediction.label}</b> —{" "}
            {prediction.confidence}% confidence
          </p>
        </div>
      )}

      {/* --- FEEDBACK FORM --- */}
      {showFeedback && prediction && (
        <FeedbackForm
          imageData={imageData}
          predictedClass={prediction.label}
          mapping={mapping}
          drawBy="Camera"
          inferenceTime={prediction?.inference_time}
          onSubmitted={() => setShowFeedback(false)}
        />
      )}

      {/* --- CSS ANIMATION --- */}
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

// --- STYLES ---
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
  cameraWrapper: {
    display: "flex",
    justifyContent: "center",
  },
  video: {
    border: "3px solid #1976D2",
    borderRadius: "12px",
    backgroundColor: "#000",
    boxShadow: "0 4px 16px rgba(25, 118, 210, 0.25)",
    width: "960px",
    height: "540px",
    objectFit: "cover",
  },
  videoPlaceholder: {
    border: "3px dashed #90CAF9",
    borderRadius: "12px",
    width: "960px",
    height: "540px",
    color: "#1565C0",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "18px",
    background: "rgba(227, 242, 253, 0.4)",
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
  startButton: {
  backgroundColor: "#FFC107", // 💛 Vàng tươi (Material Design Amber 500)
  boxShadow: "0 4px 10px rgba(255, 193, 7, 0.4)", // Bóng vàng nhẹ
  color: "white", // Chữ trắng nổi bật
  transition: "all 0.3s ease",
},
  stopButton: {
    backgroundColor: "#E53935",
    boxShadow: "0 4px 10px rgba(229,57,53,0.4)",
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

