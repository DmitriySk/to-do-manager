import { Box, CircularProgress } from "@mui/material";

export default function LoadingSpinner({ label = "Loading" }: { label?: string }) {
  return (
    <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
      <CircularProgress aria-label={label} size={32} />
    </Box>
  );
}
