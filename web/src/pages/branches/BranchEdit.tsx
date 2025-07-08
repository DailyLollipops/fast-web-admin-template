import { Edit, SimpleForm, TextInput } from "react-admin";
import {
  ProvinceInput,
  MunicipalityInput,
  BarangayInput,
} from "../../components";

export const BranchEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <ProvinceInput />
      <MunicipalityInput />
      <BarangayInput />
    </SimpleForm>
  </Edit>
);
