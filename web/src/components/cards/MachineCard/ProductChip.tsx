import { useState } from "react";
import {
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Button,
  Card,
  CardMedia,
  CardContent,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { useDataProvider, useNotify } from "react-admin";
import { stringToMuiColor } from "../../../utils";
import { Product } from "../../../types";
import { API_URL } from "../../../constants";

interface ProductChipProps {
  product: Product;
  machineId: string;
  onDeleted?: () => void;
}

export const ProductChip = ({
  product,
  machineId,
  onDeleted,
}: ProductChipProps) => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openDetailsDialog, setOpenDetailsDialog] = useState(false);

  const handleDelete = async () => {
    try {
      await dataProvider.deleteManyToManyReference(
        ["machines", "products"],
        [machineId, product.id],
      );
      notify("Product removed", { type: "info" });
      onDeleted?.();
    } catch (error) {
      notify(`Error: ${(error as Error).message}`, { type: "error" });
    } finally {
      setOpenDeleteDialog(false);
    }
  };

  return (
    <>
      <Chip
        key={product.id}
        label={product.name}
        size="small"
        onClick={() => setOpenDetailsDialog(true)}
        onDelete={onDeleted ? () => setOpenDeleteDialog(true) : undefined}
        deleteIcon={onDeleted ? <DeleteIcon /> : undefined}
        color={stringToMuiColor(product.name)}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
      >
        <DialogTitle>Remove Product</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to remove <strong>{product.name}</strong> from
            this machine? Doing so would remove related sales and audits.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error">
            Remove
          </Button>
        </DialogActions>
      </Dialog>

      {/* Product Details Dialog */}
      <Dialog
        open={openDetailsDialog}
        onClose={() => setOpenDetailsDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Product Details</DialogTitle>
        <DialogContent>
          <Card>
            <CardMedia
              component="img"
              height="200"
              image={`${API_URL}/${product.image}`}
              alt={product.name}
            />
            <CardContent>
              <Typography variant="h6">{product.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {product.description || "No description provided."}
              </Typography>
            </CardContent>
          </Card>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDetailsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
