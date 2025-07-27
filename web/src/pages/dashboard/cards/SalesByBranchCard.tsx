import { Box, Card, Stack, Typography } from "@mui/material";
import Chart from "react-apexcharts";
import { Audit, Branch } from "../../../types";
import { formatCurrencyShort } from "../../../utils";

interface SalesByBranchCardProps {
  audits: Audit[];
  branches: Branch[];
}

export const SalesByBranchCard = ({
  audits,
  branches,
}: SalesByBranchCardProps) => {
  const salesMap = new Map<string, { name: string; total: number }>();
  branches.forEach((branch) => {
    salesMap.set(branch.id.toString(), {
      name: branch.name,
      total: 0,
    });
  });

  audits.forEach((audit) => {
    const branchId = audit.branch_id.toString();
    if (!branchId || !salesMap.has(branchId)) return;

    const entry = salesMap.get(branchId)!;
    entry.total += isNaN(audit.sales) ? 0 : audit.sales;
  });

  const branchNames = Array.from(salesMap.values()).map((b) => b.name);
  const salesTotals = Array.from(salesMap.values()).map((b) => b.total);

  // Auto-compute maxValue for y-axis
  const step = 1000;
  const rawMax = Math.max(...salesTotals);
  const maxValue = Math.ceil(rawMax / step) * step;
  const tickAmount = maxValue > 0 ? maxValue / step : 1;

  const options: ApexCharts.ApexOptions = {
    chart: {
      type: "bar",
      toolbar: { show: false },
    },
    xaxis: {
      categories: branchNames,
      labels: {
        formatter: (value) =>
          typeof value === "number" ? formatCurrencyShort(value) : value,
        style: { fontWeight: 500 },
      },
    },
    yaxis: {
      min: 0,
      max: maxValue,
      tickAmount,
      labels: {
        style: { fontWeight: 500 },
      },
    },
    tooltip: {
      x: { show: true },
      y: {
        formatter: (val) =>
          val.toLocaleString("en-US", {
            style: "currency",
            currency: "PHP",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
      },
    },
    grid: { strokeDashArray: 5 },
    dataLabels: { enabled: false },
    plotOptions: {
      bar: {
        horizontal: true,
        borderRadius: 4,
        barHeight: "70%",
      },
    },
    colors: ["#43a047"],
  };

  return (
    <Card
      sx={{
        p: 3,
        borderRadius: 4,
        overflowX: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <Stack spacing={2} direction="column" sx={{ width: "100%" }}>
        <Typography variant="body2" color="text.secondary">
          Sales by Branch
        </Typography>
        {branchNames.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            No branches available
          </Typography>
        ) : (
          <Box overflow={{ x: "scroll" }}>
            <Chart
              options={options}
              series={[{ name: "Sales", data: salesTotals }]}
              type="bar"
              height={branchNames.length * 45 + 60}
            />
          </Box>
        )}
      </Stack>
    </Card>
  );
};
