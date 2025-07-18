import {
  Create,
  SimpleForm,
  TextInput,
  ImageInput,
  ImageField,
  required,
} from "react-admin";

export const ProductCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" validate={[required()]} />
      <TextInput multiline source="description" validate={[required()]} />
      <ImageInput source="image" label="Image" validate={[required()]}>
        <ImageField source="src" title="name" />
      </ImageInput>
    </SimpleForm>
  </Create>
);
