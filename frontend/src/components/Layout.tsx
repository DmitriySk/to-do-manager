import LogoutIcon from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
import {
  AppBar,
  Avatar,
  Box,
  Divider,
  Drawer,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { type ReactNode, useState } from "react";

import { useAuth } from "../auth/AuthContext";
import type { NotificationItem } from "../types";
import NotificationPanel from "./NotificationPanel";
import Sidebar from "./Sidebar";

const DRAWER_WIDTH = 280;

interface LayoutProps {
  selectedListId: number | null;
  onSelectList: (id: number | null) => void;
  notifications: NotificationItem[];
  onAckNotification: (id: string) => void;
  children: ReactNode;
}

export default function Layout({ selectedListId, onSelectList, notifications, onAckNotification, children }: LayoutProps) {
  const theme = useTheme();
  const isNarrow = useMediaQuery(theme.breakpoints.down("md"));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const { user, logout } = useAuth();

  const drawerContent = <Sidebar selectedListId={selectedListId} onSelectList={(id) => {
    onSelectList(id);
    if (isNarrow) setMobileOpen(false);
  }} />;

  return (
    <Box sx={{ display: "flex", height: "100vh" }}>
      <AppBar
        position="fixed"
        color="inherit"
        elevation={0}
        sx={{ borderBottom: "1px solid rgba(0,0,0,0.08)", zIndex: (t) => t.zIndex.drawer + 1 }}
      >
        <Toolbar sx={{ gap: 1 }}>
          {isNarrow && (
            <IconButton edge="start" aria-label="Open lists menu" onClick={() => setMobileOpen(true)}>
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" fontWeight={700} sx={{ flexGrow: 1 }}>
            To-Do Manager
          </Typography>

          <NotificationPanel notifications={notifications} onAck={onAckNotification} />

          <IconButton onClick={(e) => setUserMenuAnchor(e.currentTarget)} aria-label="Account menu" sx={{ ml: 1 }}>
            <Avatar src={user?.avatar_url ?? undefined} sx={{ width: 32, height: 32 }}>
              {user?.display_name?.[0]?.toUpperCase()}
            </Avatar>
          </IconButton>
          <Menu anchorEl={userMenuAnchor} open={Boolean(userMenuAnchor)} onClose={() => setUserMenuAnchor(null)}>
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="body2" fontWeight={600}>
                {user?.display_name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email}
              </Typography>
            </Box>
            <Divider />
            <MenuItem onClick={() => logout()}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Log out</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {isNarrow ? (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ "& .MuiDrawer-paper": { width: DRAWER_WIDTH } }}
        >
          {drawerContent}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{
            width: DRAWER_WIDTH,
            flexShrink: 0,
            "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box", borderRight: "1px solid rgba(0,0,0,0.08)" },
          }}
          open
        >
          <Toolbar />
          {drawerContent}
        </Drawer>
      )}

      <Box component="main" sx={{ flexGrow: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
        <Toolbar />
        <Box sx={{ flex: 1, overflowY: "auto" }}>{children}</Box>
      </Box>
    </Box>
  );
}
