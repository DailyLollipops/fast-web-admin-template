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

export const ResetPasswordPage = () => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    const hash = window.location.hash;
    const url = new URL("http://dummy.com" + hash.substring(1));
    const token = url.searchParams.get("token");
    console.log(token);
    await dataProvider.fetchJson(`/auth/reset_password?token=${token}`, {
      method: "POST",
      body: JSON.stringify({
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
    });
    notify("Password has been reset successfully!", { type: "success" });
    navigate("/login");
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
              Reset Password
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              align="center"
              sx={{ mb: 2 }}
            >
              Enter your new password below.
            </Typography>

            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ mt: 1, width: "100%" }}
            >
              <TextField
                label="New Password"
                type="password"
                fullWidth
                required
                margin="normal"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
              <TextField
                label="Confirm Password"
                type="password"
                fullWidth
                required
                margin="normal"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ mt: 3 }}
              >
                Reset Password
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
