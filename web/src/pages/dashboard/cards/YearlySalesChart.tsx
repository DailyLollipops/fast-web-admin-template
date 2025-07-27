import Chart from "react-apexcharts";
import { Card, Stack, Typography } from "@mui/material";
import { Audit } from "../../../types";
import { formatCurrencyShort } from "../../../utils";

interface YearlySalesBarChartProps {
  audits: Audit[];
}

export const YearlySalesBarChart = ({ audits }: YearlySalesBarChartProps) => {
  const currentYear = new Date().getFullYear();
  const salesByMonth = Array(12).fill(0);

  audits.forEach((audit) => {
    const date = new Date(audit.created_at);
    if (date.getFullYear() === currentYear) {
      const monthIndex = date.getMonth();
      salesByMonth[monthIndex] += isNaN(audit.sales) ? 0 : audit.sales;
    }
  });

  const options: ApexCharts.ApexOptions = {
    chart: {
      type: "bar",
      toolbar: { show: false },
      animations: { enabled: false },
    },
    xaxis: {
      categories: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
    },
    yaxis: {
      labels: {
        formatter: formatCurrencyShort,
        style: { fontWeight: 500 },
      },
    },
    tooltip: {
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
    grid: {
      strokeDashArray: 5,
      yaxis: {
        lines: {
          show: true,
        },
      },
    },
    dataLabels: {
      enabled: false,
    },
    plotOptions: {
      bar: {
        borderRadius: 6,
        columnWidth: "50%",
      },
    },
    colors: ["#1976d2"],
  };

  return (
    <Card sx={{ p: 3, borderRadius: 4 }}>
      <Stack spacing={2} direction="column">
        <Typography variant="body2" color="text.secondary">
          Yearly Sales
        </Typography>
      </Stack>
      {salesByMonth.length === 0 ? (
        <Typography variant="body1" color="text.secondary">
          No sales data available
        </Typography>
      ) : (
        <Chart
          options={options}
          series={[{ name: "Sales", data: salesByMonth }]}
          type="bar"
          height={300}
        />
      )}
    </Card>
  );
};
