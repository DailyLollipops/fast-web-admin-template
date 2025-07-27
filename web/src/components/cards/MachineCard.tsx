import { useState } from "react";
import {
  EditButton,
  DeleteWithConfirmButton,
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
  Skeleton,
  Stack,
} from "@mui/material";
import OilBarrelIcon from "@mui/icons-material/OilBarrel";
import AddIcon from "@mui/icons-material/Add";
import GasStation from "../../assets/GasStation.png";
import { Product, Machine } from "../../types";
import { AddProductDialog } from "./MachineCard/AddProductDialog";
import { RefillGasDialog } from "./MachineCard/RefillGasDialog";
import { ProductChip } from "./MachineCard/ProductChip";
import { stringToMuiColor } from "../../utils";
import { useGetManyToManyReferenceList } from "../../hooks";

interface MachineCardProps {
  machine: Machine;
  actions: boolean;
  showReserves: boolean;
  showSales: boolean;
}

export const MachineCard = (props: MachineCardProps) => {
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down("sm"));
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [refillDialogOpen, setRefillDialogOpen] = useState(false);
  const [version, setVersion] = useState(0);

  console.debug(version);

  const { data: products, loading } = useGetManyToManyReferenceList<Product>(
    ["machines", "products"],
    [props.machine.id.toString()],
    version,
  );

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
          <Typography variant="h6">{props.machine.name}</Typography>
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
                    machineId={props.machine.id.toString()}
                    onDeleted={
                      props.actions ? () => setVersion((v) => v + 1) : undefined
                    }
                  />
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.disabled">
                No products
              </Typography>
            )}
          </Box>
          {props.showReserves && (
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
          )}
          {props.showSales && (
            <Box mt={2} minHeight={{ xs: 65, sm: 165, md: 135 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Last Sales:
              </Typography>

              {loading ? (
                <Skeleton variant="rectangular" height={100} />
              ) : products.length > 0 ? (
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {products.map((p) => (
                    <Grid size={{ xs: 12, md: 6 }} key={p.id}>
                      <Stack spacing={0.5}>
                        <Typography variant="body2" fontWeight={500}>
                          {p.name}
                        </Typography>
                        {p.last_price != null && p.last_sale != null ? (
                          <Typography variant="body2" color="text.secondary">
                            ₱{p.last_sale} @ ₱{p.last_price}/L
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.disabled">
                            No sales yet
                          </Typography>
                        )}
                      </Stack>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.disabled">
                  No products available
                </Typography>
              )}
            </Box>
          )}
        </CardContent>
        {props.actions && (
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
            <EditButton record={props.machine} />
            <DeleteWithConfirmButton record={props.machine} redirect={false} />
          </CardActions>
        )}
      </Card>

      <AddProductDialog
        machineId={props.machine.id.toString()}
        open={addDialogOpen}
        onClose={handleDialogClose}
      />
      <RefillGasDialog
        machineId={props.machine.id.toString()}
        products={products}
        open={refillDialogOpen}
        onClose={handleDialogClose}
      />
    </>
  );
};
