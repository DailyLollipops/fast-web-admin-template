import { Logout, UserMenu as RaUserMenu, useGetIdentity } from "react-admin";
import {
  Avatar,
  Box,
  Divider,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Typography,
} from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import VerifiedIcon from "@mui/icons-material/Verified";
import { Link } from "react-router-dom";
import { snakeToCapitalizedWords, stringToMuiColor } from "../../../utils";
import { API_URL } from "../../../constants";

export const UserMenu = () => {
  const { identity } = useGetIdentity();
  console.log("Identity:", identity);

  const ProfileIcon = ({ size }: { size: number }) => {
    if (identity?.profile) {
      return (
        <Avatar
          src={`${API_URL}${identity.profile}`}
          sx={{ width: size, height: size }}
        />
      );
    }

    return (
      <Avatar
        sx={{
          width: size,
          height: size,
          bgcolor: stringToMuiColor(identity?.name ?? "Anonymous"),
        }}
      >
        {identity?.name?.charAt(0).toUpperCase() ?? "A"}
      </Avatar>
    );
  };

  return (
    <RaUserMenu icon={<ProfileIcon size={32} />}>
      {/* Profile Info */}
      <Box display="flex" flexDirection="row" padding={1} alignItems="center">
        <ProfileIcon size={48} />
        <Box display="flex" flexDirection="column" marginLeft={1} gap={0}>
          <Typography variant="subtitle2" marginLeft={1}>
            {identity?.name ?? "Anonymous"}
          </Typography>
          <Typography
            variant="caption"
            color="text.secondary"
            marginLeft={1}
            display="block"
          >
            {identity?.email ?? "No Email"}
          </Typography>
          <Box
            display="flex"
            flexDirection="row"
            gap={0.5}
            ml={0.75}
            alignItems="center"
          >
            <VerifiedIcon fontSize="small" color="success" />
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
            >
              {snakeToCapitalizedWords(identity?.role ?? "User")}
            </Typography>
          </Box>
        </Box>
      </Box>
      <Divider />

      {/* Profile Settings */}
      <MenuItem component={Link} to="/profile">
        <ListItemIcon>
          <SettingsIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>Profile Settings</ListItemText>
      </MenuItem>

      {/* Logout Button */}
      <Logout />
    </RaUserMenu>
  );
};
