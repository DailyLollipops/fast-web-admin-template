import { TextInput, TextInputProps, required } from "react-admin";
import { useWatch } from "react-hook-form";

export const ConfirmPasswordInput = (props: Partial<TextInputProps>) => {
  const password = useWatch({ name: "password" });

  const validate = (value: string) =>
    value === password ? undefined : "Passwords do not match";

  return (
    <TextInput
      source="confirm_password"
      label="Confirm Password"
      type="password"
      validate={[required(), validate]}
      {...props}
    />
  );
};
