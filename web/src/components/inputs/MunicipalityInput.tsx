import { SelectInput, SelectInputProps } from "react-admin";
import { useWatch } from "react-hook-form";
import { geodata } from "../../utils";

export const MunicipalityInput = (props: Partial<SelectInputProps>) => {
  const province: string = useWatch({ name: "province" });
  const municipalities: Record<string, string[]> = geodata[province] ?? {};
  const choices: string[] = Object.keys(municipalities);

  return <SelectInput source="municipality" choices={choices} {...props} />;
};
