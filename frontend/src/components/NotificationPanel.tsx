import CloseIcon from "@mui/icons-material/Close";
import NotificationsIcon from "@mui/icons-material/Notifications";
import {
  Badge,
  Box,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Popover,
  Typography,
} from "@mui/material";
import { useState } from "react";

import type { NotificationItem } from "../types";
import EmptyState from "./EmptyState";

interface NotificationPanelProps {
  notifications: NotificationItem[];
  onAck: (id: string) => void;
}

const KIND_LABEL: Record<NotificationItem["kind"], string> = {
  overdue: "Overdue",
  due_soon: "Due soon",
};

const KIND_COLOR: Record<NotificationItem["kind"], "error" | "warning"> = {
  overdue: "error",
  due_soon: "warning",
};

export default function NotificationPanel({ notifications, onAck }: NotificationPanelProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  return (
    <>
      <IconButton
        aria-label={`Notifications (${notifications.length})`}
        onClick={(e) => setAnchorEl(e.currentTarget)}
      >
        <Badge badgeContent={notifications.length} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={() => setAnchorEl(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
      >
        <Box sx={{ width: 340, maxHeight: 420, overflowY: "auto" }}>
          <Box sx={{ px: 2, py: 1.5, borderBottom: "1px solid rgba(0,0,0,0.08)" }}>
            <Typography variant="subtitle2">Notifications</Typography>
          </Box>

          {notifications.length === 0 ? (
            <EmptyState title="You're all caught up" description="No overdue or due-soon tasks right now." />
          ) : (
            <List disablePadding>
              {notifications.map((n) => (
                <ListItem
                  key={n.id}
                  divider
                  secondaryAction={
                    <IconButton edge="end" size="small" aria-label="Dismiss notification" onClick={() => onAck(n.id)}>
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  }
                >
                  <ListItemText
                    primary={n.title}
                    secondary={
                      <>
                        <Chip
                          label={KIND_LABEL[n.kind]}
                          color={KIND_COLOR[n.kind]}
                          size="small"
                          sx={{ mr: 1, height: 20 }}
                        />
                        Due {n.due_date}
                      </>
                    }
                    secondaryTypographyProps={{ component: "span", sx: { display: "flex", alignItems: "center", mt: 0.5 } }}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Popover>
    </>
  );
}
