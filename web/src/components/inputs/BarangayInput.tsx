import { SelectInput, SelectInputProps } from "react-admin";
import { useWatch } from "react-hook-form";
import { geodata } from "../../utils";

export const BarangayInput = (props: Partial<SelectInputProps>) => {
  const province: string = useWatch({ name: "province" });
  const municipality: string = useWatch({ name: "municipality" });
  const barangays: string[] = geodata?.[province]?.[municipality] ?? [];

  return <SelectInput source="barangay" choices={barangays} {...props} />;
};
