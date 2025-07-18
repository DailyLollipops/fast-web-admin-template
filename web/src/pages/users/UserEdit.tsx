import { Edit, ReferenceInput, SimpleForm, TextInput } from "react-admin";

export const UserEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="id" readOnly />
      <TextInput source="email" />
      <TextInput source="role" />
      <TextInput source="name" />
      <ReferenceInput source="branch_id" reference="branches" />
    </SimpleForm>
  </Edit>
);
