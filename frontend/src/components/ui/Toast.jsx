/**
 * Toast.jsx — Central notification toast configuration.
 *
 * Uses react-hot-toast with styles matching our glassmorphism dark/light design.
 */

import { Toaster } from "react-hot-toast";

export default function AppToaster() {
  return (
    <Toaster
      position="bottom-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: "rgba(30, 41, 59, 0.85)",
          color: "#f8fafc",
          backdropFilter: "blur(12px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          borderRadius: "14px",
          padding: "12px 18px",
          fontSize: "14px",
          boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.3)",
        },
        success: {
          iconTheme: {
            primary: "#10b981",
            secondary: "#ffffff",
          },
        },
        error: {
          iconTheme: {
            primary: "#f43f5e",
            secondary: "#ffffff",
          },
        },
      }}
    />
  );
}

