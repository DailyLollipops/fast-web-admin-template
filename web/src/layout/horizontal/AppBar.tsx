import { TitlePortal, useGetIdentity } from "react-admin";
import {
  Box,
  AppBar as MuiAppBar,
  Toolbar,
  Typography,
  IconButton,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { NotificationMenu } from "./Appbar/NotificationMenu";
import { UserMenu } from "./Appbar/UserMenu";

interface AppBarProps {
  onToggleDrawer: () => void;
}

export const AppBar = (props: AppBarProps) => {
  const { identity } = useGetIdentity();

  return (
    <MuiAppBar
      position="static"
      color="transparent"
      elevation={0}
      sx={{ mb: 2 }}
    >
      <Toolbar
        sx={{
          display: "flex",
          justifyContent: "space-between",
          background: "white",
          borderRadius: 2,
        }}
      >
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={props.onToggleDrawer}
          sx={{ display: { md: "none" } }}
        >
          <MenuIcon />
        </IconButton>
        <TitlePortal color="#000000" fontWeight="bold" />
        <Box display="flex" alignItems="center" gap={2}>
          <Typography
            fontWeight="bold"
            sx={{ display: { xs: "none", sm: "block" } }}
          >
            {identity?.name || "User"}
          </Typography>
          <NotificationMenu />
          <UserMenu />
        </Box>
      </Toolbar>
    </MuiAppBar>
  );
};
