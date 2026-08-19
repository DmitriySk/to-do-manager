import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import EditIcon from "@mui/icons-material/Edit";
import { Box, Card, Chip, IconButton, MenuItem, Stack, TextField, Typography } from "@mui/material";

import type { Task, TaskStatus } from "../types";

interface TaskItemProps {
  task: Task;
  onEdit: () => void;
  onDelete: () => void;
  onStatusChange: (status: TaskStatus) => void;
}

const PRIORITY_COLOR: Record<Task["priority"], "default" | "warning" | "error"> = {
  low: "default",
  medium: "warning",
  high: "error",
};

function dueDateMeta(task: Task): { label: string; color: "text.secondary" | "error.main" | "warning.main" } {
  if (!task.due_date) return { label: "No due date", color: "text.secondary" };
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(`${task.due_date}T00:00:00`);
  const diffDays = Math.round((due.getTime() - today.getTime()) / 86_400_000);

  if (task.status !== "done" && diffDays < 0) return { label: `Overdue · ${task.due_date}`, color: "error.main" };
  if (task.status !== "done" && diffDays <= 3) return { label: `Due soon · ${task.due_date}`, color: "warning.main" };
  return { label: `Due ${task.due_date}`, color: "text.secondary" };
}

export default function TaskItem({ task, onEdit, onDelete, onStatusChange }: TaskItemProps) {
  const due = dueDateMeta(task);

  return (
    <Card
      variant="outlined"
      sx={{
        p: 2,
        display: "flex",
        alignItems: "flex-start",
        gap: 2,
        "&:hover .task-actions": { opacity: 1 },
        "&:focus-within .task-actions": { opacity: 1 },
      }}
    >
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
          <Typography
            variant="subtitle1"
            fontWeight={600}
            sx={{ textDecoration: task.status === "done" ? "line-through" : "none", color: task.status === "done" ? "text.secondary" : "text.primary" }}
          >
            {task.title}
          </Typography>
          <Chip label={task.priority} color={PRIORITY_COLOR[task.priority]} size="small" sx={{ textTransform: "capitalize" }} />
        </Stack>
        {task.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, whiteSpace: "pre-wrap" }}>
            {task.description}
          </Typography>
        )}
        <Typography variant="caption" sx={{ color: due.color, fontWeight: 500 }}>
          {due.label}
        </Typography>
      </Box>

      <TextField
        select
        size="small"
        value={task.status}
        onChange={(e) => onStatusChange(e.target.value as TaskStatus)}
        aria-label={`Change status for ${task.title}`}
        sx={{ minWidth: 140 }}
      >
        <MenuItem value="todo">To Do</MenuItem>
        <MenuItem value="in_progress">In Progress</MenuItem>
        <MenuItem value="done">Done</MenuItem>
      </TextField>

      <Stack direction="row" className="task-actions" sx={{ opacity: 0, transition: "opacity 0.15s" }}>
        <IconButton size="small" aria-label={`Edit ${task.title}`} onClick={onEdit}>
          <EditIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" aria-label={`Delete ${task.title}`} onClick={onDelete}>
          <DeleteOutlineIcon fontSize="small" />
        </IconButton>
      </Stack>
    </Card>
  );
}
