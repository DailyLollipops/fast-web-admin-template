import {
  Form,
  SaveButton,
  Toolbar,
  useDataProvider,
  useNotify,
  useRefresh,
  ArrayInput,
  SimpleFormIterator,
  TextInput,
  ResourceContextProvider,
  useGetList,
  RaRecord,
} from "react-admin";
import {
  Typography,
  Box,
  IconButton,
  Tooltip,
  Button,
  Card,
  CardContent,
} from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import DeleteIcon from "@mui/icons-material/Delete";
import { useFormContext, useFieldArray } from "react-hook-form";

type RoleSetting = {
  id?: number;
  role: string;
  permissions: string[];
};

type RoleAccessData = RoleSetting[];

export const RoleAccessSettingsForm = () => {
  const { data, isLoading } = useGetList("role_access_controls", {
    sort: { field: "id", order: "ASC" },
    meta: { infinite: true },
  });
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  if (isLoading) return null;
  const initialData = data as RoleSetting[] | undefined;

  const RoleAccessSettingsFormToolbar = () => {
    const { getValues } = useFormContext();

    const handleSave = async () => {
      const values: RoleAccessData = getValues("roles");

      const roleNames = values.map((r) => r.role.trim());
      const duplicates = roleNames.filter(
        (name, index) => roleNames.indexOf(name) !== index,
      );
      if (duplicates.length > 0) {
        notify(
          `Duplicate role name detected: "${duplicates[0]}". Please use unique names.`,
          { type: "warning" },
        );
        return;
      }

      try {
        const updates = values.map((item) => {
          if (item.id) {
            return dataProvider.update("role_access_controls", {
              id: item.id,
              data: { permissions: item.permissions },
              previousData: item,
            });
          } else {
            return dataProvider.create("role_access_controls", {
              data: { role: item.role.trim(), permissions: item.permissions },
            });
          }
        });

        const valueIds = values.map((v) => v.id).filter(Boolean);
        const missingRoles = initialData!.filter(
          (orig) => orig.id && !valueIds.includes(orig.id),
        );

        const deletes = missingRoles.map((role) =>
          dataProvider.delete("role_access_controls", {
            id: role.id!,
            previousData: role as RaRecord,
          }),
        );

        await Promise.all([...updates, ...deletes]);
        notify("Roles updated successfully", { type: "success" });
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

  const RolesFieldArray = () => {
    const { control } = useFormContext();
    const { fields, append, remove } = useFieldArray({
      control,
      name: "roles",
    });

    return (
      <Box display="flex" flexDirection="column" gap={2}>
        {fields.map((field, index) => (
          <Card key={field.id} variant="outlined">
            <CardContent>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                mb={2}
              >
                <TextInput
                  source={`roles.${index}.role`}
                  label="Role Name"
                  fullWidth
                />
                <IconButton onClick={() => remove(index)}>
                  <DeleteIcon />
                </IconButton>
              </Box>

              <ArrayInput source={`roles.${index}.permissions`}>
                <SimpleFormIterator>
                  <TextInput source="" label="Permission" fullWidth />
                </SimpleFormIterator>
              </ArrayInput>
            </CardContent>
          </Card>
        ))}

        <Button
          variant="outlined"
          sx={{ my: 4 }}
          onClick={() => append({ role: "", permissions: [] })}
        >
          + Add Role
        </Button>
      </Box>
    );
  };

  return (
    <Form defaultValues={{ roles: initialData ?? [] }}>
      <ResourceContextProvider value="role_access_controls">
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Typography variant="h6" sx={{ fontWeight: 500 }}>
            Role Access Control Settings
          </Typography>
          <Tooltip title="Permission format: <resource>.<action>. Use * for all.">
            <IconButton size="small" sx={{ p: 0.5 }}>
              <HelpOutlineIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        <RolesFieldArray />

        <RoleAccessSettingsFormToolbar />
      </ResourceContextProvider>
    </Form>
  );
};
