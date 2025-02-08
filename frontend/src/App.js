import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./Dashboard"; // Import our new Dashboard component
import "./index.css"; // If you have global styles or Google Fonts link

function App() {
  // Inline style objects for the landing page
  const styles = {
    page: {
      fontFamily: "'Poppins', sans-serif",
      margin: 0,
      padding: 0,
      boxSizing: "border-box",
      color: "#333",
      backgroundColor: "#fff",
    },
    navbar: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "1rem 2rem",
      backgroundColor: "#ffffff",
      boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
      position: "sticky",
      top: 0,
      zIndex: 999,
    },
    logo: {
      fontSize: "1.8rem",
      fontWeight: "700",
      color: "#2ecc71",
    },
    navList: {
      listStyleType: "none",
      display: "flex",
      gap: "1.5rem",
      margin: 0,
      padding: 0,
    },
    navLink: {
      textDecoration: "none",
      color: "#333",
      fontWeight: "500",
      fontSize: "1rem",
    },

    // Hero
    heroSection: {
      position: "relative",
      padding: "6rem 2rem 8rem 2rem",
      textAlign: "center",
      background: "linear-gradient(135deg, #2ecc71 30%, #27ae60 100%)",
      color: "#ffffff",
      clipPath: "polygon(0 0, 100% 0, 100% 85%, 0 100%)",
    },
    heroContent: {
      maxWidth: "800px",
      margin: "0 auto",
      position: "relative",
      zIndex: 1,
    },
    heroTitle: {
      fontSize: "3rem",
      marginBottom: "0.5rem",
      fontWeight: "700",
      lineHeight: 1.2,
    },
    heroSubtitle: {
      fontSize: "1.6rem",
      marginBottom: "1.5rem",
      fontWeight: "500",
      opacity: 0.9,
    },
    heroParagraph: {
      fontSize: "1.1rem",
      fontWeight: "300",
      maxWidth: "600px",
      margin: "0 auto 2rem",
      lineHeight: 1.6,
    },
    ctaButton: {
      backgroundColor: "#fff",
      color: "#27ae60",
      padding: "0.85rem 2rem",
      borderRadius: "2rem",
      fontSize: "1rem",
      fontWeight: "700",
      textDecoration: "none",
      boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
    },

    // Features
    featuresSection: {
      padding: "4rem 2rem",
      backgroundColor: "#f8f8f8",
    },
    featuresHeader: {
      textAlign: "center",
      fontSize: "2.2rem",
      marginBottom: "3rem",
    },
    featuresGrid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
      gap: "2rem",
      maxWidth: "1000px",
      margin: "0 auto",
    },
    featureCard: {
      backgroundColor: "#ffffff",
      padding: "2rem",
      borderRadius: "1rem",
      boxShadow: "0 4px 10px rgba(0,0,0,0.05)",
    },
    featureTitle: {
      color: "#2ecc71",
      marginBottom: "1rem",
      fontSize: "1.3rem",
      fontWeight: 600,
    },
    featureDescription: {
      lineHeight: 1.6,
      fontWeight: 300,
    },

    // How it Works
    howItWorksSection: {
      padding: "4rem 2rem",
      maxWidth: "900px",
      margin: "0 auto",
      textAlign: "center",
    },
    howItWorksHeader: {
      fontSize: "2rem",
      marginBottom: "2rem",
    },
    stepsContainer: {
      display: "flex",
      flexDirection: "column",
      gap: "2rem",
      marginTop: "2rem",
    },
    stepItem: {
      display: "flex",
      alignItems: "center",
      gap: "1rem",
      textAlign: "left",
    },
    stepNumber: {
      flexShrink: 0,
      backgroundColor: "#2ecc71",
      color: "#fff",
      fontSize: "1.2rem",
      width: "2.2rem",
      height: "2.2rem",
      borderRadius: "50%",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontWeight: "700",
    },
    stepText: {
      fontWeight: 300,
      lineHeight: 1.6,
    },

    // Signup CTA
    signupSection: {
      textAlign: "center",
      padding: "4rem 2rem",
      backgroundColor: "#ffffff",
    },
    signupHeader: {
      marginBottom: "2rem",
      fontSize: "1.8rem",
      color: "#2ecc71",
      fontWeight: 600,
    },

    // Footer
    footer: {
      padding: "2rem",
      textAlign: "center",
      backgroundColor: "#f8f8f8",
    },
    footerLink: {
      color: "#27ae60",
      textDecoration: "none",
      fontWeight: 500,
    },
    socialList: {
      display: "flex",
      justifyContent: "center",
      gap: "1rem",
      listStyle: "none",
      margin: "1rem 0",
      padding: 0,
    },
    socialLink: {
      color: "#27ae60",
      textDecoration: "none",
    },
  };

  // Landing Page Layout
  const LandingPage = () => (
    <div style={styles.page}>
      {/* Navbar */}
      <header style={styles.navbar}>
        <div style={styles.logo}>Plately</div>
        <nav>
          <ul style={styles.navList}>
            <li>
              <a href="#home" style={styles.navLink}>
                Home
              </a>
            </li>
            <li>
              <a href="#features" style={styles.navLink}>
                Features
              </a>
            </li>
            <li>
              <a href="#how-it-works" style={styles.navLink}>
                How It Works
              </a>
            </li>
            <li>
              <a href="#contact" style={styles.navLink}>
                Contact
              </a>
            </li>
          </ul>
        </nav>
      </header>

      {/* Hero */}
      <section style={styles.heroSection} id="home">
        <div style={styles.heroContent}>
          <h1 style={styles.heroTitle}>Plately</h1>
          <h2 style={styles.heroSubtitle}>Your AI Menu Engineer</h2>
          <p style={styles.heroParagraph}>
            Reinvent your restaurant’s menu with data-driven insights,
            custom recommendations, and simple setup.
          </p>
          {/*
            IMPORTANT:
            We use `target="_blank"` so the Dashboard opens in a new tab.
            Make sure you also use rel="noopener noreferrer" for security.
          */}
          <a
            href="/dashboard"
            target="_blank"
            rel="noopener noreferrer"
            style={styles.ctaButton}
          >
            Get Started
          </a>
        </div>
      </section>

      {/* Features */}
      <section style={styles.featuresSection} id="features">
        <h3 style={styles.featuresHeader}>Why Plately?</h3>
        <div style={styles.featuresGrid}>
          <div style={styles.featureCard}>
            <h4 style={styles.featureTitle}>Smart Recommendations</h4>
            <p style={styles.featureDescription}>
              Our AI engine analyzes customer tastes and trends to optimize
              your menu selection.
            </p>
          </div>
          <div style={styles.featureCard}>
            <h4 style={styles.featureTitle}>Easy Integrations</h4>
            <p style={styles.featureDescription}>
              Seamlessly connect with existing POS systems for real-time
              menu updates.
            </p>
          </div>
          <div style={styles.featureCard}>
            <h4 style={styles.featureTitle}>Save Time &amp; Money</h4>
            <p style={styles.featureDescription}>
              Streamline menu operations, reduce waste, and boost
              profitability.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section style={styles.howItWorksSection} id="how-it-works">
        <h3 style={styles.howItWorksHeader}>How It Works</h3>
        <div style={styles.stepsContainer}>
          <div style={styles.stepItem}>
            <div style={styles.stepNumber}>1</div>
            <p style={styles.stepText}>
              Sign up &amp; connect your restaurant data.
            </p>
          </div>
          <div style={styles.stepItem}>
            <div style={styles.stepNumber}>2</div>
            <p style={styles.stepText}>
              Analyze menu performance &amp; customer preferences.
            </p>
          </div>
          <div style={styles.stepItem}>
            <div style={styles.stepNumber}>3</div>
            <p style={styles.stepText}>
              Deploy recommended changes &amp; track improvements.
            </p>
          </div>
        </div>
      </section>

      {/* Signup CTA */}
      <section style={styles.signupSection} id="signup">
        <h3 style={styles.signupHeader}>Ready to elevate your menu?</h3>
        <a
          href="#contact"
          style={styles.ctaButton}
        >
          Contact Us
        </a>
      </section>

      {/* Footer */}
      <footer style={styles.footer} id="contact">
        <p>
          Contact us at{" "}
          <a
            href="mailto:info@plately.ai"
            style={styles.footerLink}
          >
            info@plately.ai
          </a>
        </p>
        <p>Follow us:</p>
        <ul style={styles.socialList}>
          <li>
            <a href="https://twitter.com" style={styles.socialLink}>
              Twitter
            </a>
          </li>
          <li>
            <a href="https://linkedin.com" style={styles.socialLink}>
              LinkedIn
            </a>
          </li>
        </ul>
        <p>&copy; 2025 Plately. All rights reserved.</p>
      </footer>
    </div>
  );

  return (
    <Router>
      <Routes>
        {/*
          MAIN LANDING PAGE ("/")
          We'll display the landing page on the root path.
        */}
        <Route path="/" element={<LandingPage />} />

        {/*
          DASHBOARD PAGE ("/dashboard")
          This is rendered if the user goes to /dashboard — 
          or if they click the Get Started link which opens /dashboard in a new tab.
        */}
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
