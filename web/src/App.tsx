import { Admin, Resource } from "react-admin";
import ManageAccountsIcon from "@mui/icons-material/ManageAccounts";
import StoreIcon from "@mui/icons-material/Store";
import GasMeterIcon from "@mui/icons-material/GasMeter";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import { Layout } from "./layout/Layout";
import { dataProvider, authProvider } from "./providers";
import { Dashboard } from "./pages/dashboard";
import { UserList, UserShow, UserEdit, UserCreate } from "./pages/users";
import { AuditList, AuditShow } from "./pages/audits";
import {
  BranchList,
  BranchShow,
  BranchEdit,
  BranchCreate,
} from "./pages/branches";
import {
  ProductList,
  ProductShow,
  ProductEdit,
  ProductCreate,
} from "./pages/products";
import {
  MachineList,
  MachineShow,
  MachineEdit,
  MachineCreate,
} from "./pages/machines";

export const App = () => (
  <Admin
    layout={Layout}
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
  >
    <Resource
      name="branches"
      icon={StoreIcon}
      list={BranchList}
      show={BranchShow}
      edit={BranchEdit}
      create={BranchCreate}
    />
    <Resource
      name="products"
      icon={GasMeterIcon}
      list={ProductList}
      show={ProductShow}
      edit={ProductEdit}
      create={ProductCreate}
    />
    <Resource
      name="machines"
      icon={LocalGasStationIcon}
      list={MachineList}
      show={MachineShow}
      edit={MachineEdit}
      create={MachineCreate}
    />
    <Resource
      name="audits"
      icon={ReceiptLongIcon}
      list={AuditList}
      show={AuditShow}
    />
    <Resource
      name="users"
      icon={ManageAccountsIcon}
      list={UserList}
      show={UserShow}
      edit={UserEdit}
      create={UserCreate}
    />
  </Admin>
);
