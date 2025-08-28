import {
  BooleanInput,
  Edit,
  SimpleForm,
  SelectInput,
  TextInput,
} from "react-admin";

const roles = [
  { id: "admin", name: "Admin" },
  { id: "user", name: "User" },
];

export const UserEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="email" />
      <SelectInput source="role" choices={roles} />
      <TextInput source="profile" />
      <BooleanInput source="verified" />
    </SimpleForm>
  </Edit>
);
