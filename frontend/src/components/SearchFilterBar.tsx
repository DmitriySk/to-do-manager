import SearchIcon from "@mui/icons-material/Search";
import { InputAdornment, MenuItem, Stack, TextField } from "@mui/material";
import { useEffect, useState } from "react";

import type { DueCategory, TaskPriority, TaskStatus } from "../types";

export interface TaskFilterState {
  q: string;
  status: TaskStatus | "all";
  priority: TaskPriority | "all";
  due_category: DueCategory;
}

interface SearchFilterBarProps {
  value: TaskFilterState;
  onChange: (value: TaskFilterState) => void;
}

export default function SearchFilterBar({ value, onChange }: SearchFilterBarProps) {
  const [searchInput, setSearchInput] = useState(value.q);

  useEffect(() => {
    const handle = setTimeout(() => {
      if (searchInput !== value.q) {
        onChange({ ...value, q: searchInput });
      }
    }, 300);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  return (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} sx={{ mb: 2 }}>
      <TextField
        size="small"
        placeholder="Search title or description…"
        value={searchInput}
        onChange={(e) => setSearchInput(e.target.value)}
        sx={{ flex: 1, minWidth: 220 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon fontSize="small" />
            </InputAdornment>
          ),
        }}
        inputProps={{ "aria-label": "Search tasks" }}
      />

      <TextField
        size="small"
        select
        label="Status"
        value={value.status}
        onChange={(e) => onChange({ ...value, status: e.target.value as TaskFilterState["status"] })}
        sx={{ minWidth: 150 }}
      >
        <MenuItem value="all">All statuses</MenuItem>
        <MenuItem value="todo">To Do</MenuItem>
        <MenuItem value="in_progress">In Progress</MenuItem>
        <MenuItem value="done">Done</MenuItem>
      </TextField>

      <TextField
        size="small"
        select
        label="Priority"
        value={value.priority}
        onChange={(e) => onChange({ ...value, priority: e.target.value as TaskFilterState["priority"] })}
        sx={{ minWidth: 150 }}
      >
        <MenuItem value="all">All priorities</MenuItem>
        <MenuItem value="low">Low</MenuItem>
        <MenuItem value="medium">Medium</MenuItem>
        <MenuItem value="high">High</MenuItem>
      </TextField>

      <TextField
        size="small"
        select
        label="Due"
        value={value.due_category}
        onChange={(e) => onChange({ ...value, due_category: e.target.value as DueCategory })}
        sx={{ minWidth: 150 }}
      >
        <MenuItem value="all">Any time</MenuItem>
        <MenuItem value="overdue">Overdue</MenuItem>
        <MenuItem value="today">Today</MenuItem>
        <MenuItem value="next_7_days">Next 7 days</MenuItem>
      </TextField>
    </Stack>
  );
}
