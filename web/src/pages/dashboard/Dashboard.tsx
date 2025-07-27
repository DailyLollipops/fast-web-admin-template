import { Title, useGetIdentity } from "react-admin";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import { PumpAttendantDashboard } from "./PumpAttendantDashboard";
import { SalesAdminDashboard } from "./SalesAdminDashboard";

export const Dashboard = () => {
  const { data: identity, isLoading } = useGetIdentity();

  if (isLoading || !identity) return null;

  if (identity.role == "pump_attendant") {
    return <PumpAttendantDashboard />;
  }

  if (identity.role == "admin_sales") {
    return <SalesAdminDashboard />;
  }

  return (
    <Card>
      <Title title="Dashboard" />
      <CardContent>Lorem ipsum sic dolor amet...</CardContent>
    </Card>
  );
};
