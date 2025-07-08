import {
  EmailField,
  ReferenceField,
  Show,
  SimpleShowLayout,
  TextField,
} from "react-admin";

export const UserShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <EmailField source="email" />
      <TextField source="role" />
      <TextField source="name" />
      <ReferenceField source="branch_id" reference="branches" />
    </SimpleShowLayout>
  </Show>
);
