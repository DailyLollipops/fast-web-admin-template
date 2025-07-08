import { ThemeOptions } from "@mui/material/styles";
import { defaultTheme } from "react-admin";
import { deepmerge } from "@mui/utils";

const drawerStyleOverrides = {
  MuiDrawer: {
    styleOverrides: {
      paper: {
        backgroundColor: "#ffffff", // white for light mode
        color: "#000000",
        width: 260,
        borderRight: "1px solid #e0e0e0",
        boxShadow: "2px 0 10px rgba(0,0,0,0.05)",
        borderTopRightRadius: 12,
        borderBottomRightRadius: 12,
      },
    },
  },
};

const drawerStyleOverridesDark = {
  MuiDrawer: {
    styleOverrides: {
      paper: {
        backgroundColor: "#1e1e1e", // dark drawer background
        color: "#ffffff",
        width: 260,
        borderRight: "1px solid #333",
        boxShadow: "2px 0 10px rgba(0,0,0,0.3)",
        borderTopRightRadius: 12,
        borderBottomRightRadius: 12,
      },
    },
  },
};

const lightThemeOptions: ThemeOptions = {
  palette: {
    mode: "light",
    primary: {
      main: "#b53f45",
    },
    secondary: {
      main: "#f50057",
    },
    background: {
      default: "#f5f5f5",
      paper: "#ffffff",
    },
    text: {
      primary: "#000000",
      secondary: "#4f4f4f",
    },
  },
  components: drawerStyleOverrides,
};

const darkThemeOptions: ThemeOptions = {
  palette: {
    mode: "dark",
    primary: {
      main: "#b53f45",
    },
    secondary: {
      main: "#f50057",
    },
    background: {
      default: "#121212",
      paper: "#1e1e1e",
    },
    text: {
      primary: "#ffffff",
      secondary: "#b0b0b0",
    },
  },
  components: drawerStyleOverridesDark,
};

export const lightTheme = deepmerge(defaultTheme, lightThemeOptions);
export const darkTheme = deepmerge(defaultTheme, darkThemeOptions);
