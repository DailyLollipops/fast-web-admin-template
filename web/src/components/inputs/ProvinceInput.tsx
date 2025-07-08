import { SelectInput, SelectInputProps } from "react-admin";
import { geodata } from "../../utils";

export const ProvinceInput = (props: Partial<SelectInputProps>) => {
  const provinces: string[] = Object.keys(geodata);

  return <SelectInput source="province" choices={provinces} {...props} />;
};
