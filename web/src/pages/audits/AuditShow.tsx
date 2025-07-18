import {
  DateField,
  NumberField,
  ReferenceField,
  Show,
  SimpleShowLayout,
  TextField,
} from "react-admin";

export const AuditShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <ReferenceField source="user_id" reference="users" />
      <ReferenceField source="branch_id" reference="branches" />
      <ReferenceField source="machine_id" reference="machines" />
      <ReferenceField source="product_id" reference="products" />
      <NumberField source="remaining" />
      <TextField source="dispensed" />
      <TextField source="price" />
      <TextField source="sales" />
      <NumberField source="refill_amount" />
      <TextField source="category" />
      <DateField source="created_at" showTime={true} />
    </SimpleShowLayout>
  </Show>
);
