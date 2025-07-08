import { DataTable, List } from "react-admin";

export const BranchList = () => (
  <List>
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.Col source="name" />
      <DataTable.Col source="province" />
      <DataTable.Col source="municipality" />
      <DataTable.Col source="barangay" />
    </DataTable>
  </List>
);
