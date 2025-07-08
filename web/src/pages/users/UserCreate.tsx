import {
  Create,
  SimpleForm,
  TextInput,
  SelectInput,
  required,
} from "react-admin";
import { ConfirmPasswordInput } from "../../components";

const choices = [
  { id: "pump_attendant", name: "Pump Attendant" },
  { id: "admin_sales", name: "Admin Sales" },
  { id: "admin_inventory", name: "Admin Inventory" },
  { id: "owner", name: "Owner" },
];

export const UserCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" validate={[required()]} />
      <TextInput source="email" validate={[required()]} />
      <TextInput source="password" type="password" validate={[required()]} />
      <ConfirmPasswordInput />
      <SelectInput source="role" choices={choices} validate={[required()]} />
    </SimpleForm>
  </Create>
);
