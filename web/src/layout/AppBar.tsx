import React from "react";
import {
  AppBar as RaAppBar,
  Logout,
  UserMenu,
  useUserMenu,
  TitlePortal,
} from "react-admin";
import {
  Box,
  ListItemIcon,
  ListItemText,
  MenuItem,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import { Link } from "react-router-dom";
import Logo from "../assets/Logo.png";

// eslint-disable-next-line react/display-name
const SettingsMenuItem = React.forwardRef<HTMLAnchorElement>((props, ref) => {
  const userMenuContext = useUserMenu();
  if (!userMenuContext) {
    throw new Error("<SettingsMenuItem> should be used inside a <UserMenu>");
  }
  const { onClose } = userMenuContext;
  return (
    <MenuItem
      onClick={onClose}
      ref={ref}
      component={Link}
      to="/profile"
      {...props}
    >
      <ListItemIcon>
        <SettingsIcon fontSize="small" />
      </ListItemIcon>
      <ListItemText>Profile Settings</ListItemText>
    </MenuItem>
  );
});

const AppBarUserMenu = () => (
  <UserMenu>
    <SettingsMenuItem />
    <Logout />
  </UserMenu>
);

export const AppBar = () => {
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <RaAppBar userMenu={<AppBarUserMenu />}>
      {!isSm && (
        <>
          <Box component="img" src={Logo} alt="Logo" sx={{ height: 32 }} />
          <Box sx={{ width: 32 }} />
        </>
      )}
      <TitlePortal sx={{ textAlign: "center" }} />
    </RaAppBar>
  );
};
