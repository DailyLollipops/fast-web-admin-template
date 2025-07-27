import { useListContext, useGetIdentity } from "react-admin";
import { Grid } from "@mui/material";
import { MachineCard } from "../../../components";

export const MachineCards = () => {
  const { identity } = useGetIdentity();
  const { data, isLoading } = useListContext();
  if (isLoading) return <>Loading...</>;
  if (!data || data.length === 0) return <>No machines found.</>;

  const showReservesRoles = ["admin", "admin_inventory", "owner"];
  const showSalesRoles = ["admin", "admin_sales", "owner"];

  return (
    <Grid container spacing={2} sx={{ mt: 1 }}>
      {data.map((machine) => (
        <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }} key={machine.id}>
          <MachineCard
            machine={machine}
            actions={true}
            showReserves={showReservesRoles.includes(identity?.role ?? "")}
            showSales={showSalesRoles.includes(identity?.role ?? "")}
          />
        </Grid>
      ))}
    </Grid>
  );
};
