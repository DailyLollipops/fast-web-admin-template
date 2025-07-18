import { useState } from "react";
import {
  Show,
  SimpleShowLayout,
  ReferenceManyField,
  Pagination,
} from "react-admin";
import {
  Box,
  Button,
  Fab,
  Typography,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { BranchNameField } from "./BranchShow/BranchNameField";
import { LocationField } from "./BranchShow/LocationField";
import { MachineCards } from "./BranchShow/MachineCards";
import { AddMachineDialog } from "./BranchShow/AddMachineDialog";
import { useRecordContext } from "react-admin";

const BranchShowContent = () => {
  const record = useRecordContext();
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down("sm"));
  const [open, setOpen] = useState(false);

  if (!record) return null;

  return (
    <>
      <AddMachineDialog
        branchId={record.id.toString()}
        open={open}
        onClose={() => setOpen(false)}
      />

      <BranchNameField />
      <LocationField />

      <Box
        display="flex"
        flexDirection="row"
        justifyContent="space-between"
        alignItems="center"
      >
        <Typography variant="h6" sx={{ my: 3 }}>
          Machines in this Branch
        </Typography>

        {isSm ? (
          <Fab
            color="primary"
            onClick={() => setOpen(true)}
            sx={{
              position: "fixed",
              bottom: 16,
              right: 16,
              zIndex: 1300,
            }}
            aria-label="Add Machine"
          >
            <AddIcon />
          </Fab>
        ) : (
          <Button
            startIcon={<AddIcon />}
            variant="contained"
            onClick={() => setOpen(true)}
            sx={{ mt: 2 }}
          >
            Add Machine
          </Button>
        )}
      </Box>

      <ReferenceManyField
        reference="machines"
        target="branch_id"
        sort={{ field: "id", order: "ASC" }}
        perPage={6}
        pagination={<Pagination rowsPerPageOptions={[6, 12, 24]} />}
      >
        <MachineCards />
      </ReferenceManyField>
    </>
  );
};

export const BranchShow = () => (
  <Show>
    <SimpleShowLayout>
      <BranchShowContent />
    </SimpleShowLayout>
  </Show>
);
