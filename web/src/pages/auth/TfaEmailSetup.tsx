import { useState, useEffect } from "react";
import { useDataProvider, useNotify, useRefresh } from "react-admin";
import {
  Stack,
  Typography,
  TextField,
  Button,
  Alert,
  Divider,
  InputAdornment,
} from "@mui/material";

interface TfaEmailSetupProps {
  enabled?: boolean;
}

export const TfaEmailSetup = ({ enabled = false }: TfaEmailSetupProps) => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [tested, setTested] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (!cooldown) return;
    const timer = setInterval(() => setCooldown((c) => c - 1), 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  const handleSendEmail = async () => {
    setError(null);
    setLoading(true);
    try {
      await dataProvider.fetchJson("/auth/tfa/setup/email", { method: "POST" });
      setCooldown(30);
      setTested(false);
      setOtp("");
    } catch (error: unknown) {
      notify(error instanceof Error ? error.message : "Failed to send email", {
        type: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    setError(null);
    if (otp.length !== 6) {
      setError("Enter a valid 6-digit code.");
      return;
    }
    setLoading(true);
    try {
      const { json } = await dataProvider.fetchJson(
        `/auth/tfa/verify/email?code=${otp}`,
        { method: "POST" },
      );
      if (!json.verified) {
        setError("Invalid verification code.");
        return;
      }
      setTested(true);
    } catch {
      setError("Invalid verification code.");
    } finally {
      setLoading(false);
    }
  };

  const handleEnable2FA = async () => {
    setLoading(true);
    try {
      await dataProvider.fetchJson(`/auth/tfa/enable/email`, {
        method: "POST",
      });
      setOtp("");
      setTested(false);
      notify("Email-based 2FA enabled", { type: "success" });
      refresh();
    } catch {
      notify("Failed to enable 2FA", { type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    setLoading(true);
    try {
      await dataProvider.fetchJson(`/auth/tfa/disable/email`, {
        method: "POST",
      });
      setOtp("");
      setTested(false);
      notify("Email-based 2FA disabled", { type: "warning" });
      refresh();
    } catch {
      notify("Failed to disable 2FA", { type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={3}>
      {enabled ? (
        <>
          <Alert severity="success">
            Email-based two-factor authentication is enabled.
          </Alert>
          <Typography variant="body2">
            To disable email-based 2FA, enter a valid verification code sent to
            your email.
          </Typography>

          <TextField
            label="6-digit verification code"
            value={otp}
            onChange={(e) =>
              setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
            }
            error={!!error}
            helperText={error ?? "Enter the code to test before disabling"}
            disabled={loading}
            fullWidth
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <Button
                      variant="outlined"
                      onClick={handleSendEmail}
                      disabled={loading || cooldown > 0}
                    >
                      {cooldown > 0 ? `Resend in ${cooldown}s` : "Send email"}
                    </Button>
                  </InputAdornment>
                ),
              },
            }}
          />

          {tested && (
            <Alert severity="success">
              Code verified. You can now disable 2FA.
            </Alert>
          )}

          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              onClick={handleVerifyOtp}
              disabled={loading || otp.length !== 6}
            >
              Test code
            </Button>

            <Button
              color="error"
              variant="contained"
              onClick={handleDisable2FA}
              disabled={!tested || loading}
            >
              Disable 2FA
            </Button>
          </Stack>
        </>
      ) : (
        <>
          <Typography variant="body2">
            We’ll send a one-time verification code to your email address.
          </Typography>

          <TextField
            label="6-digit verification code"
            value={otp}
            onChange={(e) =>
              setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
            }
            error={!!error}
            helperText={
              error ??
              (tested
                ? "Code verified! You can enable 2FA."
                : "Enter the code from your email")
            }
            disabled={loading}
            fullWidth
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <Button
                      variant="outlined"
                      onClick={handleSendEmail}
                      disabled={loading || cooldown > 0}
                    >
                      {cooldown > 0 ? `Resend in ${cooldown}s` : "Send email"}
                    </Button>
                  </InputAdornment>
                ),
              },
            }}
          />

          {tested && (
            <Alert severity="success">
              Code verified successfully. You can now enable 2FA.
            </Alert>
          )}

          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              onClick={handleVerifyOtp}
              disabled={loading || otp.length !== 6}
            >
              Test code
            </Button>

            <Button
              variant="contained"
              onClick={handleEnable2FA}
              disabled={!tested || loading}
            >
              Enable 2FA
            </Button>
          </Stack>
        </>
      )}

      <Divider />
    </Stack>
  );
};
