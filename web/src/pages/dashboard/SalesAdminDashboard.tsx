import { Title, useGetList } from "react-admin";
import { Card, Grid, CardContent, Typography } from "@mui/material";
import { WelcomeCard } from "./cards/WelcomeCard";
import { TotalSalesCard } from "./cards/TotalSalesCard";
import { TotalDispensedCard } from "./cards/TotalDispensedCard";
import { TotalExpensesCard } from "./cards/TotalExpensesCard";
import { SalesByProductCard } from "./cards/SalesByProductCard";
import { YearlySalesBarChart } from "./cards/YearlySalesChart";
import { SalesByBranchCard } from "./cards/SalesByBranchCard";
import { MachineCard } from "../../components";
import { Audit, Branch, Product } from "../../types";

export const SalesAdminDashboard = () => {
  const { data: audits, isLoading: auditsLoading } = useGetList("audits", {
    sort: { field: "created_at", order: "DESC" },
    filter: { category: "sales" },
  });

  const { data: branches, isLoading: branchesLoading } = useGetList(
    "branches",
    {
      sort: { field: "id", order: "DESC" },
    },
  );

  const { data: products, isLoading: productsLoading } = useGetList(
    "products",
    {
      sort: { field: "id", order: "DESC" },
    },
  );

  const { data: machines, isLoading: machinesLoading } = useGetList(
    "machines",
    {
      sort: { field: "id", order: "ASC" },
    },
  );

  if (auditsLoading || productsLoading || branchesLoading || machinesLoading)
    return null;

  return (
    <>
      <Card>
        <Title title="Dashboard" />
        <CardContent>
          <Grid container spacing={2} sx={{ mt: 3 }}>
            <Grid size={{ xs: 12, lg: 7 }}>
              <WelcomeCard />
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
          <Grid container spacing={2} mb={3}>
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
          <Grid container spacing={2}>
            <Grid size={12}>
              <SalesByBranchCard
                audits={audits as Audit[]}
                branches={branches as Branch[]}
              />
            </Grid>
          </Grid>
          <Typography variant="h6" my={3} sx={{ fontWeight: "bold" }}>
            Machines Overview
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {machines!.map((machine) => (
              <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }} key={machine.id}>
                <MachineCard
                  machine={machine}
                  actions={false}
                  showReserves={false}
                  showSales={true}
                />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </>
  );
};
