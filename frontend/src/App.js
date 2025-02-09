import React, { useState } from "react";
import axios from "axios";
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  Box,
  CssBaseline,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Grid,
  Button,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  Tabs,
  Tab,
  InputBase
} from "@mui/material";

import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableHead from "@mui/material/TableHead";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";

import SearchIcon from "@mui/icons-material/Search";
import HistoryIcon from "@mui/icons-material/History";
import MenuIcon from "@mui/icons-material/Menu";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import PaymentsIcon from "@mui/icons-material/Payments";

import {
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from "recharts";

// --- THEME / COLORS ---
const drawerWidthExpanded = 220;
const drawerWidthCollapsed = 70;

const themeColors = {
  // Dashboard screenshot style
  primary: "#6948ff",       // a lively purple
  secondary: "#60da63",     // a green accent (for charts, etc.)
  background: "#f5f2fe",    // light pastel purple background
  cardBackground: "#ffffff",
  textPrimary: "#333333",
  textSecondary: "#999999",
};

// Fake brand-like accent for the top-left logo area
const brandAccentColor = "#9077f7";

// --------------- COMPONENT ---------------
function App() {
  const [apiData, setApiData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  const COLORS = ["#60da63", "#ff4081", "#2196f3", "#ffc107"];

  const toggleSidebar = () => {
    setIsSidebarExpanded((prev) => !prev);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleOptimizePrices = async () => {
    setError("");
    setApiData(null);
    setLoading(true);

    try {
      // Replace with your FastAPI endpoint
      const response = await axios.post("http://127.0.0.1:8000/optimize-prices");
      setApiData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error optimizing prices.");
    } finally {
      setLoading(false);
    }
  };

  // Helper: safe array of results from backend
  const results = apiData?.results || [];
  const totalProfitFromResults = results.reduce(
    (sum, result) => sum + (result.expected_profit || 0),
    0
  );

  // ----------------- RENDER --------------------
  return (
    <Box sx={{ display: "flex", backgroundColor: themeColors.background, minHeight: "100vh" }}>
      <CssBaseline />

      {/* =============== SIDEBAR =============== */}
      <Drawer
        variant="permanent"
        sx={{
          width: isSidebarExpanded ? drawerWidthExpanded : drawerWidthCollapsed,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: isSidebarExpanded ? drawerWidthExpanded : drawerWidthCollapsed,
            boxSizing: "border-box",
            transition: "width 0.3s ease-in-out",
            backgroundColor: "#fff",
            borderRight: "1px solid #e0e0e0",
            overflowX: "hidden",
          },
        }}
      >
        {/* Top brand area */}
        <Box
          sx={{
            height: 60,
            backgroundColor: brandAccentColor,
            display: "flex",
            alignItems: "center",
            justifyContent: isSidebarExpanded ? "center" : "center",
          }}
        >
          {isSidebarExpanded ? (
            <Typography variant="h6" sx={{ color: "#fff", fontWeight: 600 }}>
              Logo
            </Typography>
          ) : (
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: "#fff",
              }}
            />
          )}
        </Box>

        <List sx={{ mt: 2 }}>
          <ListItem button onClick={toggleSidebar}>
            <ListItemIcon>
              <MenuIcon />
            </ListItemIcon>
            {isSidebarExpanded && <ListItemText primary="Toggle Menu" />}
          </ListItem>

          <Divider sx={{ my: 2 }} />

          <ListItem button>
            <ListItemIcon>
              <HistoryIcon />
            </ListItemIcon>
            {isSidebarExpanded && <ListItemText primary="Recents" />}
          </ListItem>

          <ListItem button>
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            {isSidebarExpanded && <ListItemText primary="Dashboard" />}
          </ListItem>

          <ListItem button>
            <ListItemIcon>
              <PeopleIcon />
            </ListItemIcon>
            {isSidebarExpanded && <ListItemText primary="Teams" />}
          </ListItem>

          <ListItem button>
            <ListItemIcon>
              <AccountCircleIcon />
            </ListItemIcon>
            {isSidebarExpanded && <ListItemText primary="Account" />}
          </ListItem>

          <ListItem button>
            <ListItemIcon>
              <PaymentsIcon />
            </ListItemIcon>
            {isSidebarExpanded && <ListItemText primary="Payments" />}
          </ListItem>
        </List>
      </Drawer>

      {/* =============== MAIN CONTENT =============== */}
      <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
        {/* TOP APP BAR: TABS + SEARCH, etc. */}
        <AppBar
          position="static"
          sx={{
            backgroundColor: themeColors.primary,
            boxShadow: "none",
            borderRadius: "0 0 20px 20px",
            px: 2,
          }}
        >
          <Toolbar sx={{ minHeight: 60, display: "flex", justifyContent: "space-between" }}>
            {/* Left: Tabs (Overview, Member, Account, Payment) */}
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              textColor="inherit"
              TabIndicatorProps={{ style: { backgroundColor: "#fff" } }}
              sx={{
                "& .MuiTab-root": { textTransform: "none", fontWeight: 500 },
                "& .Mui-selected": { color: "#fff" },
              }}
            >
              <Tab label="Overview" />
              <Tab label="Member" />
              <Tab label="Account" />
              <Tab label="Payment" />
            </Tabs>

            {/* Right: Search bar */}
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                backgroundColor: "rgba(255,255,255,0.2)",
                borderRadius: 2,
                px: 2,
                py: 0.5,
              }}
            >
              <SearchIcon sx={{ color: "#fff", mr: 1 }} />
              <InputBase
                placeholder="Search..."
                sx={{ color: "#fff", width: 120 }}
              />
            </Box>
          </Toolbar>
        </AppBar>

        {/* MAIN SCROLLABLE CONTENT */}
        <Box component="main" sx={{ flexGrow: 1, p: 2 }}>
          {/* GREETING + SMALL TEXT */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, color: themeColors.textPrimary }}>
              Dashboard
            </Typography>
          </Box>
          {/* PRICE OPTIMIZATION ACTION (replacing your old card) */}
          <Paper
            elevation={2}
            sx={{
              p: 3,
              mb: 3,
              borderRadius: 3,
              backgroundColor: themeColors.cardBackground,
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              Run AI Menu Price Optimization
            </Typography>
            <Button
              variant="contained"
              onClick={handleOptimizePrices}
              disabled={loading}
              sx={{
                backgroundColor: themeColors.secondary,
                "&:hover": { backgroundColor: "#4CAF50" },
                borderRadius: 2,
                px: 3,
                fontWeight: 700,
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : "Optimize Now"}
            </Button>
          </Paper>

          {/* Show Error if any */}
          {error && (
            <Alert
              severity="error"
              sx={{
                mb: 4,
                borderRadius: 2,
                fontSize: "0.9rem",
              }}
            >
              {error}
            </Alert>
          )}

          {/* If we have data from the API, display it */}
          {apiData && (
            <>
              {/* CHARTS & ANALYTICS */}
              <Grid container spacing={2} sx={{ mb: 2 }}>
                {/* Sale Analysis (similar to screenshot) */}
                <Grid item xs={12} md={8}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Sale Analysis
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap" }}>
                      {/* Let’s put the bar chart in here */}
                      <Box sx={{ flex: "1 1 100%", height: 300 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={results}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="dish_id" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="expected_profit" fill={themeColors.secondary} />
                          </BarChart>
                        </ResponsiveContainer>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>

                {/* Example: a small card or placeholder for "December Calendar" like screenshot */}
                <Grid item xs={12} md={4}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3, height: "100%" }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      December
                    </Typography>
                    {/* Just a placeholder: you might integrate a real calendar */}
                    <Box
                      sx={{
                        backgroundColor: "#f5f5f5",
                        borderRadius: 2,
                        p: 2,
                        textAlign: "center",
                        color: "#666",
                      }}
                    >
                      <Typography variant="body1">Calendar Goes Here</Typography>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>

              <Grid container spacing={2} sx={{ mb: 2 }}>
                {/* Pie Chart for "Top Tokens" or "Profit Contribution" */}
                <Grid item xs={12} md={4}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Top Tokens (Example)
                    </Typography>
                    {/* Or you can rename it to "Profit by Dish" */}
                    <Box sx={{ width: "100%", height: 250 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={results}
                            dataKey="expected_profit"
                            nameKey="dish_id"
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            label
                          >
                            {results.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </Paper>
                </Grid>

                {/* Another small card for something like "Top View Performance" */}
                <Grid item xs={12} md={8}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Top View Performance
                    </Typography>
                    <Box sx={{ backgroundColor: "#f5f5f5", borderRadius: 2, p: 2 }}>
                      {/* Put any chart or info here */}
                      <Typography variant="body2">
                        Placeholder for second chart or stats
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>

              {/* Additional Info from AI explanation or co-occurrence */}
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} md={6}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Co-occurrence Insights
                    </Typography>
                    <Typography variant="body1">
                      {apiData.co_occurrence_info || "N/A"}
                    </Typography>
                  </Paper>
                </Grid>      
              </Grid>

              {/* KIPs if you want them somewhere else */}
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} md={4}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="subtitle2" sx={{ color: themeColors.textSecondary }}>
                      Baseline Profit
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      ${apiData.baseline_profit?.toFixed(2)}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="subtitle2" sx={{ color: themeColors.textSecondary }}>
                      Optimized Profit
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      ${apiData.optimized_profit?.toFixed(2)}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="subtitle2" sx={{ color: themeColors.textSecondary }}>
                      Sum of Expected Profits
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      ${totalProfitFromResults.toFixed(2)}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* RESULTS TABLE */}
              <Paper elevation={3} sx={{ p: 3, borderRadius: 3, mb: 4 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Optimization Results
                </Typography>
                <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                  <Table>
                    <TableHead sx={{ backgroundColor: "#f9f9f9" }}>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Dish ID</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Dish Name</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Current Price</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Optimized Price</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Expected Profit</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Expected Demand</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Elasticity</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Price Diff</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {results.map((item, index) => (
                        <TableRow key={index} hover>
                          <TableCell>{item.dish_id}</TableCell>
                          <TableCell>{item.dish_name || "N/A"}</TableCell>
                          <TableCell>
                            {item.current_price
                              ? `$${item.current_price.toFixed(2)}`
                              : "N/A"}
                          </TableCell>
                          <TableCell>
                            {item.optimal_price
                              ? `$${item.optimal_price.toFixed(2)}`
                              : "N/A"}
                          </TableCell>
                          <TableCell>
                            {item.expected_profit
                              ? `$${item.expected_profit.toFixed(2)}`
                              : "N/A"}
                          </TableCell>
                          <TableCell>{item.expected_demand ?? "N/A"}</TableCell>
                          <TableCell>
                            {item.elasticity !== null && item.elasticity !== undefined
                              ? item.elasticity.toFixed(2)
                              : "N/A"}
                          </TableCell>
                          <TableCell
                            sx={{
                              color:
                                item.optimal_price - item.current_price > 0 ? "green" : "red",
                              fontWeight: 600,
                            }}
                          >
                            {item.optimal_price && item.current_price
                              ? `$${(item.optimal_price - item.current_price).toFixed(2)}`
                              : "N/A"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default App;
