import {
  Show,
  SimpleShowLayout,
  TextField,
  useRecordContext,
} from "react-admin";
import { Box } from "@mui/material";
import { API_URL } from "../../constants";

const ProductImageField = () => {
  const record = useRecordContext();

  if (!record || !record.image) return null;

  return (
    <Box
      component="img"
      src={`${API_URL}${record.image}`}
      alt={record.name}
      sx={{ maxWidth: 300 }}
    />
  );
};

export const ProductShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <ProductImageField />
    </SimpleShowLayout>
  </Show>
);
