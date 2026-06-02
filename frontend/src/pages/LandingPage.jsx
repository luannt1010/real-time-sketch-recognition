import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import App from "./App"; 

export default function LandingPage() {
  const [showMain, setShowMain] = useState(false);

  return (
    <div style={styles.wrapper}>
      <AnimatePresence mode="wait">
        {!showMain ? (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -150 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            style={styles.landing}
          >
            <motion.h1
              style={styles.title}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              🎨 Demo
            </motion.h1>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              style={styles.button}
              onClick={() => setShowMain(true)}
            >
              🚀 Start Drawing
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            key="main"
            initial={{ y: "100vh" }}
            animate={{ y: 0 }}
            exit={{ y: "-100vh" }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          >
            <App />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

const styles = {
  wrapper: {
    height: "100vh",
    overflow: "hidden",
    fontFamily: "'Poppins', sans-serif",
  },
  landing: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(180deg, #2196F3, #E3F2FD)",
  },
  title: {
    fontSize: "72px",
    color: "white",
    fontWeight: "700",
    textShadow: "0 4px 12px rgba(0,0,0,0.25)",
    marginBottom: "50px",
  },
  button: {
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
};
