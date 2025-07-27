import Chart from "react-apexcharts";
import { Card, Stack, Typography } from "@mui/material";
import { Audit, Product } from "../../../types";
import { toCurrencyString } from "../../../utils";

interface SalesByProductCardProps {
  audits: Audit[];
  productNames?: Product[];
}

export const SalesByProductCard = ({
  audits,
  productNames = [],
}: SalesByProductCardProps) => {
  const productNameMap = productNames.reduce<Record<string, string>>(
    (acc, product) => {
      acc[product.id.toString()] = product.name;
      return acc;
    },
    {},
  );

  const salesByProduct = audits.reduce<Record<string, number>>((acc, audit) => {
    const id = String(audit.product_id ?? "unknown");
    acc[id] = (acc[id] || 0) + (isNaN(audit.sales) ? 0 : audit.sales);
    return acc;
  }, {});

  const labels = Object.keys(salesByProduct).map(
    (id) => productNameMap[id] || `Product ${id}`,
  );
  const series = Object.values(salesByProduct);

  const options: ApexCharts.ApexOptions = {
    labels,
    legend: {
      position: "bottom",
    },
    chart: {
      type: "donut",
    },
    dataLabels: {
      enabled: true,
      formatter: (val: number) => `${val.toFixed(2)}%`,
    },
    tooltip: {
      y: {
        formatter: (value: number) =>
          value.toLocaleString("en-US", {
            style: "currency",
            currency: "PHP",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
      },
    },
    plotOptions: {
      pie: {
        donut: {
          labels: {
            show: true,
            value: {
              show: true,
              formatter: (value) => toCurrencyString(value),
            },
            total: {
              show: true,
              label: "Total",
              formatter: () =>
                series
                  .reduce((sum, val) => sum + val, 0)
                  .toLocaleString("en-US", {
                    style: "currency",
                    currency: "PHP",
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }),
            },
          },
        },
      },
    },
  };

  return (
    <Card
      sx={{
        p: 3,
        borderRadius: 4,
        minHeight: 384,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Stack spacing={2} direction="column">
        <Typography variant="body2" color="text.secondary" textAlign="center">
          Total Sales by Product
        </Typography>
        {series.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            No sales data available
          </Typography>
        ) : (
          <Chart
            options={options}
            series={series}
            type="donut"
            height={300}
            width={240}
          />
        )}
      </Stack>
    </Card>
  );
};
