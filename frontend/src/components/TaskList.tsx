import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import SearchOffIcon from "@mui/icons-material/SearchOff";
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Stack } from "@mui/material";
import { useState } from "react";

import { useDeleteTask, useTasks, useUpdateTask } from "../hooks/useTasks";
import type { Task, TaskFilters, TaskStatus } from "../types";
import EmptyState from "./EmptyState";
import LoadingSpinner from "./LoadingSpinner";
import TaskItem from "./TaskItem";
import TaskModal from "./TaskModal";

interface TaskListProps {
  filters: TaskFilters;
  hasActiveFilters: boolean;
  editingTask: Task | null;
  onEditingTaskChange: (task: Task | null) => void;
  createOpen: boolean;
  onCreateOpenChange: (open: boolean) => void;
}

export default function TaskList({
  filters,
  hasActiveFilters,
  editingTask,
  onEditingTaskChange,
  createOpen,
  onCreateOpenChange,
}: TaskListProps) {
  const { data: tasks, isLoading } = useTasks(filters);
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();
  const [taskPendingDelete, setTaskPendingDelete] = useState<Task | null>(null);

  return (
    <>
      {isLoading && <LoadingSpinner label="Loading tasks" />}

      {!isLoading && (!tasks || tasks.length === 0) && (
        <EmptyState
          icon={hasActiveFilters ? <SearchOffIcon sx={{ fontSize: 40, opacity: 0.4 }} /> : <AssignmentTurnedInIcon sx={{ fontSize: 40, opacity: 0.4 }} />}
          title={hasActiveFilters ? "No tasks match your search" : "No tasks yet"}
          description={
            hasActiveFilters
              ? "Try a different search term or clear your filters."
              : "Create a task to start planning your work."
          }
        />
      )}

      {!isLoading && tasks && tasks.length > 0 && (
        <Stack spacing={1.5} sx={{ p: { xs: 2, md: 3 }, pt: 0 }}>
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onEdit={() => onEditingTaskChange(task)}
              onDelete={() => setTaskPendingDelete(task)}
              onStatusChange={(status: TaskStatus) => updateTask.mutate({ id: task.id, input: { status } })}
            />
          ))}
        </Stack>
      )}

      <TaskModal
        open={createOpen}
        onClose={() => onCreateOpenChange(false)}
        listId={filters.list_id ?? null}
      />
      <TaskModal
        open={editingTask !== null}
        onClose={() => onEditingTaskChange(null)}
        listId={editingTask?.list_id ?? null}
        task={editingTask}
      />

      <Dialog open={taskPendingDelete !== null} onClose={() => setTaskPendingDelete(null)}>
        <DialogTitle>Delete "{taskPendingDelete?.title}"?</DialogTitle>
        <DialogContent>
          <DialogContentText>This can't be undone.</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTaskPendingDelete(null)}>Cancel</Button>
          <Button
            color="error"
            variant="contained"
            onClick={() => {
              if (taskPendingDelete) deleteTask.mutate(taskPendingDelete.id);
              setTaskPendingDelete(null);
            }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
