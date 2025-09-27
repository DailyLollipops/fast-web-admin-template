import {
  useGetList,
  Form,
  TextInput,
  SaveButton,
  Toolbar,
  useDataProvider,
  useNotify,
  useRefresh,
  SelectInput,
} from "react-admin";
import { Typography, Grid, Box, Tooltip, IconButton } from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { useFormContext } from "react-hook-form";

type Setting = {
  id: number;
  name: string;
  value: string;
  created_at: string;
  updated_at: string;
  modified_by_id: number;
};

export const ApplicationSettingsForm = () => {
  const { data, isLoading } = useGetList("application_settings", {
    meta: { infinite: true },
  });

  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  if (isLoading) return null;
  const applicationSettings = data as Setting[] | undefined;

  const mappedSettings = [
    "notification",
    "user_verification",
    "base_url",
    "smtp_server",
    "smtp_port",
    "smtp_username",
    "smtp_password",
  ];
  const unmappedSettings: Setting[] = applicationSettings!.filter(
    (s) => !mappedSettings.includes(s.name),
  );

  const getSettingByName = (settings: Setting[], name: string) => {
    return settings.find((setting) => setting.name === name);
  };

  const ApplicationSettingsFormToolbar = () => {
    const { getValues } = useFormContext();

    const handleSave = async () => {
      const values = getValues();

      try {
        const updates = Object.entries(values)
          .filter(([name, value]) => {
            const original = applicationSettings!.find((s) => s.name === name);
            return original && String(original.value) !== String(value);
          })
          .map(([name, value]) =>
            dataProvider.update("application_settings", {
              id: applicationSettings!.find((s) => s.name === name)!.id,
              data: { name, value },
              previousData: applicationSettings!.find((s) => s.name === name)!,
            }),
          );

        if (updates.length === 0) {
          notify("No changes to save", { type: "info" });
          return;
        }

        await Promise.all(updates);
        notify("Settings updated successfully", { type: "success" });
        refresh();
      } catch (error: unknown) {
        if (error instanceof Error) {
          notify(`Error: ${error.message}`, { type: "error" });
        } else {
          notify(`An unknown error occurred`, { type: "error" });
        }
      }
    };

    return (
      <Toolbar sx={{ mb: 4 }}>
        <SaveButton label="Save All" onClick={handleSave} alwaysEnable />
      </Toolbar>
    );
  };

  return (
    <>
      <Typography variant="subtitle1" sx={{ fontWeight: "500", mb: 2 }}>
        Application Settings
      </Typography>
      <Form>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="subtitle2" sx={{ fontWeight: "500" }}>
            SMTP Settings
          </Typography>
          <Tooltip title="Required for user email verification.">
            <IconButton size="small" sx={{ p: 0.5 }}>
              <HelpOutlineIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Grid container columnGap={1} mb={2}>
          <Grid size={{ xs: 12, sm: 5.9, lg: 2.9 }}>
            <TextInput
              source="smtp_server"
              label="SMTP Server"
              helperText="SMTP server host (e.g. smtp.gmail.com)"
              defaultValue={
                getSettingByName(applicationSettings!, "smtp_server")?.value ??
                ""
              }
              fullWidth
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 5.9, lg: 2.9 }}>
            <TextInput
              source="smtp_port"
              label="SMTP Port"
              helperText="SMTP server host (e.g. 465)"
              defaultValue={
                getSettingByName(applicationSettings!, "smtp_port")?.value ?? ""
              }
              fullWidth
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 5.9, lg: 2.9 }}>
            <TextInput
              source="smtp_username"
              label="SMTP Username"
              defaultValue={
                getSettingByName(applicationSettings!, "smtp_username")
                  ?.value ?? ""
              }
              fullWidth
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 5.9, lg: 2.9 }}>
            <TextInput
              source="smtp_password"
              label="SMTP Password"
              type="password"
              defaultValue={
                getSettingByName(applicationSettings!, "smtp_password")
                  ?.value ?? ""
              }
              fullWidth
            />
          </Grid>
        </Grid>
        <Typography variant="subtitle2" sx={{ fontWeight: "500" }}>
          User Authentication
        </Typography>
        <Grid container columnGap={1} mb={2}>
          <Grid size={{ xs: 12, sm: 5.9, lg: 2.9 }}>
            <SelectInput
              source="user_verification"
              helperText="Setting to `none` would automatically set new users as verified"
              defaultValue={
                getSettingByName(applicationSettings!, "user_verification")
                  ?.value ?? ""
              }
              choices={[
                { id: "none", name: "None" },
                { id: "email", name: "Email" },
              ]}
            />
          </Grid>
        </Grid>
        <Typography variant="subtitle2" sx={{ fontWeight: "500" }}>
          Notifications
        </Typography>
        <Grid container columnGap={1} mb={2}>
          <Grid size={{ xs: 12, sm: 5.9, lg: 2.9 }}>
            <SelectInput
              source="notification"
              helperText="Allow creation of notification records on actions that invoke it"
              defaultValue={
                getSettingByName(applicationSettings!, "notification")?.value ??
                ""
              }
              choices={[
                { id: "0", name: "Disabled" },
                { id: "1", name: "Enabled" },
              ]}
            />
          </Grid>
        </Grid>
        <Grid container gap={2}>
          {unmappedSettings.length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ fontWeight: "500" }}>
                Other Settings
              </Typography>
              <Grid container columnGap={1}>
                {unmappedSettings.map((setting) => (
                  <Grid size={{ xs: 12, sm: 5.9, lg: 2.9 }} key={setting.name}>
                    <TextInput
                      source={setting.name}
                      defaultValue={setting.value}
                      fullWidth
                    />
                  </Grid>
                ))}
              </Grid>
            </>
          )}
        </Grid>
        <ApplicationSettingsFormToolbar />
      </Form>
    </>
  );
};
