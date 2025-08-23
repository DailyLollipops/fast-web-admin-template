import { AppBar as RaAppBar, TitlePortal } from "react-admin";
import { useMediaQuery, useTheme } from "@mui/material";
import Logo from "../../assets/brand.svg?react";
import { UserMenu } from "./Appbar/UserMenu";
import { NotificationMenu } from "./Appbar/NotificationMenu";

export const AppBar = () => {
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <RaAppBar userMenu={<UserMenu />}>
      {!isSm && (
        <>
          <Logo
            style={{
              height: 48,
              width: 200,
              color: theme.palette.mode === "dark" ? "#fff" : "#fff",
            }}
          />
          <TitlePortal sx={{ textAlign: "center" }} />
        </>
      )}
      <NotificationMenu />
    </RaAppBar>
  );
};
