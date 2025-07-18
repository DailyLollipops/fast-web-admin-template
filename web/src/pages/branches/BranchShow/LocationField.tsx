import { useRecordContext } from "react-admin";
import { Typography, Box } from "@mui/material";
import PlaceIcon from "@mui/icons-material/Place";

export const LocationField = () => {
  const record = useRecordContext();
  if (!record) return null;

  const { barangay, municipality, province } = record;
  const location = [barangay, municipality, province]
    .filter(Boolean)
    .join(", ");

  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
      <PlaceIcon color="action" fontSize="small" />
      <Typography>{location}</Typography>
    </Box>
  );
};
