import { Admin, CustomRoutes, Resource } from "react-admin";
import { Route } from "react-router-dom";
import ManageAccountsIcon from "@mui/icons-material/ManageAccounts";
import StoreIcon from "@mui/icons-material/Store";
import GasMeterIcon from "@mui/icons-material/GasMeter";
import LocalGasStationIcon from "@mui/icons-material/LocalGasStation";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import { AUTH_DETAILS } from "./constants";
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
import { AboutApp } from "./pages/custom";

const resourcePermissions = {
  branches: ["admin", "owner", "admin_sales", "admin_inventory"],
  products: ["admin", "owner", "admin_sales", "admin_inventory"],
  machines: ["admin", "owner", "admin_sales", "admin_inventory"],
  audits: [
    "admin",
    "owner",
    "admin_sales",
    "admin_inventory",
    "pump_attendant",
  ],
  users: ["admin", "owner"],
};

export const App = () => {
  const authCredentials = JSON.parse(localStorage.getItem(AUTH_DETAILS)!);
  const { role } = authCredentials ?? { role: "" };

  return (
    <Admin
      requireAuth
      layout={Layout}
      dataProvider={dataProvider}
      authProvider={authProvider}
      dashboard={Dashboard}
    >
      {resourcePermissions.branches.includes(role ?? "") && (
        <Resource
          name="branches"
          icon={StoreIcon}
          list={BranchList}
          show={BranchShow}
          edit={BranchEdit}
          create={BranchCreate}
        />
      )}
      {resourcePermissions.products.includes(role ?? "") && (
        <Resource
          name="products"
          icon={GasMeterIcon}
          list={ProductList}
          show={ProductShow}
          edit={ProductEdit}
          create={ProductCreate}
        />
      )}
      {resourcePermissions.machines.includes(role ?? "") && (
        <Resource
          name="machines"
          icon={LocalGasStationIcon}
          list={MachineList}
          show={MachineShow}
          edit={MachineEdit}
          create={MachineCreate}
        />
      )}
      {resourcePermissions.audits.includes(role ?? "") && (
        <Resource
          name="audits"
          icon={ReceiptLongIcon}
          list={AuditList}
          show={AuditShow}
        />
      )}
      {resourcePermissions.users.includes(role ?? "") && (
        <Resource
          name="users"
          icon={ManageAccountsIcon}
          list={UserList}
          show={UserShow}
          edit={UserEdit}
          create={UserCreate}
        />
      )}
      <CustomRoutes>
        <Route path="/about" element={<AboutApp />} />
      </CustomRoutes>
    </Admin>
  );
};
