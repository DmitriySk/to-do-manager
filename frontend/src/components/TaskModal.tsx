import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

import { useCreateTask, useUpdateTask } from "../hooks/useTasks";
import type { Task, TaskPriority, TaskStatus } from "../types";

interface TaskModalProps {
  open: boolean;
  onClose: () => void;
  listId: number | null;
  task?: Task | null; // present when editing, absent when creating
}

interface FormState {
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string;
}

const EMPTY_FORM: FormState = { title: "", description: "", status: "todo", priority: "medium", due_date: "" };

export default function TaskModal({ open, onClose, listId, task }: TaskModalProps) {
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [titleError, setTitleError] = useState<string | null>(null);
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();

  const isEditing = Boolean(task);
  const isPending = createTask.isPending || updateTask.isPending;

  useEffect(() => {
    if (open) {
      setForm(
        task
          ? {
              title: task.title,
              description: task.description ?? "",
              status: task.status,
              priority: task.priority,
              due_date: task.due_date ?? "",
            }
          : EMPTY_FORM,
      );
      setTitleError(null);
    }
  }, [open, task]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const title = form.title.trim();
    if (!title) {
      setTitleError("Title is required");
      return;
    }

    const payload = {
      title,
      description: form.description.trim() || null,
      status: form.status,
      priority: form.priority,
      due_date: form.due_date || null,
    };

    if (isEditing && task) {
      updateTask.mutate({ id: task.id, input: payload }, { onSuccess: onClose });
    } else if (listId !== null) {
      createTask.mutate({ list_id: listId, ...payload }, { onSuccess: onClose });
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <Stack component="form" onSubmit={handleSubmit} noValidate>
        <DialogTitle>{isEditing ? "Edit task" : "New task"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 0.5 }}>
            <TextField
              label="Title"
              value={form.title}
              onChange={(e) => {
                setForm((f) => ({ ...f, title: e.target.value }));
                if (titleError) setTitleError(null);
              }}
              error={Boolean(titleError)}
              helperText={titleError ?? " "}
              autoFocus
              required
              fullWidth
            />
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              multiline
              minRows={3}
              fullWidth
            />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField
                select
                label="Status"
                value={form.status}
                onChange={(e) => setForm((f) => ({ ...f, status: e.target.value as TaskStatus }))}
                fullWidth
              >
                <MenuItem value="todo">To Do</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="done">Done</MenuItem>
              </TextField>
              <TextField
                select
                label="Priority"
                value={form.priority}
                onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value as TaskPriority }))}
                fullWidth
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </TextField>
              <TextField
                label="Due date"
                type="date"
                value={form.due_date}
                onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2.5 }}>
          <Button onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isPending}>
            {isEditing ? "Save changes" : "Create task"}
          </Button>
        </DialogActions>
      </Stack>
    </Dialog>
  );
}
