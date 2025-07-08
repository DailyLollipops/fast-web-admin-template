import { Create, SimpleForm, TextInput, required } from "react-admin";
import {
  ProvinceInput,
  MunicipalityInput,
  BarangayInput,
} from "../../components";

export const BranchCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" validate={[required()]} />
      <ProvinceInput />
      <MunicipalityInput />
      <BarangayInput />
    </SimpleForm>
  </Create>
);
