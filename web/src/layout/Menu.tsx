import { Menu as RaMenu } from "react-admin";
import LabelIcon from "@mui/icons-material/Label";

export const Menu = () => (
  <RaMenu>
    <RaMenu.DashboardItem />
    <RaMenu.ResourceItems />
    <RaMenu.Item
      to="/custom-route"
      primaryText="Miscellaneous"
      leftIcon={<LabelIcon />}
    />
  </RaMenu>
);
