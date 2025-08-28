import { useEffect, useState } from "react";
import { useAuthProvider, ResourceDefinition } from "react-admin";
import { useNavigate } from "react-router-dom";
import { ListItemButton, ListItemIcon, ListItemText } from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import StorageIcon from "@mui/icons-material/Storage";
import { snakeToCapitalizedWords } from "@/utils";

export const ResourceItem = ({
  resource,
}: {
  resource: ResourceDefinition;
}) => {
  const navigate = useNavigate();
  const authProvider = useAuthProvider();
  const [allowed, setAllowed] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    const check = async () => {
      if (!authProvider?.canAccess) {
        setAllowed(true);
        return;
      }
      try {
        const can = await authProvider.canAccess({
          action: "list",
          resource: resource.name,
        });
        if (active) setAllowed(can);
      } catch {
        if (active) setAllowed(false);
      }
    };
    check();
    return () => {
      active = false;
    };
  }, [resource, authProvider]);

  if (allowed === null) {
    return null;
  }

  return (
    <ListItemButton
      sx={{ pl: 4 }}
      onClick={() =>
        allowed ? navigate(`/${resource.name}`) : navigate("/access-denied")
      }
    >
      <ListItemIcon sx={{ color: "#fff" }}>
        {resource.icon ? <resource.icon /> : <StorageIcon />}
      </ListItemIcon>
      <ListItemText primary={snakeToCapitalizedWords(resource.name)} />
      {!allowed && <LockIcon sx={{ color: "rgba(255,255,255,0.6)" }} />}
    </ListItemButton>
  );
};
