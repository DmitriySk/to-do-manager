import GitHubIcon from "@mui/icons-material/GitHub";
import GoogleIcon from "@mui/icons-material/Google";
import { Box, Button, Paper, Stack, Typography } from "@mui/material";
import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const { user, loading, login } = useAuth();

  if (!loading && user) {
    return <Navigate to="/" replace />;
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
        px: 2,
      }}
    >
      <Paper elevation={0} sx={{ p: { xs: 3, sm: 5 }, maxWidth: 400, width: "100%", border: "1px solid rgba(0,0,0,0.08)" }}>
        <Stack spacing={1} sx={{ mb: 4, textAlign: "center" }}>
          <Typography variant="h5" fontWeight={700}>
            Personal To-Do Manager
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Plan your work across projects, set priorities and deadlines, and never miss what matters today.
          </Typography>
        </Stack>

        <Stack spacing={2}>
          <Button
            variant="outlined"
            size="large"
            startIcon={<GoogleIcon />}
            onClick={() => login("google")}
            sx={{ py: 1.25 }}
          >
            Continue with Google
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<GitHubIcon />}
            onClick={() => login("github")}
            sx={{ py: 1.25 }}
          >
            Continue with GitHub
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
