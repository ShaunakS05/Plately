import React from "react";

function Dashboard() {
  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Welcome to Plately’s Dashboard</h1>
      <p style={styles.paragraph}>
        Here’s where you can manage your AI-driven menu optimizations, track performance, and discover insights.
      </p>
    </div>
  );
}

// Simple inline styles for demonstration
const styles = {
  container: {
    fontFamily: "'Poppins', sans-serif",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    backgroundColor: "#f3f3f3",
  },
  heading: {
    fontSize: "2rem",
    color: "#2ecc71",
    marginBottom: "1rem",
  },
  paragraph: {
    maxWidth: "600px",
    textAlign: "center",
    lineHeight: 1.6,
    fontWeight: 300,
  },
};

export default Dashboard;
