import Chart from "react-apexcharts";
import { TrendingUp, TrendingDown } from "@mui/icons-material";
import { Card, Stack, Typography, Box, SvgIcon } from "@mui/material";
import { Audit } from "../../../types";

interface TotalSalesCardProps {
  audits: Audit[];
}

export const TotalSalesCard = ({ audits }: TotalSalesCardProps) => {
  const totalSales = (
    audits?.reduce((total, a) => total + a.sales, 0) || 0
  ).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const percentChange = audits?.[1]?.sales
    ? ((audits[0].sales - audits[1].sales) / audits[1].sales) * 100
    : 0;
  const isUp = percentChange >= 0;

  const today = new Date();
  const past7Dates = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(today);
    date.setDate(today.getDate() - (6 - i));
    return date.toISOString().split("T")[0];
  });

  const salesMap = (audits ?? []).reduce(
    (acc, curr) => {
      const date = new Date(curr.created_at).toISOString().split("T")[0];
      acc[date] = (acc[date] || 0) + curr.sales;
      return acc;
    },
    {} as Record<string, number>,
  );

  const last7Days = past7Dates.map((date) => ({
    date,
    sales: salesMap[date] || 0,
  }));

  return (
    <Card sx={{ p: 3, borderRadius: 4 }}>
      <Stack spacing={2} direction="column">
        <Typography variant="body2" color="text.secondary">
          Total Sales
        </Typography>

        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h4" fontWeight="bold">
            ₱ {totalSales}
          </Typography>

          <Box sx={{ width: 100, height: 60 }}>
            <Chart
              options={{
                chart: {
                  type: "bar",
                  sparkline: { enabled: true },
                },
                colors: ["#4caf50"],
                xaxis: {
                  categories: last7Days.map((d) =>
                    new Date(d.date).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    }),
                  ),
                },
                tooltip: {
                  enabled: true,
                  y: {
                    formatter: (value: number) =>
                      `₱ ${value.toLocaleString("en-US", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}`,
                    title: {
                      formatter: (
                        _: string,
                        { dataPointIndex }: { dataPointIndex: number },
                      ) => {
                        const date = new Date(last7Days[dataPointIndex].date);
                        return date.toLocaleDateString("en-US", {
                          weekday: "short",
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        });
                      },
                    },
                  },
                },
              }}
              series={[
                {
                  name: "Sales",
                  data: last7Days.map((d) => d.sales),
                },
              ]}
              type="bar"
              height={60}
              width={100}
            />
          </Box>
        </Box>

        <Box display="flex" alignItems="center">
          <SvgIcon
            sx={{
              color: isUp ? "success.main" : "error.main",
              fontSize: 18,
              mr: 0.5,
            }}
          >
            {isUp ? <TrendingUp /> : <TrendingDown />}
          </SvgIcon>
          <Typography
            variant="body2"
            sx={{
              color: isUp ? "success.main" : "error.main",
              fontWeight: 500,
            }}
          >
            {`${isUp ? "+" : ""}${percentChange.toFixed(1)}%`}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
            since last entry
          </Typography>
        </Box>
      </Stack>
    </Card>
  );
};
