/* eslint-disable react/jsx-key */
import {
  DataTable,
  DateField,
  List,
  ReferenceField,
  ReferenceInput,
} from "react-admin";

const filters = [
  <ReferenceInput
    source="branch_id"
    label="Branch"
    reference="branches"
    alwaysOn
  />,
  <ReferenceInput
    source="machine_id"
    label="Machine"
    reference="machines"
    alwaysOn
  />,
  <ReferenceInput
    source="product_id"
    label="Product"
    reference="products"
    alwaysOn
  />,
];

export const AuditList = () => (
  <List filters={filters}>
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.Col source="user_id">
        <ReferenceField source="user_id" reference="users" />
      </DataTable.Col>
      <DataTable.Col source="branch_id">
        <ReferenceField source="branch_id" reference="branches" />
      </DataTable.Col>
      <DataTable.Col source="machine_id">
        <ReferenceField source="machine_id" reference="machines" />
      </DataTable.Col>
      <DataTable.Col source="product_id">
        <ReferenceField source="product_id" reference="products" />
      </DataTable.Col>
      <DataTable.NumberCol source="remaining" />
      <DataTable.Col source="dispensed" />
      <DataTable.Col source="price" />
      <DataTable.Col source="sales" />
      <DataTable.NumberCol source="refill_amount" />
      <DataTable.Col source="category" />
      <DataTable.Col source="created_at">
        <DateField
          source="created_at"
          showTime
          options={{
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "numeric",
            minute: "2-digit",
            hour12: true,
          }}
        />
      </DataTable.Col>
    </DataTable>
  </List>
);
