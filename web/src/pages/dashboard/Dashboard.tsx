import { Title, useGetIdentity } from "react-admin";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import { PumpAttendantDashboard } from "./PumpAttendantDashboard";

export const Dashboard = () => {
  const { data: identity, isLoading } = useGetIdentity();

  if (isLoading || !identity) return null;

  if (identity.role == "pump_attendant") {
    return <PumpAttendantDashboard />;
  }

  return (
    <Card>
      <Title title="Dashboard" />
      <CardContent>Lorem ipsum sic dolor amet...</CardContent>
    </Card>
  );
};
