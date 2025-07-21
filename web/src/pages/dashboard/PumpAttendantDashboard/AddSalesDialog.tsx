import { useEffect, useState } from "react";
import {
  SaveButton,
  Toolbar,
  useDataProvider,
  useNotify,
  useRefresh,
  useGetManyReference,
  useGetIdentity,
} from "react-admin";
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Grid,
  TextField,
  Typography,
} from "@mui/material";
import { FieldValues, FormProvider, useForm } from "react-hook-form";
import { Machine, Product } from "../../../types";

interface AddSalesProps {
  onClose: () => void;
  branchId: number;
  machines: Machine[];
  productMap: Record<number, Product[]>;
}

export const AddSalesForm = ({
  onClose,
  branchId,
  machines,
  productMap,
}: AddSalesProps) => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  const methods = useForm();
  const { register, handleSubmit } = methods;

  const [submitting, setSubmitting] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const onSubmit = async (data: FieldValues) => {
    setSubmitting(true);
    try {
      const sales = [];

      for (const machine of machines) {
        const products = productMap[machine.id] || [];
        for (const product of products) {
          const key = `${machine.id}_${product.id}`;
          const price = parseFloat(data[`price_${key}`]);
          const dispensed = parseInt(data[`dispensed_${key}`]);
          const expenses = parseInt(data[`expenses_${key}`]);

          if (!isNaN(price) || !isNaN(dispensed) || !isNaN(expenses)) {
            sales.push({
              machine_id: machine.id,
              product_id: product.id,
              price,
              dispensed,
              expenses,
            });
          }
        }
      }

      console.log(sales);
      await dataProvider.createManyToManyReference(
        ["branches", "sales"],
        [branchId.toString()],
        {
          data: { sales: sales },
        },
      );
      notify("Sales saved successfully", { type: "success" });
      refresh();
      onClose();
    } catch (error: unknown) {
      if (error instanceof Error) {
        notify(`Error: ${error.message}`, { type: "error" });
      }
    } finally {
      setSubmitting(false);
      setConfirmOpen(false);
    }
  };

  const handleOpenConfirm = () => {
    setConfirmOpen(true);
  };

  const handleConfirm = () => {
    handleSubmit(onSubmit)();
  };

  const handleCancel = () => {
    setConfirmOpen(false);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleOpenConfirm}>
        {machines.map((machine) => (
          <Box key={machine.id} mb={3}>
            <Typography variant="h6">{machine.name}</Typography>
            <Divider sx={{ my: 1 }} />
            {productMap[machine.id]?.map((product) => {
              const key = `${machine.id}_${product.id}`;
              return (
                <Box key={product.id} mb={2}>
                  <Typography variant="subtitle1">{product.name}</Typography>
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 6, md: 4 }}>
                      <TextField
                        label="Price"
                        type="number"
                        fullWidth
                        slotProps={{
                          htmlInput: {
                            step: 0.01,
                          },
                        }}
                        {...register(`price_${key}`)}
                      />
                    </Grid>
                    <Grid size={{ xs: 6, md: 4 }}>
                      <TextField
                        label="Dispensed"
                        type="number"
                        fullWidth
                        slotProps={{
                          htmlInput: {
                            step: 0.01,
                          },
                        }}
                        {...register(`dispensed_${key}`)}
                      />
                    </Grid>
                    <Grid size={{ xs: 6, md: 4 }}>
                      <TextField
                        label="Expenses"
                        type="number"
                        fullWidth
                        {...register(`expenses_${key}`)}
                      />
                    </Grid>
                  </Grid>
                </Box>
              );
            })}
          </Box>
        ))}
        <Toolbar>
          <SaveButton
            type="button"
            disabled={submitting}
            onClick={handleOpenConfirm}
          />
        </Toolbar>

        {/* Confirmation Dialog */}
        <Dialog open={confirmOpen} onClose={handleCancel}>
          <DialogTitle>Confirm Save</DialogTitle>
          <DialogContent>
            Are you sure you want to save this sales record?
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCancel} color="inherit">
              Cancel
            </Button>
            <Button onClick={handleConfirm} color="primary" autoFocus>
              Confirm
            </Button>
          </DialogActions>
        </Dialog>
      </form>
    </FormProvider>
  );
};

export const AddSalesDialog = ({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) => {
  const { identity } = useGetIdentity();
  const { data: machines, isLoading: machinesLoading } =
    useGetManyReference<Machine>("machines", {
      target: "branch_id",
      id: identity?.branch_id,
      sort: { field: "created_at", order: "DESC" },
    });

  const [productMap, setProductMap] = useState<Record<number, Product[]>>({});
  const [loadingProducts, setLoadingProducts] = useState(true);

  const dataProvider = useDataProvider();

  useEffect(() => {
    const fetchProducts = async () => {
      if (!machines) return;
      const map: Record<number, Product[]> = {};

      for (const machine of machines) {
        const { data } = await dataProvider.getManyToManyReferenceList(
          ["machines", "products"],
          [machine.id.toString()],
        );
        map[machine.id] = data;
      }

      setProductMap(map);
      setLoadingProducts(false);
    };

    fetchProducts();
  }, [machines, dataProvider]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Add Sale</DialogTitle>
      <DialogContent>
        {machinesLoading || loadingProducts ? (
          <Box p={2} display="flex" justifyContent="center">
            <CircularProgress />
          </Box>
        ) : (
          <AddSalesForm
            onClose={onClose}
            branchId={identity?.branch_id ?? ""}
            machines={machines || []}
            productMap={productMap}
          />
        )}
      </DialogContent>
    </Dialog>
  );
};
