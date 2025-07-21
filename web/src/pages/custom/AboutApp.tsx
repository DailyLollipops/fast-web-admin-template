import { Card, CardContent, Typography } from "@mui/material";

export const AboutApp = () => {
  return (
    <Card sx={{ p: 3, borderRadius: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: "bold" }}>
          About This App
        </Typography>

        <Typography variant="body1" paragraph>
          This application is a sales and inventory monitoring system developed
          specifically for local gas stations in the province of Marinduque,
          Philippines. It streamlines daily operations by enabling branch-level
          data entry, centralized sales tracking, and inventory oversight.
        </Typography>

        <Typography variant="body1" paragraph>
          The system supports multiple user roles:
        </Typography>

        <Typography variant="body2" component="ul" sx={{ pl: 3 }}>
          <li>
            <strong>Pump Attendant</strong> – records daily sales and expenses
            at their assigned station.
          </li>
          <li>
            <strong>Sales Admin</strong> – monitors and analyzes overall sales
            data across all branches.
          </li>
          <li>
            <strong>Inventory Admin</strong> – manages gasoline reserves,
            machine information, and product inventory.
          </li>
          <li>
            <strong>Owner</strong> – oversees the entire system and accesses all
            high-level reports.
          </li>
          <li>
            <strong>Admin</strong> – handles user management and system
            configuration.
          </li>
        </Typography>

        <Typography variant="body2" color="text.secondary" mt={3}>
          Version: 1.0.0
        </Typography>
      </CardContent>
    </Card>
  );
};
