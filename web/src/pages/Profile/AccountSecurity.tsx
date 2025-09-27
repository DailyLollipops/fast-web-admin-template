import { useState, useEffect } from "react";
import {
  Box,
  Button,
  Card,
  Collapse,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import { useGetIdentity, useDataProvider } from "react-admin";
import LockResetIcon from "@mui/icons-material/LockReset";
import EmailIcon from "@mui/icons-material/Email";
import SecurityIcon from "@mui/icons-material/Security";
import LogoutIcon from "@mui/icons-material/Logout";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { UpdatePasswordDialog } from "./UpdatePasswordDialog";

export const AccountSecurity = () => {
  const dataProvider = useDataProvider();
  const { identity } = useGetIdentity();
  const [showUpdatePasswordDialog, setOpenUpdatePasswordDialog] =
    useState(false);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    if (identity?.api != null || identity?.api != undefined) {
      setApiKey(identity.api);
      setShowApiKey(true);
    }
  }, [identity?.api]);

  const maskKey = (key: string) =>
    key.length > 12 ? `${key.slice(0, 3)}*********${key.slice(-3)}` : "******";

  const handleNotImplemented = () => {
    alert("This feature is not implemented yet.");
  };

  const handleGenerateApiKey = async () => {
    const { json: data } = await dataProvider.fetchJson(
      "/auth/generate_api_key",
      {
        method: "POST",
      },
    );
    console.log(data);
    setApiKey(data.api);
    setShowApiKey(true);
  };

  const handleCopy = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      alert("API Key copied to clipboard!");
    }
  };

  return (
    <>
      <UpdatePasswordDialog
        open={showUpdatePasswordDialog}
        onClose={() => setOpenUpdatePasswordDialog(false)}
      />

      <Card
        sx={{
          p: 2,
          width: "100%",
          mt: 3,
        }}
      >
        <List sx={{ p: 0 }}>
          <ListItem
            secondaryAction={
              <Button
                variant="outlined"
                size="small"
                onClick={() => setOpenUpdatePasswordDialog(true)}
              >
                Update
              </Button>
            }
          >
            <ListItemIcon>
              <LockResetIcon />
            </ListItemIcon>
            <ListItemText
              primary="Update Password"
              secondary="Update your account password."
            />
          </ListItem>

          <ListItem
            secondaryAction={
              <Button
                variant="outlined"
                size="small"
                onClick={handleNotImplemented}
              >
                Change
              </Button>
            }
          >
            <ListItemIcon>
              <EmailIcon />
            </ListItemIcon>
            <ListItemText
              primary="Reset Email"
              secondary="Update your recovery or login email address."
            />
          </ListItem>

          <ListItem
            secondaryAction={
              <Button
                variant="outlined"
                size="small"
                onClick={handleNotImplemented}
              >
                Enable
              </Button>
            }
          >
            <ListItemIcon>
              <SecurityIcon />
            </ListItemIcon>
            <ListItemText
              primary="Enable Two-Factor Auth"
              secondary="Add an extra layer of security to your account."
            />
          </ListItem>

          <ListItem
            secondaryAction={
              <Button
                variant="outlined"
                size="small"
                onClick={handleGenerateApiKey}
              >
                {apiKey ? "Regenerate" : "Generate"}
              </Button>
            }
          >
            <ListItemIcon>
              <VpnKeyIcon />
            </ListItemIcon>
            <ListItemText
              primary="API Key"
              secondary="Generate and manage API keys for external integrations."
            />
          </ListItem>
          <Collapse in={showApiKey} timeout="auto" unmountOnExit>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              px={6}
              py={1}
              sx={{ bgcolor: "grey.100", borderRadius: 1, mt: 1 }}
            >
              <Typography variant="body2" sx={{ wordBreak: "break-all" }}>
                {maskKey(apiKey ?? "")}
              </Typography>
              <IconButton onClick={handleCopy} size="small">
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Box>
          </Collapse>

          <ListItem
            secondaryAction={
              <Button variant="outlined" color="error" size="small">
                Logout
              </Button>
            }
          >
            <ListItemIcon>
              <LogoutIcon color="error" />
            </ListItemIcon>
            <ListItemText
              primary="Logout of All Devices"
              secondary="Sign out from every active session across devices."
            />
          </ListItem>
        </List>
      </Card>
    </>
  );
};
