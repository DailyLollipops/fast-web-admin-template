import {
  Edit,
  SimpleForm,
  TextInput,
  ImageInput,
  ImageField,
} from "react-admin";

export const ProductEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="id" readOnly />
      <TextInput source="name" />
      <TextInput source="description" />
      <ImageInput source="image" label="Image">
        <ImageField source="src" title="name" />
      </ImageInput>
    </SimpleForm>
  </Edit>
);
