import { useState } from "react";
import { Title } from "react-admin";
import { Box, Card, CardContent, Tabs, Tab, Typography } from "@mui/material";
import { ApplicationSettingsForm } from "./Settings/ApplicationSettingsForm";
import { RoleAccessSettingsForm } from "./Settings/RoleAccessSettingsForm";
import { TemplateSettingsForm } from "./Settings/TemplateSettingsForm";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
    >
      {value === index && (
        <Box sx={{ pt: 2 }}>
          <Typography component="div">{children}</Typography>
        </Box>
      )}
    </div>
  );
}

export const Settings = () => {
  const [tab, setTab] = useState(0);

  const handleChange = (_: React.SyntheticEvent, newValue: number) => {
    setTab(newValue);
  };

  return (
    <Card sx={{ minHeight: "calc(100vh - 48px)" }}>
      <Title title="Application Settings" />
      <CardContent>
        <Typography variant="h6" fontWeight="500" gutterBottom>
          Application System Settings
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Manage the application wide settings such as environment variables,
          authentication methods, and role access permissions, etc.
        </Typography>

        <Tabs
          value={tab}
          onChange={handleChange}
          aria-label="settings tabs"
          textColor="primary"
          indicatorColor="primary"
          sx={{ mt: 2 }}
        >
          <Tab
            label="Application"
            id="settings-tab-0"
            aria-controls="settings-tabpanel-0"
          />
          <Tab
            label="Role Access"
            id="settings-tab-1"
            aria-controls="settings-tabpanel-1"
          />
          <Tab
            label="Templates"
            id="settings-tab-2"
            aria-controls="settings-tabpanel-2"
          />
        </Tabs>

        <TabPanel value={tab} index={0}>
          <ApplicationSettingsForm />
        </TabPanel>

        <TabPanel value={tab} index={1}>
          <RoleAccessSettingsForm />
        </TabPanel>

        <TabPanel value={tab} index={2}>
          <TemplateSettingsForm />
        </TabPanel>
      </CardContent>
    </Card>
  );
};
