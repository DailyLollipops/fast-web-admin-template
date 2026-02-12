import { useState } from "react";
import { useDataProvider, useNotify } from "react-admin";
import { useNavigate } from "react-router";
import {
  Avatar,
  Box,
  Button,
  Container,
  Link,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";

export const ForgotPasswordPage = () => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await dataProvider.fetchJson("/auth/forgot_password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    notify("Password reset email sent!", { type: "success" });
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        bgcolor: "grey.100",
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={4} sx={{ p: 6, borderRadius: 3 }}>
          <Box display="flex" flexDirection="column" alignItems="center">
            <Avatar sx={{ bgcolor: "primary.main", mb: 2 }}>
              <LockOutlinedIcon />
            </Avatar>
            <Typography variant="h5" gutterBottom>
              Forgot Password
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              align="center"
              sx={{ mb: 2 }}
            >
              Enter your email address and we’ll send you instructions to reset
              your password.
            </Typography>

            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ mt: 1, width: "100%" }}
            >
              <TextField
                label="Email Address"
                type="email"
                fullWidth
                required
                margin="normal"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ mt: 3 }}
              >
                Send Reset Link
              </Button>

              <Typography variant="body2" align="center" sx={{ mt: 3 }}>
                <Link
                  component="button"
                  underline="hover"
                  onClick={() => navigate("/login")}
                >
                  Back to Login
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};
