import { useState } from "react";
import { useGetList } from "react-admin";
import {
  ListItemIcon,
  ListItemText,
  MenuItem,
  Typography,
  IconButton,
  Badge,
  Menu,
} from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import SystemUpdateAltIcon from "@mui/icons-material/SystemUpdateAlt";
import { getRelativeDate } from "../../../utils";

const categoryIcons: Record<string, JSX.Element> = {
  default: <SystemUpdateAltIcon color="primary" />,
};

export const NotificationMenu = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const { data: notifications, isLoading: notificationsLoading } = useGetList(
    "notifications",
    {
      sort: { field: "created_at", order: "DESC" },
    },
  );

  if (notificationsLoading) return null;

  return (
    <>
      <IconButton
        color="inherit"
        onClick={(e) => setAnchorEl(e.currentTarget)}
        sx={{ ml: "auto" }}
      >
        <Badge badgeContent={notifications!.length} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={() => setAnchorEl(null)}
        slotProps={{
          paper: { sx: { width: { xs: 300, md: 400 } } },
        }}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        {notifications!.map((n) => {
          const icon = categoryIcons[n.category] || (
            <SystemUpdateAltIcon color="primary" />
          );

          return (
            <MenuItem
              key={n.id}
              sx={{
                alignItems: "flex-start",
                whiteSpace: "normal",
                py: 1.5,
              }}
            >
              {/* Icon */}
              <ListItemIcon sx={{ mt: 0.5 }}>{icon}</ListItemIcon>

              <ListItemText
                primary={
                  <Typography
                    variant="subtitle2"
                    fontWeight={600}
                    sx={{ whiteSpace: "normal", wordBreak: "break-word" }}
                  >
                    {n.title}
                  </Typography>
                }
                secondary={
                  <>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        display: "block",
                        mb: 0.5,
                        whiteSpace: "normal",
                        wordBreak: "break-word",
                      }}
                    >
                      {n.body}
                    </Typography>
                    <Typography variant="caption" color="text.disabled">
                      {getRelativeDate(new Date(n.created_at))}
                    </Typography>
                  </>
                }
              />
            </MenuItem>
          );
        })}
        {notifications!.length === 0 && (
          <MenuItem>
            <Typography variant="body2" color="text.secondary">
              No new notifications
            </Typography>
          </MenuItem>
        )}
      </Menu>
    </>
  );
};
