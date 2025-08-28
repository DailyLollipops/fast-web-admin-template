import {
  BooleanField,
  ColumnsButton,
  DataTable,
  DateField,
  EmailField,
  ExportButton,
  List,
  SearchInput,
  TopToolbar,
} from "react-admin";

const userFilters = [<SearchInput key="q" source="email_ilike" alwaysOn />];
const UserListActions = () => (
  <TopToolbar>
    <ColumnsButton />
    <ExportButton />
  </TopToolbar>
);

export const UserList = () => (
  <List actions={<UserListActions />} filters={userFilters}>
    <DataTable hiddenColumns={["updated_at", "profile"]}>
      <DataTable.Col source="id" />
      <DataTable.Col source="name" />
      <DataTable.Col source="email">
        <EmailField source="email" />
      </DataTable.Col>
      <DataTable.Col source="role" />
      <DataTable.Col source="profile" />
      <DataTable.Col source="verified">
        <BooleanField source="verified" />
      </DataTable.Col>
      <DataTable.Col source="created_at">
        <DateField source="created_at" />
      </DataTable.Col>
      <DataTable.Col source="updated_at">
        <DateField source="updated_at" />
      </DataTable.Col>
    </DataTable>
  </List>
);
