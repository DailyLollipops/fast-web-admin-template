import { useState } from "react";
import { useDataProvider, useNotify } from "react-admin";
import {
  Avatar,
  Box,
  Button,
  Container,
  Paper,
  TextField,
  Typography,
  Link,
} from "@mui/material";
import PersonAddAltIcon from "@mui/icons-material/PersonAddAlt";
import { useNavigate } from "react-router-dom";

export const RegisterPage = () => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      notify("Passwords do not match", { type: "error" });
      return;
    }

    await dataProvider.fetchJson("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        name: name,
        email: email,
        password: password,
        confirm_password: confirmPassword,
      }),
    });
    notify(
      "Registration successful! Please check your email to verify your account.",
      { type: "success" },
    );
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
              <PersonAddAltIcon />
            </Avatar>
            <Typography variant="h5" gutterBottom>
              Create Your DevistLab Account
            </Typography>

            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ mt: 3, width: "100%" }}
            >
              <TextField
                label="Full Name"
                fullWidth
                required
                margin="normal"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <TextField
                label="Email Address"
                type="email"
                fullWidth
                required
                margin="normal"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <TextField
                label="Password"
                type="password"
                fullWidth
                required
                margin="normal"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
                Register
              </Button>

              <Typography
                variant="body2"
                color="text.secondary"
                align="center"
                sx={{ mt: 3 }}
              >
                Already have an account?{" "}
                <Link
                  component="button"
                  underline="hover"
                  onClick={() => navigate("/login")}
                >
                  Login here
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};
