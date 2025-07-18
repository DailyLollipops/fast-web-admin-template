import {
  Create,
  SimpleForm,
  TextInput,
  ReferenceInput,
  required,
} from "react-admin";

export const MachineCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" validate={[required()]} />
      <ReferenceInput source="branch_id" reference="branches" />
    </SimpleForm>
  </Create>
);
