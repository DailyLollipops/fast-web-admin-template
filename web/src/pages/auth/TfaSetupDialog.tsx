import { useState } from "react";
import { useGetIdentity } from "react-admin";
import {
  Alert,
  Box,
  Card,
  CardActionArea,
  CardContent,
  Dialog,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
  IconButton,
} from "@mui/material";
import { ArrowBack, EmailOutlined, LockOutline } from "@mui/icons-material";
import { TfaAuthenticatorSetup } from "./TfaAuthenticatorSetup";
import { TfaEmailSetup } from "./TfaEmailSetup";

interface TfaSetupDialogProps {
  open: boolean;
  onClose: () => void;
}

type TfaMethod = "authenticator" | "email" | null;

export const TfaSetupDialog = ({ open, onClose }: TfaSetupDialogProps) => {
  const { identity } = useGetIdentity();
  const [method, setMethod] = useState<TfaMethod>(null);

  const handleClose = () => {
    setMethod(null);
    onClose();
  };

  const enabledMethods: string[] = identity?.tfa_methods || [];

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        {method && (
          <IconButton size="small" onClick={() => setMethod(null)}>
            <ArrowBack />
          </IconButton>
        )}
        {method ? "Verify your identity" : "Set up Two-Factor Authentication"}
      </DialogTitle>

      <DialogContent>
        {!method && (
          <MethodSelection
            onSelect={setMethod}
            enabledMethods={enabledMethods}
          />
        )}

        {method === "authenticator" && (
          <TfaAuthenticatorSetup
            enabled={enabledMethods.includes("authenticator")}
          />
        )}

        {method === "email" && (
          <TfaEmailSetup enabled={enabledMethods.includes("email")} />
        )}
      </DialogContent>
    </Dialog>
  );
};

const MethodSelection = ({
  onSelect,
  enabledMethods,
}: {
  onSelect: (method: TfaMethod) => void;
  enabledMethods: string[];
}) => (
  <>
    <Typography variant="body2" color="text.secondary" mb={3}>
      Choose how you’d like to receive your verification codes.
    </Typography>

    <Stack spacing={2}>
      <Card variant="outlined">
        <CardContent>
          <Stack spacing={2}>
            <Alert
              severity={
                enabledMethods.includes("authenticator") ? "success" : "warning"
              }
            >
              {enabledMethods.includes("authenticator")
                ? "Authenticator 2FA is enabled"
                : "Authenticator 2FA is disabled"}
            </Alert>

            <CardActionArea onClick={() => onSelect("authenticator")}>
              <Stack direction="row" spacing={2} alignItems="center">
                <LockOutline />
                <Box>
                  <Typography variant="subtitle1">Authenticator App</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Use Google Authenticator, Authy, or similar apps to generate
                    one-time codes.
                  </Typography>
                </Box>
              </Stack>
            </CardActionArea>
          </Stack>
        </CardContent>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Stack spacing={2}>
            <Alert
              severity={
                enabledMethods.includes("email") ? "success" : "warning"
              }
            >
              {enabledMethods.includes("email")
                ? "Email 2FA is enabled"
                : "Email 2FA is disabled"}
            </Alert>

            <CardActionArea onClick={() => onSelect("email")}>
              <Stack direction="row" spacing={2} alignItems="center">
                <EmailOutlined />
                <Box>
                  <Typography variant="subtitle1">Email</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Receive a one-time verification code via email.
                  </Typography>
                </Box>
              </Stack>
            </CardActionArea>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  </>
);
