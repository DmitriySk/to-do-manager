import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#4f46e5" },
    secondary: { main: "#0ea5e9" },
    background: { default: "#f5f6fa" },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: [
      "Inter",
      "-apple-system",
      "BlinkMacSystemFont",
      "Segoe UI",
      "Roboto",
      "Helvetica Neue",
      "Arial",
      "sans-serif",
    ].join(","),
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { textTransform: "none", fontWeight: 600 } },
    },
    MuiCard: {
      styleOverrides: { root: { border: "1px solid rgba(0,0,0,0.08)" } },
    },
  },
});
