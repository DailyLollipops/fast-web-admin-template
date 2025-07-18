import { Edit, ReferenceInput, SimpleForm, TextInput } from "react-admin";

export const MachineEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="id" readOnly />
      <ReferenceInput source="branch_id" reference="branches" />
      <TextInput source="name" />
    </SimpleForm>
  </Edit>
);
