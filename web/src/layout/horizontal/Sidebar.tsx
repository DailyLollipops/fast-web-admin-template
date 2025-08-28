import { useState } from "react";
import { useGetIdentity, useResourceDefinitions } from "react-admin";
import {
  Collapse,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  useTheme,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import ExtensionIcon from "@mui/icons-material/Extension";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LanguageIcon from "@mui/icons-material/Language";
import Logo from "@/assets/brand.svg?react";
import { ResourceItem } from "./Appbar/ResourceItem";

interface SidebarProps {
  mobileOpen: boolean;
  onClose: () => void;
}

export const Sidebar = (props: SidebarProps) => {
  return (
    <>
      <Drawer
        variant="temporary"
        open={props.mobileOpen}
        onClose={props.onClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: "block", sm: "block", md: "none" },
          "& .MuiDrawer-paper": {
            width: 240,
            backgroundColor: "#800000",
            color: "#fff",
          },
        }}
      >
        <SizebarContent />
      </Drawer>

      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", sm: "none", md: "block" },
          "& .MuiDrawer-paper": {
            width: 240,
            backgroundColor: "#800000",
            color: "#fff",
          },
        }}
        open
      >
        <SizebarContent />
      </Drawer>
    </>
  );
};

const SizebarContent = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const resources = useResourceDefinitions();
  const { identity } = useGetIdentity();
  const [openMenus, setOpenMenus] = useState<{ [key: string]: boolean }>({});

  const toggleMenu = (menuKey: string) => {
    setOpenMenus((prev) => ({
      ...prev,
      [menuKey]: !prev[menuKey],
    }));
  };

  return (
    <>
      <Toolbar>
        <Logo
          style={{
            height: 48,
            width: 200,
            color: theme.palette.mode === "dark" ? "#fff" : "#fff",
          }}
        />
      </Toolbar>
      <List>
        <ListItemButton onClick={() => navigate("/")}>
          <ListItemIcon sx={{ color: "#fff" }}>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItemButton>

        <>
          <ListItemButton onClick={() => toggleMenu("resources")}>
            <ListItemIcon sx={{ color: "#fff" }}>
              <ExtensionIcon />
            </ListItemIcon>
            <ListItemText primary="Resources" />
            {openMenus["resources"] ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
          <Collapse in={openMenus["resources"]} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {Object.values(resources).map((resource) => (
                <ResourceItem key={resource.name} resource={resource} />
              ))}
            </List>
          </Collapse>
        </>

        {identity?.role === "system" && (
          <ListItemButton onClick={() => navigate("/settings")}>
            <ListItemIcon sx={{ color: "#fff" }}>
              <AdminPanelSettingsIcon />
            </ListItemIcon>
            <ListItemText primary="App Settings" />
          </ListItemButton>
        )}

        <ListItemButton onClick={() => navigate("/about")}>
          <ListItemIcon sx={{ color: "#fff" }}>
            <LanguageIcon />
          </ListItemIcon>
          <ListItemText primary="About App" />
        </ListItemButton>
      </List>
    </>
  );
};
