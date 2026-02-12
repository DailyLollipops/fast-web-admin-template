import { useState } from "react";
import { useLogin, useNotify } from "react-admin";
import { useNavigate } from "react-router";
import {
  Avatar,
  Box,
  Button,
  Checkbox,
  Container,
  Divider,
  FormControlLabel,
  Link,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import { LockOutline } from "@mui/icons-material";
import { GoogleSignInButton } from "@/components";

export const LoginPage = () => {
  const login = useLogin();
  const notify = useNotify();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login({
      username: email,
      password: password,
      remember: rememberMe,
    }).catch(() => notify("Invalid email or password"));
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
              <LockOutline />
            </Avatar>
            <Typography variant="h5" gutterBottom>
              Application Login
            </Typography>

            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ mt: 3, width: "100%" }}
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
              <TextField
                label="Password"
                type="password"
                fullWidth
                required
                margin="normal"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />

              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mt: 1,
                  mb: 2,
                }}
              >
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Remember me"
                />
                <Link
                  component="button"
                  type="button"
                  underline="hover"
                  onClick={() => navigate("/forgot-password")}
                >
                  Forgot password?
                </Link>
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ mt: 3 }}
              >
                Login
              </Button>

              <Divider sx={{ my: 2 }}>OR</Divider>
              <GoogleSignInButton
                onClick={() => {
                  login({
                    provider: "google",
                    returnTo: "/",
                    remember: rememberMe,
                  });
                }}
              />

              <Typography
                variant="body2"
                color="text.secondary"
                align="center"
                sx={{ mt: 3 }}
              >
                Don&apos;t have an account?{" "}
                <Link
                  component="button"
                  underline="hover"
                  onClick={() => navigate("/register")}
                >
                  Register here
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};
