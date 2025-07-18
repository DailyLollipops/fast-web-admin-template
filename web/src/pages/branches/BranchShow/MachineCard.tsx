import { useEffect, useState } from "react";
import {
  useDataProvider,
  useNotify,
  EditButton,
  DeleteWithConfirmButton,
  RaRecord,
  LinearProgress,
} from "react-admin";
import {
  Box,
  Button,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  CircularProgress,
  Typography,
  useTheme,
  useMediaQuery,
  Tooltip,
  Grid,
} from "@mui/material";
import OilBarrelIcon from "@mui/icons-material/OilBarrel";
import AddIcon from "@mui/icons-material/Add";
import GasStation from "../../../assets/GasStation.png";
import { Product } from "../../../types";
import { AddProductDialog } from "./AddProductDialog";
import { RefillGasDialog } from "./RefillGasDialog";
import { ProductChip } from "./ProductChip";
import { stringToMuiColor } from "../../../utils";

interface MachineCardProps {
  machine: RaRecord;
}

export const MachineCard = ({ machine }: MachineCardProps) => {
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down("sm"));
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [refillDialogOpen, setRefillDialogOpen] = useState(false);

  const dataProvider = useDataProvider();
  const notify = useNotify();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    setLoading(true);
    dataProvider
      .getManyToManyReferenceList(
        ["machines", "products"],
        [machine.id.toString()],
      )
      .then(({ data }: { data: Product[] }) => {
        setProducts(data);
      })
      .catch((error: Error) => {
        notify(`Failed to load products: ${error.message}`, { type: "error" });
      })
      .finally(() => setLoading(false));
  }, [dataProvider, machine.id, notify, version]);

  const handleDialogClose = () => {
    setAddDialogOpen(false);
    setRefillDialogOpen(false);
    setVersion((v) => v + 1);
  };

  return (
    <>
      <Card>
        <CardMedia
          sx={{ height: 220 }}
          image={GasStation}
          title="Gas Station"
        />
        <CardContent>
          <Typography variant="h6">{machine.name}</Typography>
          <Box mt={1} minHeight={{ xs: 55, sm: 70 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Products:
            </Typography>
            {loading ? (
              <CircularProgress size={16} />
            ) : products.length > 0 ? (
              <Box display="flex" flexWrap="wrap" gap={1}>
                {products.map((p) => (
                  <ProductChip
                    key={p.id}
                    product={p}
                    machineId={machine.id.toString()}
                    onDeleted={() => setVersion((v) => v + 1)}
                  />
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.disabled">
                No products
              </Typography>
            )}
          </Box>
          <Box mt={2} minHeight={{ xs: 65, sm: 165, md: 135 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Reserves:
            </Typography>
            {loading ? (
              <CircularProgress size={16} />
            ) : products.length > 0 ? (
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {products.map((p) => (
                  <Grid size={{ sm: 12, md: 6 }} key={p.id}>
                    <Typography variant="body2">{p.name}</Typography>
                    <Tooltip title={`${p.remaining || 0}% remaining`}>
                      <LinearProgress
                        variant="determinate"
                        value={p.remaining}
                        color={stringToMuiColor(p.name)}
                        sx={{
                          height: 8,
                          borderRadius: 5,
                          backgroundColor: "#eee",
                        }}
                      />
                    </Tooltip>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography variant="body2" color="text.disabled">
                No products
              </Typography>
            )}
          </Box>
        </CardContent>
        <CardActions sx={{ justifyContent: "flex-end", px: 2, pb: 2 }}>
          <Button
            startIcon={<OilBarrelIcon />}
            color="success"
            onClick={() => setRefillDialogOpen(true)}
          >
            {!isSm ? "Refill" : ""}
          </Button>
          <Button
            startIcon={<AddIcon />}
            color="success"
            onClick={() => setAddDialogOpen(true)}
          >
            {!isSm ? "Add" : ""}
          </Button>
          <EditButton record={machine} />
          <DeleteWithConfirmButton record={machine} redirect={false} />
        </CardActions>
      </Card>

      <AddProductDialog
        machineId={machine.id.toString()}
        open={addDialogOpen}
        onClose={handleDialogClose}
      />
      <RefillGasDialog
        machineId={machine.id.toString()}
        products={products}
        open={refillDialogOpen}
        onClose={handleDialogClose}
      />
    </>
  );
};
