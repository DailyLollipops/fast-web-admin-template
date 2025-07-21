import { Card, CardContent, Typography, Stack, Box } from "@mui/material";
import BadgeIcon from "@mui/icons-material/Badge";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import StoreIcon from "@mui/icons-material/Store";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";

interface BranchInfoCardProps {
  name: string;
  location: string;
  machineCount: number;
}

export const BranchInfoCard = (props: BranchInfoCardProps) => {
  return (
    <Card
      sx={{
        position: "relative",
        p: 3,
        borderRadius: 4,
        minHeight: { lg: 284 },
      }}
    >
      <Box
        component="svg"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
        sx={{
          position: "absolute",
          top: -40,
          right: -40,
          width: 160,
          height: 160,
          zIndex: 0,
          opacity: 0.1,
          transform: "rotate(15deg)",
        }}
      >
        <path
          fill="#1976d2"
          d="M53.4,-67.3C68.3,-59.7,79.1,-45.1,80.5,-30.1C82,-15.1,74,0.2,67.4,16.2C60.7,32.1,55.4,48.6,43.9,59.6C32.5,70.7,15.7,76.2,0.5,75.4C-14.6,74.6,-29.2,67.6,-44.5,58.2C-59.8,48.9,-75.9,37.1,-81.6,21.8C-87.3,6.5,-82.6,-12.3,-73.3,-27.3C-64.1,-42.3,-50.2,-53.6,-35.4,-60.9C-20.6,-68.2,-4.9,-71.4,10.4,-74.1C25.7,-76.7,51.2,-78.8,53.4,-67.3Z"
          transform="translate(100 100)"
        />
      </Box>
      <Box
        component="svg"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
        sx={{
          position: "absolute",
          bottom: -40,
          left: -40,
          width: 160,
          height: 160,
          zIndex: 0,
          opacity: 0.08,
          transform: "rotate(-25deg)",
        }}
      >
        <path
          fill="#1976d2"
          d="M38.1,-62.6C51.1,-55.3,65.2,-48.5,70.8,-37.6C76.4,-26.6,73.5,-11.5,71.4,4.2C69.3,20,68.1,36.4,59.7,46.3C51.4,56.2,35.9,59.5,21.4,61.3C6.9,63.2,-6.7,63.5,-19.6,58.9C-32.5,54.2,-44.6,44.6,-54.7,32.5C-64.9,20.3,-73,5.7,-72.6,-8.2C-72.3,-22.1,-63.6,-35.3,-52.6,-45.4C-41.7,-55.5,-28.6,-62.5,-14.5,-68.2C-0.4,-73.9,14.7,-78.2,28.6,-73.8C42.5,-69.4,56.2,-56.3,38.1,-62.6Z"
          transform="translate(100 100)"
        />
      </Box>
      <CardContent>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: "bold" }}>
          Branch Info
        </Typography>

        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
          <StoreIcon fontSize="small" color="action" />
          <Typography
            variant="body2"
            color="text.primary"
            sx={{ fontWeight: "bold" }}
          >
            {props.name}
          </Typography>
        </Stack>

        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
          <LocationOnIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {props.location}
          </Typography>
        </Stack>

        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
          <LocalGasStationIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {props.machineCount}{" "}
            {props.machineCount === 1 ? "machine" : "machines"}
          </Typography>
        </Stack>

        <Stack direction="row" alignItems="center" spacing={1}>
          <BadgeIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            Pump Attendant
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
};
