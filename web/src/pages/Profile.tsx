import { Title, useGetIdentity } from "react-admin";
import { Card, CardContent, Grid, Typography } from "@mui/material";
import { ProfileCard } from "@/components";
import { AccountSecurity } from "./Profile/AccountSecurity";

export const Profile = () => {
  const { identity } = useGetIdentity();
  console.log("User Identity:", identity);

  return (
    <Card sx={{ minHeight: "calc(100vh - 48px)" }}>
      <Title title="Profile" />
      <CardContent>
        <Typography variant="h6" fontWeight="500" gutterBottom>
          User Profile
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Manage your user profile information and account settings here.
        </Typography>

        <Grid container spacing={4} mt={4}>
          <Grid size={{ xs: 12, md: 5 }}>
            <Typography variant="subtitle1" fontWeight="500" gutterBottom>
              Profile Information
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Manage and update your personal information.
            </Typography>
            <ProfileCard />
          </Grid>
          <Grid size={{ xs: 12, md: 7 }}>
            <Typography variant="subtitle1" fontWeight="500" gutterBottom>
              Account Security
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Manage your password, authentication methods, and account access.
            </Typography>
            <AccountSecurity />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};
