import { Title } from "react-admin";
import { Box, Card, CardContent } from "@mui/material";
import { ApplicationSettingsForm } from "./Settings/ApplicationSettingsForm";
import { RoleAccessSettingsForm } from "./Settings/RoleAccessSettingsForm";

export const Settings = () => {
  return (
    <Card>
      <Title title="Application Settings" />
      <CardContent>
        <Box gap={2}>
          <ApplicationSettingsForm />
          <RoleAccessSettingsForm />
        </Box>
      </CardContent>
    </Card>
  );
};
