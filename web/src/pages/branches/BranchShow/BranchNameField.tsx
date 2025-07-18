import { useRecordContext } from "react-admin";
import { Typography, Box } from "@mui/material";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";

export const BranchNameField = () => {
  const record = useRecordContext();
  if (!record) return null;

  const { name } = record;

  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
      <LocalGasStationIcon color="action" fontSize="small" />
      <Typography>{name}</Typography>
    </Box>
  );
};
