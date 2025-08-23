import { Menu as RaMenu, useGetIdentity } from "react-admin";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LanguageIcon from "@mui/icons-material/Language";

export const Menu = () => {
  const { identity } = useGetIdentity();
  return (
    <RaMenu>
      <RaMenu.DashboardItem />
      <RaMenu.ResourceItems />
      {identity?.role === "system" && (
        <RaMenu.Item
          to="/settings"
          primaryText="App Settings"
          leftIcon={<AdminPanelSettingsIcon />}
        />
      )}
      <RaMenu.Item
        to="/about"
        primaryText="About App"
        leftIcon={<LanguageIcon />}
      />
    </RaMenu>
  );
};
