import { useEffect, useState } from "react";
import { Loading, useDataProvider, useNotify } from "react-admin";
import {
  Avatar,
  Box,
  Button,
  Container,
  Link,
  Paper,
  TextField,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  CircularProgress,
} from "@mui/material";
import { Security } from "@mui/icons-material";

type TfaMethod = "authenticator" | "email";

const EMAIL_COOLDOWN_SECONDS = 60;

export const TfaVerificationWindow = () => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const [otp, setOtp] = useState("");
  const [allowedMethods, setAllowedMethods] = useState<TfaMethod[]>([]);
  const [method, setMethod] = useState<TfaMethod | null>(null);
  const [loading, setLoading] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);

  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown <= 0) return;

    const timer = setInterval(() => {
      setCooldown((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [cooldown]);

  useEffect(() => {
    if (!document.location) return;

    const params = new URLSearchParams(
      window.location.toString().split("?")[1],
    );

    const tfaToken = params.get("tfa_token");
    const userInfo = params.get("user_info");
    const methodsParam = params.get("methods");

    if (tfaToken) {
      document.cookie = `tfa_token=${tfaToken}; path=/; secure; samesite=lax`;
    }

    if (userInfo) {
      document.cookie = `user_info=${userInfo}; path=/; secure; samesite=lax`;
    }

    if (methodsParam) {
      const parsed = methodsParam.split(",") as TfaMethod[];
      console.log("Allowed 2FA methods:", parsed);
      setAllowedMethods(parsed);
      if (parsed.length > 0) {
        setMethod(parsed[0]);
      }
    }
  }, []);

  const handleMethodChange = (
    _: React.MouseEvent<HTMLElement>,
    newMethod: TfaMethod | null,
  ) => {
    if (newMethod) {
      setMethod(newMethod);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { json } = await dataProvider.fetchJson(
        `/auth/tfa/verify/${method}?code=${otp}`,
        {
          method: "POST",
          cookies: "include",
        },
      );
      if (!json.verified) {
        notify("Invalid verification code.", { type: "error" });
        return;
      }
      notify("Verification successful", { type: "success" });

      if (window.opener) {
        window.opener.postMessage("login-success", window.location.origin);
        window.close();
      } else {
        window.location.href = "/";
      }
    } catch {
      notify("Invalid verification code", { type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmailCode = async () => {
    if (cooldown > 0) return;

    setSendingEmail(true);
    try {
      dataProvider.fetchJson(`/auth/tfa/send_email`, {
        method: "POST",
        cookies: "include",
      });
      notify("Verification code sent to your email", { type: "info" });

      // Start cooldown
      setCooldown(EMAIL_COOLDOWN_SECONDS);
    } catch {
      notify("Failed to send email code", { type: "error" });
    } finally {
      setSendingEmail(false);
    }
  };

  const resendLabel = () => {
    if (sendingEmail) return <CircularProgress size={16} />;
    if (cooldown > 0) return `Resend code (${cooldown}s)`;
    return "Resend code";
  };

  if (!method) {
    <Loading />;
  }

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
              <Security />
            </Avatar>

            <Typography variant="h5" gutterBottom>
              Two-Factor Authentication
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              align="center"
              sx={{ mb: 3 }}
            >
              Enter the verification code from your selected method.
            </Typography>

            <ToggleButtonGroup
              value={method}
              exclusive
              onChange={handleMethodChange}
              sx={{ mb: 3 }}
              fullWidth
            >
              <ToggleButton
                value="authenticator"
                disabled={!allowedMethods.includes("authenticator")}
              >
                Authenticator App
              </ToggleButton>

              <ToggleButton
                value="email"
                disabled={!allowedMethods.includes("email")}
              >
                Email
              </ToggleButton>
            </ToggleButtonGroup>

            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ width: "100%" }}
            >
              <TextField
                label="Verification Code"
                fullWidth
                required
                margin="normal"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                slotProps={{
                  htmlInput: { maxLength: 6 },
                }}
              />

              {method === "email" && (
                <Box sx={{ textAlign: "right", mt: 1 }}>
                  <Link
                    component="button"
                    type="button"
                    underline="hover"
                    onClick={handleSendEmailCode}
                    disabled={cooldown > 0 || sendingEmail}
                    sx={{
                      pointerEvents:
                        cooldown > 0 || sendingEmail ? "none" : "auto",
                      color: cooldown > 0 ? "text.disabled" : "primary.main",
                    }}
                  >
                    {resendLabel()}
                  </Link>
                </Box>
              )}

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ mt: 3 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={22} /> : "Verify"}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};
