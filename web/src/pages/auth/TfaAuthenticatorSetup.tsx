import { useEffect, useState } from "react";
import { useDataProvider, useNotify, useRefresh } from "react-admin";
import {
  Stack,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  Divider,
} from "@mui/material";
import { QRCodeSVG } from "qrcode.react";

interface TfaAuthenticatorSetupProps {
  enabled?: boolean;
}

export const TfaAuthenticatorSetup = ({
  enabled = false,
}: TfaAuthenticatorSetupProps) => {
  const notify = useNotify();
  const refresh = useRefresh();
  const dataProvider = useDataProvider();

  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [tested, setTested] = useState(false);

  useEffect(() => {
    const fetchQrCode = async () => {
      try {
        const { json } = await dataProvider.fetchJson(
          "/auth/tfa/setup/authenticator",
          { method: "POST" },
        );
        if (!enabled) {
          setQrCodeUrl(json.tfa_link);
        }
      } catch (error) {
        console.error("Error setting up authenticator 2FA:", error);
        notify("Failed to set up authenticator 2FA. Please try again.", {
          type: "error",
        });
      }
    };

    fetchQrCode();
  }, [dataProvider, enabled, notify]);

  const handleVerifyOtp = async () => {
    setError(null);

    if (otp.length !== 6) {
      setError("Enter a valid 6-digit code.");
      return;
    }

    setLoading(true);
    try {
      const { json } = await dataProvider.fetchJson(
        `/auth/tfa/verify/authenticator?code=${otp}`,
        { method: "POST" },
      );
      if (!json.verified) {
        setError("Invalid verification code.");
        setTested(false);
        return;
      }
      setTested(true);
    } catch {
      setError("Invalid verification code.");
      setTested(false);
    } finally {
      setLoading(false);
    }
  };

  const handleEnable2FA = async () => {
    setLoading(true);
    try {
      await dataProvider.fetchJson(`/auth/tfa/enable/authenticator`, {
        method: "POST",
      });
      setOtp("");
      setTested(false);
      notify("Authenticator-based 2FA enabled", { type: "success" });
      refresh();
    } catch {
      notify("Failed to enable authenticator 2FA", { type: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    setLoading(true);
    try {
      await dataProvider.fetchJson(`/auth/tfa/disable/authenticator`, {
        method: "POST",
      });
      setOtp("");
      setTested(false);
      notify("Authenticator-based 2FA disabled", { type: "warning" });
      refresh();
    } catch {
      notify("Failed to disable authenticator 2FA", { type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={3}>
      {enabled ? (
        <>
          <Alert severity="success">
            Authenticator-based two-factor authentication is enabled.
          </Alert>
          <Typography variant="body2">
            To disable authenticator-based 2FA, enter a valid code from your
            authenticator app.
          </Typography>

          <TextField
            label="6-digit verification code"
            value={otp}
            onChange={(e) =>
              setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
            }
            fullWidth
            error={!!error}
            helperText={error ?? "Test the code before disabling 2FA"}
            disabled={loading}
          />

          {tested && (
            <Alert severity="success">
              Code verified successfully. You can now disable 2FA.
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
            Scan the QR code using your authenticator app and enter the 6-digit
            code below.
          </Typography>

          {qrCodeUrl ? (
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                p: 2,
                border: "1px dashed",
                borderColor: "divider",
                borderRadius: 1,
                width: "100%",
              }}
            >
              <QRCodeSVG value={qrCodeUrl} size={160} level="M" includeMargin />
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              Loading QR code…
            </Typography>
          )}

          <TextField
            label="6-digit verification code"
            value={otp}
            onChange={(e) =>
              setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
            }
            error={!!error}
            helperText={error ?? "Enter the code from your authenticator app"}
            disabled={loading}
            fullWidth
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
