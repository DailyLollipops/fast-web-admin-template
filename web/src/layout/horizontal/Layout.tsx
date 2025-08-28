import { ReactNode, useState } from "react";
import { Box, CssBaseline } from "@mui/material";
import { Sidebar } from "./Sidebar";
import { AppBar } from "./AppBar";

export const Layout = ({ children }: { children: ReactNode }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const handleDrawerToggle = () => setMobileOpen((prev) => !prev);

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <Sidebar mobileOpen={mobileOpen} onClose={handleDrawerToggle} />

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: "oklch(96.7% 0.003 264.542)",
          p: 3,
          marginLeft: { md: "240px" },
          minHeight: "100vh",
          height: "100%",
        }}
      >
        <AppBar onToggleDrawer={handleDrawerToggle} />

        {children}
      </Box>
    </Box>
  );
};
