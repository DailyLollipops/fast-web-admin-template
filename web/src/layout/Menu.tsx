import { Menu as RaMenu } from "react-admin";
import LanguageIcon from "@mui/icons-material/Language";

export const Menu = () => (
  <RaMenu>
    <RaMenu.DashboardItem />
    <RaMenu.ResourceItems />
    <RaMenu.Item
      to="/about"
      primaryText="About App"
      leftIcon={<LanguageIcon />}
    />
  </RaMenu>
);
