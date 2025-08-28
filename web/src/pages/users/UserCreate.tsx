import {
  Create,
  SimpleForm,
  TextInput,
  SelectInput,
  required,
} from "react-admin";
import { ConfirmPasswordInput } from "@/components";

const roles = [
  { id: "admin", name: "Admin" },
  { id: "user", name: "User" },
];

export const UserCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" validate={[required()]} />
      <TextInput source="email" validate={[required()]} />
      <TextInput source="password" type="password" validate={[required()]} />
      <ConfirmPasswordInput />
      <SelectInput source="role" choices={roles} validate={[required()]} />
    </SimpleForm>
  </Create>
);
