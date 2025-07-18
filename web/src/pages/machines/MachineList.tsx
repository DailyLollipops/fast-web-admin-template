import { DataTable, List, ReferenceField } from "react-admin";

export const MachineList = () => (
  <List>
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.Col source="branch_id">
        <ReferenceField source="branch_id" reference="branches" />
      </DataTable.Col>
      <DataTable.Col source="name" />
    </DataTable>
  </List>
);
