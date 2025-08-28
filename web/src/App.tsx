import { Admin, CustomRoutes, Resource } from "react-admin";
import { Route } from "react-router-dom";
import PeopleIcon from "@mui/icons-material/People";
import { DefaultLayout } from "@/layout";
import { dataProvider, authProvider } from "@/providers";
import {
  Dashboard,
  Settings,
  Profile,
  AboutApp,
  UserList,
  UserShow,
  UserEdit,
  UserCreate,
} from "@/pages";

export const App = () => (
  <Admin
    layout={DefaultLayout}
    dataProvider={dataProvider}
    authProvider={authProvider}
    dashboard={Dashboard}
  >
    <Resource
      name="users"
      icon={PeopleIcon}
      list={UserList}
      show={UserShow}
      edit={UserEdit}
      create={UserCreate}
    />
    <CustomRoutes>
      <Route path="/settings" element={<Settings />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/about" element={<AboutApp />} />
    </CustomRoutes>
  </Admin>
);
