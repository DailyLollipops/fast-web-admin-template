import {
  Admin,
  Resource,
  ListGuesser,
  ShowGuesser,
  EditGuesser,
} from "react-admin";
import { Layout } from "./Layout";
import { dataProvider, authProvider } from "./providers";

export const App = () => (
  <Admin
    layout={Layout}
    dataProvider={dataProvider}
    authProvider={authProvider}
  >
    <Resource
      name="users"
      list={ListGuesser}
      show={ShowGuesser}
      edit={EditGuesser}
    />
  </Admin>
);
