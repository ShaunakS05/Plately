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
  InputBase,
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
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
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";

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
import D3Heatmap from "./D3Heatmap";

// --- CONSTANTS & COLORS ---
const drawerWidthExpanded = 220;
const drawerWidthCollapsed = 70;

const themeColors = {
  primary: "#6948ff",
  secondary: "#60da63",
  background: "#f5f2fe",
  cardBackground: "#ffffff",
  textPrimary: "#333333",
  textSecondary: "#999999",
};

const brandAccentColor = "#9077f7";

// --- CREATE A CUSTOM THEME ---
const theme = createTheme({
  palette: {
    primary: {
      main: themeColors.primary,
    },
    secondary: {
      main: themeColors.secondary,
    },
    background: {
      default: themeColors.background,
      paper: themeColors.cardBackground,
    },
    text: {
      primary: themeColors.textPrimary,
      secondary: themeColors.textSecondary,
    },
  },
  typography: {
    fontFamily: '"Roboto", sans-serif',
    h4: { fontWeight: 700, color: themeColors.textPrimary },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: "#2b2b2b",
          color: "#fff",
          borderRight: "none",
          transition: "width 0.3s ease-in-out",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: "none",
          fontWeight: 600,
          padding: "8px 16px",
        },
      },
    },
  },
});

