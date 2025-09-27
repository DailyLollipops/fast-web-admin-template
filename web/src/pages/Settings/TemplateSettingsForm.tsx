import { useState } from "react";
import {
  useDataProvider,
  useGetList,
  Form,
  SaveButton,
  Toolbar,
  useNotify,
  FileInput,
  FileField,
  SelectInput,
} from "react-admin";
import { Typography, Grid, Box, Tooltip, IconButton } from "@mui/material";
import { useFormContext, Controller } from "react-hook-form";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import Editor from "@monaco-editor/react";

type Template = {
  id: number;
  name: string;
  path: string;
  template_type: string;
  content: string;
  created_at: string;
  updated_at: string;
  modified_by_id: number;
};

export const TemplateSettingsForm = () => {
  const dataProvider = useDataProvider();
  const { data, isLoading } = useGetList("templates", {
    meta: { infinite: true },
  });

  const notify = useNotify();
  const [selected, setSelected] = useState<Template | null>(null);
  const [uploadedContent, setUploadedContent] = useState<string | null>(null);

  if (isLoading) return null;
  const templates = data as Template[] | undefined;

  const ApplicationSettingsFormToolbar = () => {
    const { getValues } = useFormContext();

    const handleSave = async () => {
      const values = getValues();

      try {
        const data = values.templates[selected?.id ?? 0];
        console.log("Saving form values:", data);
        await dataProvider.update("templates", {
          id: selected?.id ?? 0,
          data: { content: data.content },
          previousData: selected ?? {},
        });
        notify("Templates saved successfully", { type: "info" });
      } catch (error: unknown) {
        if (error instanceof Error) {
          notify(`Error: ${error.message}`, { type: "error" });
        } else {
          notify(`An unknown error occurred`, { type: "error" });
        }
      }
    };

    return (
      <Toolbar sx={{ my: 2 }}>
        <SaveButton label="Save All" onClick={handleSave} alwaysEnable />
      </Toolbar>
    );
  };

  const getLanguageForTemplate = (type: string) => {
    switch (type.toLowerCase()) {
      case "html":
      case "htm":
        return "html";
      case "json":
        return "json";
      case "js":
      case "javascript":
        return "javascript";
      case "ts":
      case "typescript":
        return "typescript";
      case "css":
        return "css";
      case "txt":
      default:
        return "plaintext";
    }
  };

  const getTooltipTitle = (content: string) => {
    const regex = /\{\{\s?(.+?)\s?\}\}/g;
    const placeholders = Array.from(
      new Set(Array.from(content.matchAll(regex), (m) => m[1])),
    );

    if (placeholders.length === 0) {
      return "No valid placeholders";
    }

    return (
      <Box>
        <Typography variant="subtitle2" sx={{ fontWeight: 500, mb: 0.5 }}>
          Valid Placeholders:
        </Typography>
        <Box component="ul" sx={{ m: 0, pl: 2 }}>
          {placeholders.map((ph, idx) => (
            <li key={idx}>{ph}</li>
          ))}
        </Box>
      </Box>
    );
  };

  return (
    <>
      <Typography variant="subtitle1" sx={{ fontWeight: "500", mb: 2 }}>
        Template Settings
      </Typography>

      <Form
        values={{
          templates: templates?.reduce(
            (acc, tpl) => {
              acc[tpl.id] = { content: tpl.content };
              return acc;
            },
            {} as Record<number, { content: string }>,
          ),
        }}
      >
        {/* Row 1: Template select + Upload */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid size={6}>
            <SelectInput
              source="templateSelect"
              label="Select Template"
              choices={
                templates?.map((tpl) => ({
                  id: tpl.id,
                  name: tpl.name,
                })) ?? []
              }
              fullWidth
              onChange={(e) => {
                const tpl = templates?.find((t) => t.id === e.target.value);
                setSelected(tpl ?? null);
                setUploadedContent(null);
              }}
            />
          </Grid>
          <Grid size={6}>
            <FileInput
              source="file"
              label="Upload Template File (optional)"
              onChange={(files: File[] | null) => {
                if (files && files[0]) {
                  const reader = new FileReader();
                  reader.onload = (ev) => {
                    setUploadedContent(ev.target?.result as string);
                  };
                  reader.readAsText(files[0]);
                } else {
                  setUploadedContent(null);
                }
              }}
            >
              <FileField source="src" title="title" />
            </FileInput>
          </Grid>
        </Grid>

        {/* Row 2: Editor + Preview */}
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
            >
              <Typography variant="subtitle2" gutterBottom>
                Editor
              </Typography>
              <Tooltip
                title={getTooltipTitle(
                  selected?.content ?? uploadedContent ?? "",
                )}
              >
                <IconButton size="small" sx={{ p: 0.5 }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            {selected ? (
              <Controller
                key={selected?.id}
                name={`templates.${selected.id}.content`}
                defaultValue={selected.content}
                render={({ field }) => (
                  <Box
                    sx={{
                      border: "1px solid #ddd",
                      borderRadius: 1,
                      p: 2,
                      height: "450px",
                      backgroundColor: "#fafafa",
                      overflow: "auto",
                    }}
                  >
                    <Editor
                      height="100%"
                      language={getLanguageForTemplate(selected.template_type)}
                      value={uploadedContent ?? field.value}
                      onChange={(value) => {
                        setUploadedContent(null);
                        field.onChange(value ?? "");
                      }}
                      options={{
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        wordWrap: "on",
                        fontSize: 14,
                        automaticLayout: true,
                      }}
                    />
                  </Box>
                )}
              />
            ) : (
              <Typography variant="body1" color="textSecondary">
                Select a template to edit
              </Typography>
            )}
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Typography variant="subtitle2" gutterBottom>
              Preview
            </Typography>
            <Box
              sx={{
                border: "1px solid #ddd",
                borderRadius: 1,
                p: 2,
                minHeight: "350px",
                backgroundColor: "#fafafa",
                overflow: "auto",
              }}
            >
              {selected ? (
                <Controller
                  key={selected?.id}
                  name={`templates.${selected.id}.content`}
                  defaultValue={selected.content}
                  render={({ field }) => (
                    <div
                      dangerouslySetInnerHTML={{
                        __html: uploadedContent ?? field.value,
                      }}
                    />
                  )}
                />
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No template selected
                </Typography>
              )}
            </Box>
          </Grid>
        </Grid>

        <ApplicationSettingsFormToolbar />
      </Form>
    </>
  );
};
