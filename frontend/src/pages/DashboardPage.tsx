import AddIcon from "@mui/icons-material/Add";
import { Box, Button, Stack, Tooltip, Typography } from "@mui/material";
import { useMemo, useState } from "react";

import Layout from "../components/Layout";
import SearchFilterBar, { type TaskFilterState } from "../components/SearchFilterBar";
import TaskList from "../components/TaskList";
import { useLists } from "../hooks/useLists";
import { useWebSocket } from "../hooks/useWebSocket";
import type { Task, TaskFilters } from "../types";

const DEFAULT_FILTER_STATE: TaskFilterState = { q: "", status: "all", priority: "all", due_category: "all" };

export default function DashboardPage() {
  const [selectedListId, setSelectedListId] = useState<number | null>(null);
  const [filterState, setFilterState] = useState<TaskFilterState>(DEFAULT_FILTER_STATE);
  const [createOpen, setCreateOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const { data: lists } = useLists();
  const { notifications, sendAck } = useWebSocket();

  const selectedList = lists?.find((l) => l.id === selectedListId) ?? null;

  const filters: TaskFilters = useMemo(
    () => ({
      list_id: selectedListId ?? undefined,
      status: filterState.status === "all" ? undefined : filterState.status,
      priority: filterState.priority === "all" ? undefined : filterState.priority,
      due_category: filterState.due_category === "all" ? undefined : filterState.due_category,
      q: filterState.q || undefined,
    }),
    [selectedListId, filterState],
  );

  const hasActiveFilters = Boolean(filters.status || filters.priority || filters.due_category || filters.q);

  return (
    <Layout
      selectedListId={selectedListId}
      onSelectList={setSelectedListId}
      notifications={notifications}
      onAckNotification={sendAck}
    >
      <Box sx={{ px: { xs: 2, md: 3 }, pt: 2.5 }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
          <Typography variant="h5" fontWeight={700}>
            {selectedList ? selectedList.name : "All tasks"}
          </Typography>
          <Tooltip title={selectedListId === null ? "Select a list to add a task" : ""}>
            <span>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateOpen(true)}
                disabled={selectedListId === null}
              >
                New task
              </Button>
            </span>
          </Tooltip>
        </Stack>

        <SearchFilterBar value={filterState} onChange={setFilterState} />
      </Box>

      <TaskList
        filters={filters}
        hasActiveFilters={hasActiveFilters}
        editingTask={editingTask}
        onEditingTaskChange={setEditingTask}
        createOpen={createOpen}
        onCreateOpenChange={setCreateOpen}
      />
    </Layout>
  );
}
