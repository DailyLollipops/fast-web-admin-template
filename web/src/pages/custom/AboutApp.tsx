import { Card, CardContent, Typography } from "@mui/material";

export const AboutApp = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h4" gutterBottom>
          About This App
        </Typography>
        <Typography variant="body1">
          This is a sample React-Admin application demonstrating how to add
          custom pages with routing, authorization, and styled components.
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={2}>
          Version: 1.0.0
        </Typography>
      </CardContent>
    </Card>
  );
};
