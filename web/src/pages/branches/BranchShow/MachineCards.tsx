import { useListContext } from "react-admin";
import { Grid } from "@mui/material";
import { MachineCard } from "../../../components";

export const MachineCards = () => {
  const { data, isLoading } = useListContext();
  if (isLoading) return <>Loading...</>;
  if (!data || data.length === 0) return <>No machines found.</>;

  return (
    <Grid container spacing={2} sx={{ mt: 1 }}>
      {data.map((machine) => (
        <Grid size={{ xs: 12, sm: 6, md: 6, lg: 4 }} key={machine.id}>
          <MachineCard machine={machine} actions={true} />
        </Grid>
      ))}
    </Grid>
  );
};
