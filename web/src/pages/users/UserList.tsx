/* eslint-disable react/jsx-key */
import {
  DataTable,
  EmailField,
  FunctionField,
  List,
  ReferenceField,
  ReferenceInput,
  TextInput,
} from "react-admin";

const filters = [
  <TextInput source="name" label="Search" alwaysOn />,
  <ReferenceInput source="branch_id" label="Branch" reference="branches" />,
];

const roleMap: Record<string, string> = {
  pump_attendant: "Pump Attendant",
  admin_sales: "Admin Sales",
  admin_inventory: "Admin Inventory",
  owner: "Owner",
  admin: "Admin",
  system: "System",
};

export const UserList = () => (
  <List filters={filters}>
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.Col source="email">
        <EmailField source="email" />
      </DataTable.Col>
      <DataTable.Col source="role">
        <FunctionField
          label="role"
          render={(record) => roleMap[record.role] ?? record.role}
        />
      </DataTable.Col>
      <DataTable.Col source="name" />
      <DataTable.Col source="branch_id">
        <ReferenceField source="branch_id" reference="branches" />
      </DataTable.Col>
    </DataTable>
  </List>
);
