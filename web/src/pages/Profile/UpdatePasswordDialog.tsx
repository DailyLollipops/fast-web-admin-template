import {
  useNotify,
  useDataProvider,
  TextInput,
  required,
  Form,
} from "react-admin";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { FieldValues } from "react-hook-form";

interface UpdatePasswordDialogProps {
  open: boolean;
  onClose: () => void;
}

export const UpdatePasswordDialog = ({
  open,
  onClose,
}: UpdatePasswordDialogProps) => {
  const notify = useNotify();
  const dataProvider = useDataProvider();

  const handleSubmit = async (data: FieldValues) => {
    if (data.newPassword !== data.confirmPassword) {
      notify("New passwords do not match", { type: "warning" });
      return;
    }

    try {
      await dataProvider.fetchJson("/auth/update_password", {
        method: "POST",
        body: JSON.stringify({
          current_password: data.current_password,
          new_password: data.new_password,
          confirm_password: data.confirm_password,
        }),
        headers: { "Content-Type": "application/json" },
      });
      notify("Password updated successfully!", { type: "success" });
      onClose();
    } catch (error) {
      console.error("Error updating password:", error);
      notify("Failed to update password. Please try again.", { type: "error" });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Update Password</DialogTitle>
      <Form onSubmit={handleSubmit}>
        <DialogContent>
          <TextInput
            source="current_password"
            label="Current Password"
            type="password"
            fullWidth
            validate={required()}
          />
          <TextInput
            source="new_password"
            label="New Password"
            type="password"
            fullWidth
            validate={required()}
          />
          <TextInput
            source="confirm_password"
            label="Confirm Password"
            type="password"
            fullWidth
            validate={required()}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained">
            Update Password
          </Button>
        </DialogActions>
      </Form>
    </Dialog>
  );
};
