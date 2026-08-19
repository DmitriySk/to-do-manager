import AddIcon from "@mui/icons-material/Add";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import EditIcon from "@mui/icons-material/Edit";
import ListAltIcon from "@mui/icons-material/ListAlt";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { useCreateList, useDeleteList, useLists, useRenameList } from "../hooks/useLists";
import type { ListProject } from "../types";
import EmptyState from "./EmptyState";
import LoadingSpinner from "./LoadingSpinner";

interface SidebarProps {
  selectedListId: number | null;
  onSelectList: (id: number | null) => void;
}

export default function Sidebar({ selectedListId, onSelectList }: SidebarProps) {
  const { data: lists, isLoading } = useLists();
  const createList = useCreateList();
  const renameList = useRenameList();
  const deleteList = useDeleteList();

  const [newListName, setNewListName] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState("");
  const [listPendingDelete, setListPendingDelete] = useState<ListProject | null>(null);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const name = newListName.trim();
    if (!name) return;
    createList.mutate(name, { onSuccess: () => setNewListName("") });
  };

  const startEditing = (list: ListProject) => {
    setEditingId(list.id);
    setEditingName(list.name);
  };

  const commitEditing = () => {
    const name = editingName.trim();
    if (editingId !== null && name) {
      renameList.mutate({ id: editingId, name });
    }
    setEditingId(null);
  };

  const confirmDelete = () => {
    if (!listPendingDelete) return;
    deleteList.mutate(listPendingDelete.id, {
      onSuccess: () => {
        if (selectedListId === listPendingDelete.id) onSelectList(null);
      },
    });
    setListPendingDelete(null);
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <List dense sx={{ py: 1 }}>
        <ListItemButton selected={selectedListId === null} onClick={() => onSelectList(null)}>
          <ListItemIcon sx={{ minWidth: 36 }}>
            <ListAltIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="All tasks" />
        </ListItemButton>
      </List>

      <Divider />

      <Box sx={{ px: 2, py: 2 }}>
        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1.5, letterSpacing: 0.5 }}>
          LISTS
        </Typography>
        <Box component="form" onSubmit={handleCreate}>
          <Stack direction="row" spacing={1}>
            <TextField
              size="small"
              fullWidth
              placeholder="New list name"
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
              inputProps={{ "aria-label": "New list name" }}
            />
            <IconButton type="submit" color="primary" aria-label="Create list" disabled={!newListName.trim()}>
              <AddIcon />
            </IconButton>
          </Stack>
        </Box>
      </Box>

      <Divider />

      <Box sx={{ flex: 1, overflowY: "auto" }}>
        {isLoading && <LoadingSpinner label="Loading lists" />}

        {!isLoading && lists && lists.length === 0 && (
          <EmptyState
            icon={<ListAltIcon sx={{ fontSize: 40, opacity: 0.4 }} />}
            title="No lists yet"
            description="Create your first list above to start adding tasks."
          />
        )}

        {!isLoading && lists && lists.length > 0 && (
          <List dense sx={{ py: 0 }}>
            {lists.map((list) => (
              <ListItemButton
                key={list.id}
                selected={selectedListId === list.id}
                onClick={() => onSelectList(list.id)}
                sx={{
                  "&:hover .list-actions": { opacity: 1 },
                  py: 1,
                }}
              >
                {editingId === list.id ? (
                  <TextField
                    size="small"
                    autoFocus
                    fullWidth
                    value={editingName}
                    onChange={(e) => setEditingName(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commitEditing();
                      if (e.key === "Escape") setEditingId(null);
                    }}
                    onBlur={commitEditing}
                  />
                ) : (
                  <>
                    <ListItemText
                      primary={list.name}
                      secondary={`${list.task_count} task${list.task_count === 1 ? "" : "s"}`}
                    />
                    <Stack
                      direction="row"
                      className="list-actions"
                      sx={{ opacity: 0, transition: "opacity 0.15s" }}
                    >
                      <IconButton
                        size="small"
                        aria-label={`Rename ${list.name}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          startEditing(list);
                        }}
                      >
                        <EditIcon fontSize="inherit" />
                      </IconButton>
                      <IconButton
                        size="small"
                        aria-label={`Delete ${list.name}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setListPendingDelete(list);
                        }}
                      >
                        <DeleteOutlineIcon fontSize="inherit" />
                      </IconButton>
                    </Stack>
                  </>
                )}
              </ListItemButton>
            ))}
          </List>
        )}
      </Box>

      <Dialog open={listPendingDelete !== null} onClose={() => setListPendingDelete(null)}>
        <DialogTitle>Delete "{listPendingDelete?.name}"?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This permanently deletes the list and all {listPendingDelete?.task_count ?? 0} task
            {listPendingDelete?.task_count === 1 ? "" : "s"} in it. This can't be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setListPendingDelete(null)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={confirmDelete}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
