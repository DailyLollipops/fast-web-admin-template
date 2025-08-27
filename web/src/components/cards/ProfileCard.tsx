import { ReactNode } from "react";
import { useGetIdentity } from "react-admin";
import { Avatar, Box, Card, Divider, Typography } from "@mui/material";
import EmailIcon from "@mui/icons-material/Email";
import PersonIcon from "@mui/icons-material/Person";
import VerifiedUserIcon from "@mui/icons-material/VerifiedUser";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";

type ProfileFieldProps = {
  label: string;
  value: string;
  icon: ReactNode;
};

const ProfileField = ({ label, value, icon }: ProfileFieldProps) => (
  <Box
    display="flex"
    alignItems="center"
    justifyContent="space-between"
    mb={1}
    width="100%"
  >
    <Box display="flex" flexDirection="row" alignItems="center">
      <Box sx={{ mr: 1, color: "text.secondary" }}>{icon}</Box>
      <Typography variant="body2" fontWeight="500">
        {label}
      </Typography>
    </Box>
    <Typography variant="body2">{value}</Typography>
  </Box>
);

export const ProfileCard = () => {
  const { identity } = useGetIdentity();
  return (
    <Card
      sx={{
        p: 2,
        justifyItems: "center",
        width: "100%",
        mt: 3,
      }}
    >
      <Avatar
        src={identity?.profile || undefined}
        sx={{ width: 108, height: 108, mb: 1 }}
      >
        {identity?.name?.charAt(0) ?? "A"}
      </Avatar>
      <Typography variant="h6">{identity?.name}</Typography>
      <Divider sx={{ my: 2, width: "100%" }} />
      <ProfileField
        label="Email"
        value={identity!.email}
        icon={<EmailIcon />}
      />
      <ProfileField label="Role" value={identity!.role} icon={<PersonIcon />} />
      <ProfileField
        label="Registered"
        value={new Date(identity!.created_at).toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "2-digit",
        })}
        icon={<CalendarTodayIcon />}
      />
      <ProfileField
        label="Verified"
        value={identity!.verified ? "Yes ✅" : "No ❌"}
        icon={<VerifiedUserIcon />}
      />
    </Card>
  );
};
