import { Admin, Resource } from "react-admin";
import ManageAccountsIcon from "@mui/icons-material/ManageAccounts";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";
import { Layout } from "./layout/Layout";
import { dataProvider, authProvider } from "./providers";
import { Dashboard } from "./pages/dashboard";
import { UserList, UserShow, UserEdit, UserCreate } from "./pages/users";
import {
  BranchList,
  BranchShow,
  BranchEdit,
  BranchCreate,
} from "./pages/branches";

export const App = () => (
  <Admin
    layout={Layout}
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
  >
    <Resource
      name="users"
      icon={ManageAccountsIcon}
      list={UserList}
      show={UserShow}
      edit={UserEdit}
      create={UserCreate}
    />
    <Resource
      name="branches"
      icon={LocalGasStationIcon}
      list={BranchList}
      show={BranchShow}
      edit={BranchEdit}
      create={BranchCreate}
    />
  </Admin>
);
