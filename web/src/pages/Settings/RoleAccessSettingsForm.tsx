import { useState, useEffect } from "react";
import { useGetList, useUpdate } from "react-admin";
import { useFormContext } from "react-hook-form";
import {
  Box,
  Typography,
  List,
  ListItemButton,
  ListItemText,
  Divider,
  IconButton,
  CircularProgress,
  TextField,
  Autocomplete,
} from "@mui/material";
import { Add, Delete } from "@mui/icons-material";

type RoleSetting = {
  id?: number;
  role: string;
  permissions: string[];
};

type FormValues = {
  roles: RoleSetting[];
};

export const RoleAccessSettingsForm = () => {
  const { data: availableRoles, isLoading } = useGetList(
    "role_access_controls",
    {
      sort: { field: "id", order: "ASC" },
      filter: { role_neq: "system" },
    },
  );

  const { data: allPermissions } = useGetList("permissions", {
    meta: { infinite: true },
  });

  const [update] = useUpdate();
  const { watch, setValue, getValues } = useFormContext<FormValues>();
  const roles = watch("roles") || [];

  const [selectedRoleIndex, setSelectedRoleIndex] = useState(0);
  const [newPermission, setNewPermission] = useState("");

  useEffect(() => {
    if (availableRoles) {
      setValue("roles", availableRoles);
    }
  }, [availableRoles, setValue]);

  const selectedRole = roles[selectedRoleIndex];

  const removePermission = (permission: string) => {
    if (!selectedRole) return;

    const updated = selectedRole.permissions.filter((p) => p !== permission);
    setValue(`roles.${selectedRoleIndex}.permissions`, updated, {
      shouldDirty: true,
    });

    const currentRole = getValues(`roles.${selectedRoleIndex}`);
    update("role_access_controls", {
      id: currentRole.id,
      data: {
        role: currentRole.role,
        permissions: updated,
      },
      previousData: currentRole,
    });
  };

  const addPermission = () => {
    if (!selectedRole) return;

    const trimmed = newPermission.trim();
    if (!trimmed) return;

    if (selectedRole.permissions.includes(trimmed)) {
      setNewPermission("");
      return;
    }

    const updated = [...selectedRole.permissions, trimmed];
    setValue(`roles.${selectedRoleIndex}.permissions`, updated, {
      shouldDirty: true,
    });
    setNewPermission("");

    const currentRole = getValues(`roles.${selectedRoleIndex}`);
    update("role_access_controls", {
      id: currentRole.id,
      data: {
        role: currentRole.role,
        permissions: updated,
      },
      previousData: currentRole,
    });
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box display="flex" minHeight={500}>
      <Box width={260} borderRight="1px solid" borderColor="divider">
        <Box p={2}>
          <Typography fontWeight={600}>Roles</Typography>
        </Box>
        <Divider />
        <List dense>
          {roles.map((role, index) => (
            <ListItemButton
              key={index}
              selected={selectedRoleIndex === index}
              onClick={() => setSelectedRoleIndex(index)}
            >
              <ListItemText primary={role.role || `Role ${index + 1}`} />
            </ListItemButton>
          ))}
        </List>
      </Box>

      <Box flex={1} p={3}>
        {!selectedRole ? (
          <Typography>Select a role</Typography>
        ) : (
          <>
            <Typography variant="h6" fontWeight={600}>
              {selectedRole.role}
            </Typography>

            <Box display="flex" gap={2} mb={2} alignItems="center">
              <Autocomplete
                disablePortal
                options={allPermissions?.map((p) => p.name).sort() || []}
                inputValue={newPermission}
                onChange={(_, value) => {
                  if (value) {
                    setNewPermission(value);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    e.stopPropagation();
                    addPermission();
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    size="small"
                    placeholder="users.create, posts.delete, etc."
                    label="New Permission"
                  />
                )}
              />
              <IconButton
                color="primary"
                onClick={addPermission}
                sx={{
                  height: 48,
                  width: 48,
                  borderRadius: 1,
                  border: "1px solid",
                  borderColor: "primary.main",
                }}
              >
                <Add />
              </IconButton>
            </Box>

            <Box
              sx={{
                maxHeight: 420,
                overflowY: "auto",
                pr: 1,
              }}
            >
              {selectedRole.permissions.length > 0 ? (
                selectedRole.permissions.map((perm) => (
                  <Box
                    key={perm}
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    py={0.5}
                    px={1}
                    borderBottom="1px solid"
                    borderColor="divider"
                  >
                    <Typography variant="body2">{perm}</Typography>
                    <IconButton
                      size="small"
                      onClick={() => removePermission(perm)}
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No enabled permissions
                </Typography>
              )}
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
};
