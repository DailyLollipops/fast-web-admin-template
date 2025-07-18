import {
  Form,
  ReferenceInput,
  SelectInput,
  useDataProvider,
  useNotify,
  useRefresh,
  Toolbar,
  SaveButton,
} from "react-admin";
import { FieldValues } from "react-hook-form";
import { Dialog, DialogTitle, DialogContent } from "@mui/material";

interface AddProductFormProps {
  machineId: string;
  onClose: () => void;
}

export const AddProductForm = ({ machineId, onClose }: AddProductFormProps) => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  const handleSubmit = async (data: FieldValues) => {
    try {
      await dataProvider.createManyToManyReference(
        ["machines", "products"],
        [machineId],
        {
          data: {
            product_id: data.product_id,
          },
        },
      );
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
      <ReferenceInput source="product_id" reference="products">
        <SelectInput optionText="name" />
      </ReferenceInput>
      <Toolbar>
        <SaveButton />
      </Toolbar>
    </Form>
  );
};

export const AddProductDialog = ({
  machineId,
  open,
  onClose,
}: {
  machineId: string;
  open: boolean;
  onClose: () => void;
}) => {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Add Product to Machine</DialogTitle>
      <DialogContent>
        <AddProductForm machineId={machineId} onClose={onClose} />
      </DialogContent>
    </Dialog>
  );
};
