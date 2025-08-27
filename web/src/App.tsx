import {
  Admin,
  CustomRoutes,
  Resource,
  ListGuesser,
  ShowGuesser,
  EditGuesser,
} from "react-admin";
import { Route } from "react-router-dom";
import PeopleIcon from "@mui/icons-material/People";
import { DefaultLayout } from "./layout";
import { dataProvider, authProvider } from "./providers";
import { Dashboard, Settings, Profile, AboutApp } from "./pages";

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
      list={ListGuesser}
      show={ShowGuesser}
      edit={EditGuesser}
    />
    <CustomRoutes>
      <Route path="/settings" element={<Settings />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/about" element={<AboutApp />} />
    </CustomRoutes>
  </Admin>
);
