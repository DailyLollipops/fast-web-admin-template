import { useEffect } from "react";
import { Title, useCheckAuth, useLogout } from "react-admin";
import { Card, CardContent } from "@mui/material";

export const Dashboard = () => {
  const checkAuth = useCheckAuth();
  const logout = useLogout();

  useEffect(() => {
    checkAuth().catch(() => {
      console.error("User is not authenticated");
      logout();
    });
  }, [checkAuth, logout]);

  return (
    <Card>
      <Title title="Dashboard" />
      <CardContent>Welcome to Fast Web Admin</CardContent>
    </Card>
  );
};
