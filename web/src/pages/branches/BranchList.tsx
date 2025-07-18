/* eslint-disable react/jsx-key */
import { DataTable, List, TextInput } from "react-admin";

const filters = [
  <TextInput source="name" label="Search" alwaysOn />,
  <TextInput source="province" label="Province" />,
  <TextInput source="municipality" label="Municipality" />,
  <TextInput source="barangay" label="Barangay" />,
];

export const BranchList = () => (
  <List filters={filters}>
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.Col source="name" />
      <DataTable.Col source="province" />
      <DataTable.Col source="municipality" />
      <DataTable.Col source="barangay" />
    </DataTable>
  </List>
);
