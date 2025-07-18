import {
  Form,
  TextInput,
  SaveButton,
  Toolbar,
  useRecordContext,
  useDataProvider,
  useNotify,
  useRefresh,
} from "react-admin";
import { FieldValues } from "react-hook-form";
import { Dialog, DialogTitle, DialogContent } from "@mui/material";

interface AddMachineProps {
  branchId: string;
  onClose: () => void;
}

export const AddMachineForm = ({ branchId, onClose }: AddMachineProps) => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  const handleSubmit = async (data: FieldValues) => {
    try {
      await dataProvider.create("machines", {
        data: {
          ...data,
          branch_id: branchId,
        },
      });
      notify("Product added", { type: "success" });
      refresh();
      onClose();
    } catch (error: unknown) {
      if (error instanceof Error) {
        notify(`Error: ${error.message}`, { type: "error" });
      }
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      <TextInput source="name" fullWidth />
      <Toolbar>
        <SaveButton />
      </Toolbar>
    </Form>
  );
};

export const AddMachineDialog = ({
  branchId,
  open,
  onClose,
}: {
  branchId: string;
  open: boolean;
  onClose: () => void;
}) => {
  const branch = useRecordContext();
  if (!branch) return null;

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Add Machine</DialogTitle>
      <DialogContent>
        <AddMachineForm branchId={branchId} onClose={onClose} />
      </DialogContent>
    </Dialog>
  );
};
