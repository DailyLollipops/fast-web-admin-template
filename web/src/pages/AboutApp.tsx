import { Card, CardContent, Typography } from "@mui/material";

export const AboutApp = () => {
  return (
    <Card sx={{ p: 3, borderRadius: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: "bold" }}>
          About This App
        </Typography>

        <Typography variant="body1">
          A web template integrating both FastAPI for backend and React Admin
          for the frontend, along with other utilities to easily bootstrap a web
          application.
        </Typography>

        <Typography variant="body2" color="text.secondary" mt={3}>
          Version: 1.0.0
        </Typography>
      </CardContent>
    </Card>
  );
};
