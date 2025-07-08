import { Show, SimpleShowLayout, TextField } from "react-admin";

export const BranchShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="province" />
      <TextField source="municipality" />
      <TextField source="barangay" />
    </SimpleShowLayout>
  </Show>
);
