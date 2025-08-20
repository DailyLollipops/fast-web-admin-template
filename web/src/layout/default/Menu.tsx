import { Menu as RaMenu } from "react-admin";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LanguageIcon from "@mui/icons-material/Language";

export const Menu = () => (
  <RaMenu>
    <RaMenu.DashboardItem />
    <RaMenu.ResourceItems />
    <RaMenu.Item
      to="/settings"
      primaryText="App Settings"
      leftIcon={<AdminPanelSettingsIcon />}
    />
    <RaMenu.Item
      to="/about"
      primaryText="About App"
      leftIcon={<LanguageIcon />}
    />
  </RaMenu>
);
