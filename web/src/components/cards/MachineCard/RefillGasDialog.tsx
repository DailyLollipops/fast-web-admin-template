import {
  Form,
  NumberInput,
  SelectInput,
  required,
  useDataProvider,
  useNotify,
  useRefresh,
  Toolbar,
  SaveButton,
} from "react-admin";
import { FieldValues } from "react-hook-form";
import { Dialog, DialogTitle, DialogContent } from "@mui/material";
import { Product } from "../../../types";

interface RefillGasFormProps {
  machineId: string;
  products: Product[];
  onClose: () => void;
}

export const RefillGasForm = ({
  machineId,
  products,
  onClose,
}: RefillGasFormProps) => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  const choices = products.map((product) => ({
    id: product.id,
    name: product.name,
  }));

  const handleSubmit = async (data: FieldValues) => {
    try {
      await dataProvider.createManyToManyReference(
        ["machines", "products", "refill"],
        [machineId, data.product_id],
        {
          data: {
            refill_amount: data.refill_amount,
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
      <SelectInput
        source="product_id"
        choices={choices}
        validate={[required()]}
      />
      <NumberInput
        source="refill_amount"
        label="Refill amount (L)"
        validate={[required()]}
      />
      <Toolbar>
        <SaveButton />
      </Toolbar>
    </Form>
  );
};

export const RefillGasDialog = ({
  machineId,
  products,
  open,
  onClose,
}: {
  machineId: string;
  products: Product[];
  open: boolean;
  onClose: () => void;
}) => {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Refill Gas</DialogTitle>
      <DialogContent>
        <RefillGasForm
          machineId={machineId}
          products={products}
          onClose={onClose}
        />
      </DialogContent>
    </Dialog>
  );
};