// --- MAIN COMPONENT ---
function App() {
  const [apiData, setApiData] = useState(null);

  const [comboData, setComboData] = useState(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [expandedRows, setExpandedRows] = useState({});
  const [dishDetails, setDishDetails] = useState({});

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
      const responseCombo = await axios.post("http://127.0.0.1:8000/combo-popularity")
      setApiData(response.data);
      setComboData(responseCombo.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error optimizing prices.");
    } finally {
      setLoading(false);
    }
  };

  // Expand/collapse a dish row and fetch extra details if needed
  const handleToggleRow = async (dishId) => {
    const wasExpanded = expandedRows[dishId] || false;
    const isExpanding = !wasExpanded;

    setExpandedRows((prev) => ({
      ...prev,
      [dishId]: isExpanding,
    }));

    if (isExpanding && !dishDetails[dishId]) {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/heatscores/${dishId}`);
        setDishDetails((prev) => ({
          ...prev,
          [dishId]: response.data,
        }));
      } catch (err) {
        console.error("Error fetching dish details:", err);
      }
    }
  };

  const results = apiData?.results || [];
  const totalProfitFromResults = results.reduce(
    (sum, result) => sum + (result.expected_profit || 0),
    0
  );

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          display: "flex",
          backgroundColor: theme.palette.background.default,
          minHeight: "100vh",
        }}
      >
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
              backgroundColor: "#2b2b2b",
              color: "#fff",
              borderRight: "none",
              overflowX: "hidden",
            },
          }}
        >
          <Box
            sx={{
              height: 60,
              backgroundColor: brandAccentColor,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {isSidebarExpanded ? (
              <Typography variant="h6" sx={{ color: "#fff", fontWeight: 600 }}>
                Plately
              </Typography>
            ) : (
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  backgroundColor: "#fff",
                }}
              />
            )}
          </Box>

          <List sx={{ mt: 2 }}>
            <ListItem button onClick={toggleSidebar} sx={{ "&:hover": { backgroundColor: "#3a3a3a" } }}>
              <ListItemIcon sx={{ color: "#fff" }}>
                <MenuIcon />
              </ListItemIcon>
              {isSidebarExpanded && <ListItemText primary="Toggle Menu" />}
            </ListItem>

            <Divider sx={{ my: 2, backgroundColor: "#444" }} />

            <ListItem button sx={{ "&:hover": { backgroundColor: "#3a3a3a" } }}>
              <ListItemIcon sx={{ color: "#fff" }}>
                <HistoryIcon />
              </ListItemIcon>
              {isSidebarExpanded && <ListItemText primary="Recents" />}
            </ListItem>

            <ListItem button sx={{ "&:hover": { backgroundColor: "#3a3a3a" } }}>
              <ListItemIcon sx={{ color: "#fff" }}>
                <DashboardIcon />
              </ListItemIcon>
              {isSidebarExpanded && <ListItemText primary="Dashboard" />}
            </ListItem>

            <ListItem button sx={{ "&:hover": { backgroundColor: "#3a3a3a" } }}>
              <ListItemIcon sx={{ color: "#fff" }}>
                <PeopleIcon />
              </ListItemIcon>
              {isSidebarExpanded && <ListItemText primary="Teams" />}
            </ListItem>

            <ListItem button sx={{ "&:hover": { backgroundColor: "#3a3a3a" } }}>
              <ListItemIcon sx={{ color: "#fff" }}>
                <AccountCircleIcon />
              </ListItemIcon>
              {isSidebarExpanded && <ListItemText primary="Account" />}
            </ListItem>

            <ListItem button sx={{ "&:hover": { backgroundColor: "#3a3a3a" } }}>
              <ListItemIcon sx={{ color: "#fff" }}>
                <PaymentsIcon />
              </ListItemIcon>
              {isSidebarExpanded && <ListItemText primary="Payments" />}
            </ListItem>
          </List>
        </Drawer>

        {/* =============== MAIN CONTENT =============== */}
        <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
          <AppBar
            position="static"
            sx={{
              background: `linear-gradient(90deg, ${themeColors.primary} 0%, ${brandAccentColor} 100%)`,
              boxShadow: "none",
              borderRadius: "0 0 20px 20px",
              px: 2,
            }}
          >
            <Toolbar sx={{ minHeight: 60, display: "flex", justifyContent: "space-between" }}>
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
                <InputBase placeholder="Search..." sx={{ color: "#fff", width: 120 }} />
              </Box>
            </Toolbar>
          </AppBar>

          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Typography variant="h4" sx={{ mb: 3 }}>
              Dashboard
            </Typography>

            <Paper
              elevation={3}
              sx={{
                p: 3,
                mb: 3,
                borderRadius: 3,
                backgroundColor: theme.palette.background.paper,
              }}
            >
              <Typography variant="h6" sx={{ mb: 2 }}>
                Run AI Menu Price Optimization
              </Typography>
              <Button
                variant="contained"
                onClick={handleOptimizePrices}
                disabled={loading}
                sx={{
                  background: `linear-gradient(90deg, ${themeColors.secondary} 0%, #4CAF50 100%)`,
                  "&:hover": {
                    background: `linear-gradient(90deg, #4CAF50 0%, ${themeColors.secondary} 100%)`,
                  },
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : "Optimize Now"}
              </Button>
            </Paper>

            {error && (
              <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                {error}
              </Alert>
            )}

            {apiData && (
              <>
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={8}>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Sale Analysis
                      </Typography>
                      <Box sx={{ height: 300 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={apiData.results}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="dish_id" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="expected_profit" fill={themeColors.secondary} />
                          </BarChart>
                        </ResponsiveContainer>
                      </Box>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, height: "100%" }}>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Top Combos:
                      </Typography>
                      {/* Check if comboData exists before rendering */}
    {comboData ? (
      <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>Combo Items</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>Popularity Score</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {comboData.top_combos.map((combo, index) => (
              <TableRow key={index}>
                {/* Map combo items and join names with ", " */}
                <TableCell>
                  {combo.combo_items.map((item) => item.name).join(", ")}
                </TableCell>
                <TableCell>{combo.popularityScore}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    ) : (
      <Typography variant="body2">No combo data available.</Typography>
    )}
                      
                    </Paper>
                  </Grid>
                </Grid>

                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Top Tokens (Example)
                      </Typography>
                      <Box sx={{ width: "100%", height: 250 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={apiData.results}
                              dataKey="expected_profit"
                              nameKey="dish_id"
                              cx="50%"
                              cy="50%"
                              outerRadius={80}
                              label
                            >
                              {apiData.results.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </Box>
                    </Paper>
                  </Grid>

                  
                </Grid>

                

                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                      <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary }}>
                        Baseline Profit
                      </Typography>
                      <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        ${apiData.baseline_profit?.toFixed(2)}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                      <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary }}>
                        Optimized Profit
                      </Typography>
                      <Typography variant="h4" sx={{ fontWeight: 600 }}>
                        ${apiData.optimized_profit?.toFixed(2)}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                      <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary }}>
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
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Optimization Results
                  </Typography>

                  <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                    <Table>
                      <TableHead sx={{ backgroundColor: "#f0f0f0" }}>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>#</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Dish ID</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Dish Name</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Current Price</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Optimized Price</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Expected Profit</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Expected Demand</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Elasticity</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Price Diff</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {results.map((item, index) => {
                          const isExpanded = expandedRows[item.dish_id] || false;
                          return (
                            <React.Fragment key={item.dish_id}>
                              <TableRow hover>
                                <TableCell>{index + 1}</TableCell>
                                <TableCell>{item.dish_id}</TableCell>
                                <TableCell>{item.dish_name || "N/A"}</TableCell>
                                <TableCell>
                                  {item.current_price ? `$${item.current_price.toFixed(2)}` : "N/A"}
                                </TableCell>
                                <TableCell>
                                  {item.optimal_price ? `$${item.optimal_price.toFixed(2)}` : "N/A"}
                                </TableCell>
                                <TableCell>
                                  {item.expected_profit ? `$${item.expected_profit.toFixed(2)}` : "N/A"}
                                </TableCell>
                                <TableCell>{item.expected_demand ?? "N/A"}</TableCell>
                                <TableCell>
                                  {item.elasticity !== null && item.elasticity !== undefined
                                    ? item.elasticity.toFixed(2)
                                    : "N/A"}
                                </TableCell>
                                <TableCell
                                  sx={{
                                    color: item.optimal_price - item.current_price > 0 ? "green" : "red",
                                    fontWeight: 600,
                                  }}
                                >
                                  {item.optimal_price && item.current_price
                                    ? `$${(item.optimal_price - item.current_price).toFixed(2)}`
                                    : "N/A"}
                                </TableCell>
                                <TableCell>
                                  <IconButton onClick={() => handleToggleRow(item.dish_id)}>
                                    {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                  </IconButton>
                                </TableCell>
                              </TableRow>

                              {/* Expanded row content */}
                              {isExpanded && (
                                <TableRow>
                                  <TableCell colSpan={10} sx={{ backgroundColor: "#f9f9f9" }}>
                                    {dishDetails[item.dish_id] ? (
                                      <Box sx={{ py: 2 }}>
                                        <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
                                          Extra Details for Dish ID: {item.dish_id}
                                        </Typography>
                                        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
                                          <D3Heatmap
                                            dataObject={dishDetails[item.dish_id]}
                                            season="Winter"
                                            width={500}
                                            height={400}
                                          />
                                          <D3Heatmap
                                            dataObject={dishDetails[item.dish_id]}
                                            season="Spring"
                                            width={500}
                                            height={400}
                                          />
                                          <D3Heatmap
                                            dataObject={dishDetails[item.dish_id]}
                                            season="Fall"
                                            width={500}
                                            height={400}
                                          />
                                          <D3Heatmap
                                            dataObject={dishDetails[item.dish_id]}
                                            season="Summer"
                                            width={500}
                                            height={400}
                                          />
                                        </Box>
                                      </Box>
                                    ) : (
                                      <Typography variant="body2" sx={{ py: 2 }}>
                                        Loading details...
                                      </Typography>
                                    )}
                                  </TableCell>
                                </TableRow>
                              )}
                            </React.Fragment>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </>
            )}
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;