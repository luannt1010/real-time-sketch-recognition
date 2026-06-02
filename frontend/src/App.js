import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import CanvasRecognition from "./components/CanvasRecognition";
import CameraRecognition from "./components/CameraRecognition";

function App() {
  const [mode, setMode] = useState("canvas");
  const [showMainApp, setShowMainApp] = useState(false);

  useEffect(() => {
    const handlePopState = () => {
      setShowMainApp(false); // Quay lại landing
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  // Mỗi khi mở main app, đẩy state mới để back được
  const handleStart = () => {
    setShowMainApp(true);
    window.history.pushState({}, "MainApp"); // để trình duyệt có thể "back"
  };

  const styles = {
    logoTopLeft: {
      position: "absolute",
      top: "30px",
      left: "40px",
      width: "150px",
      height: "150px",
      objectFit: "contain",
      filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.3))",
      cursor: "pointer",
      transition: "transform 0.3s ease",
    },
    landingWrapper: {
      height: "100vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      background: "linear-gradient(180deg, #2196F3, #E3F2FD)",
      fontFamily: "'Poppins', sans-serif",
      overflow: "hidden",
    },
    landingTitle: {
      fontSize: "60px",
      color: "white",
      fontWeight: "700",
      textShadow: "0 4px 12px rgba(0,0,0,0.25)",
      marginBottom: "50px",
      textAlign: "center",
    },
    landingButton: {
      backgroundColor: "#FFC107",
      color: "#0D47A1",
      border: "none",
      borderRadius: "10px",
      padding: "16px 50px",
      fontSize: "22px",
      fontWeight: "600",
      cursor: "pointer",
      boxShadow: "0 6px 20px rgba(255,193,7,0.4)",
      transition: "all 0.3s ease",
    },
    container: {
      textAlign: "center",
      padding: "40px",
      fontFamily: "'Poppins', sans-serif",
      backgroundColor: "#FFFFFF",
      minHeight: "100vh",
      overflow: "hidden",
      position: "relative",
    },
    title: {
      color: "#1565C0",
      fontSize: "32px",
      fontWeight: "700",
      marginBottom: "30px",
      textShadow: "0 2px 6px rgba(21,101,192,0.15)",
    },
    buttonGroup: {
      marginBottom: "30px",
    },
    button: {
      padding: "12px 26px",
      borderRadius: "10px",
      border: "none",
      fontSize: "16px",
      fontWeight: "600",
      cursor: "pointer",
      margin: "0 10px",
      transition: "all 0.3s ease",
      boxShadow: "0 3px 10px rgba(0,0,0,0.1)",
    },
    activeButton: {
      backgroundColor: "#1976D2",
      color: "white",
      transform: "scale(1.05)",
      boxShadow: "0 4px 12px rgba(25,118,210,0.4)",
    },
    inactiveButton: {
      backgroundColor: "#BBDEFB",
      color: "#0D47A1",
    },
    contentWrapper: {
      position: "relative",
      height: "auto",
      minHeight: "500px",
    },
    backButton: {
      position: "fixed",
      top: "20px",
      left: "20px",
      backgroundColor: "rgba(33,150,243,0.1)",
      color: "#1565C0",
      border: "none",
      borderRadius: "8px",
      padding: "8px 14px",
      cursor: "pointer",
      fontWeight: "600",
      transition: "all 0.3s ease",
    },
    backButtonHover: {
      backgroundColor: "rgba(33,150,243,0.25)",
      transform: "scale(1.05)",
    },
  };

  const [hoverBack, setHoverBack] = useState(false);

  return (
    <div>
      <AnimatePresence mode="wait">
        {!showMainApp ? (
          // 🎨 Landing Page
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -200 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            style={styles.landingWrapper}
          >
            {/*<motion.img
              src={logo}
              alt="App Logo"
              style={styles.logoTopLeft}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            />*/}
            <motion.div
              style={styles.landingTitle}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1 }}
            >
              DRAW ANYTHING — LET AI RECOGNIZE YOUR SKETCH INSTANTLY.
            </motion.div>

            <motion.button
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.95 }}
              style={styles.landingButton}
              onClick={handleStart}
            >
              Start Drawing
            </motion.button>
          </motion.div>
        ) : (
          // 🎬 App chính (Camera + Canvas)
          <motion.div
            key="mainApp"
            initial={{ y: "100vh" }}
            animate={{ y: 0 }}
            exit={{ y: "-100vh" }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          >
            <div style={styles.container}>
              {/* ↩️ Nút Back góc trái */}
              <button
                style={{
                  ...styles.backButton,
                  ...(hoverBack ? styles.backButtonHover : {}),
                }}
                onMouseEnter={() => setHoverBack(true)}
                onMouseLeave={() => setHoverBack(false)}
                onClick={() => setShowMainApp(false)}
              >
                Back
              </button>

              <h1 style={styles.title}>🎨 AI Sketch Recognition</h1>

              <div style={styles.buttonGroup}>
                <button
                  onClick={() => setMode("canvas")}
                  style={{
                    ...styles.button,
                    ...(mode === "canvas"
                      ? styles.activeButton
                      : styles.inactiveButton),
                  }}
                >
                  Draw by Hand ✍️
                </button>

                <button
                  onClick={() => setMode("camera")}
                  style={{
                    ...styles.button,
                    ...(mode === "camera"
                      ? styles.activeButton
                      : styles.inactiveButton),
                  }}
                >
                  Draw by Camera 📷
                </button>
              </div>

              <div style={styles.contentWrapper}>
                {mode === "canvas" ? <CanvasRecognition /> : <CameraRecognition />}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;

