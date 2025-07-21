import { useState } from "react";
import {
  Title,
  useGetList,
  useGetManyReference,
  useGetIdentity,
} from "react-admin";
import {
  Box,
  Button,
  Card,
  Grid,
  CardContent,
  Typography,
} from "@mui/material";
import { PointOfSale, Notifications } from "@mui/icons-material";
// import { ProductCarousel } from "./PumpAttendantDashboard/ProductCarousel";
import { AddSalesDialog } from "./PumpAttendantDashboard/AddSalesDialog";
import { WelcomeCard } from "./PumpAttendantDashboard/WelcomeCard";
import { BranchInfoCard } from "./PumpAttendantDashboard/BranchInfoCard";
import { TotalSalesCard } from "./PumpAttendantDashboard/TotalSalesCard";
import { TotalDispensedCard } from "./PumpAttendantDashboard/TotalDispensedCard";
import { TotalExpensesCard } from "./PumpAttendantDashboard/TotalExpensesCard";
import { SalesByProductCard } from "./PumpAttendantDashboard/SalesByProductCard";
import { YearlySalesBarChart } from "./PumpAttendantDashboard/YearlySalesChart";
import { MachineCard } from "../../components";
import { Audit, Product } from "../../types";

export const PumpAttendantDashboard = () => {
  const [open, setOpen] = useState(false);
  const { identity } = useGetIdentity();

  const { data: audits, isLoading: auditsLoading } = useGetList("audits", {
    sort: { field: "created_at", order: "DESC" },
    filter: { category: "sales" },
  });

  const { data: products, isLoading: productsLoading } = useGetList(
    "products",
    {
      sort: { field: "id", order: "DESC" },
      filter: { category: "sales" },
    },
  );

  const { data: machines, isLoading: machinesLoading } = useGetManyReference(
    "machines",
    {
      target: "branch_id",
      id: identity?.branch_id,
      sort: { field: "id", order: "ASC" },
      filter: undefined,
    },
  );

  if (auditsLoading || productsLoading || machinesLoading) return null;

  return (
    <>
      <AddSalesDialog open={open} onClose={() => setOpen(false)} />

      <Card>
        <Title title="Dashboard" />
        <CardContent>
          <Box display="flex" flexDirection="column" gap={2}>
            <Box
              alignSelf="flex-end"
              display="flex"
              flexDirection={{ xs: "column", sm: "row" }}
              gap={2}
            >
              <Button
                variant="outlined"
                startIcon={<Notifications />}
                color="error"
              >
                Notify Inventory
              </Button>
              <Button
                variant="outlined"
                startIcon={<PointOfSale />}
                onClick={() => setOpen(true)}
              >
                Add Sales
              </Button>
            </Box>
          </Box>
          <Grid container spacing={2} sx={{ mt: 3 }}>
            <Grid size={{ xs: 12, lg: 7 }}>
              <WelcomeCard />
            </Grid>
            <Grid size={{ xs: 12, lg: 5 }}>
              <BranchInfoCard
                name="Main Branch"
                location="Makati City, Philippines"
                machineCount={5}
              />
            </Grid>
          </Grid>
          <Typography variant="h6" my={3} sx={{ fontWeight: "bold" }}>
            Sales Overview
          </Typography>
          <Grid container spacing={2} mb={3}>
            <Grid size={{ xs: 12, md: 6, lg: 4 }}>
              <TotalSalesCard audits={audits as Audit[]} />
            </Grid>
            <Grid size={{ xs: 12, md: 6, lg: 4 }}>
              <TotalDispensedCard audits={audits as Audit[]} />
            </Grid>
            <Grid size={{ xs: 12, md: 6, lg: 4 }}>
              <TotalExpensesCard audits={audits as Audit[]} />
            </Grid>
          </Grid>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6, lg: 4 }}>
              <SalesByProductCard
                audits={audits as Audit[]}
                productNames={products as Product[]}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6, lg: 8 }}>
              <YearlySalesBarChart audits={audits as Audit[]} />
            </Grid>
          </Grid>
          <Typography variant="h6" my={3} sx={{ fontWeight: "bold" }}>
            Machines Overview
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {machines!.map((machine) => (
              <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }} key={machine.id}>
                <MachineCard machine={machine} actions={false} />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </>
  );
};
