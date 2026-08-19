import { apiClient } from "./client";
import type { Task, TaskFilters, TaskPriority, TaskStatus } from "../types";

function toQueryString(filters: TaskFilters): string {
  const params = new URLSearchParams();
  if (filters.list_id !== undefined) params.set("list_id", String(filters.list_id));
  if (filters.status) params.set("status", filters.status);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.due_category) params.set("due_category", filters.due_category);
  if (filters.q) params.set("q", filters.q);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const fetchTasks = (filters: TaskFilters) => apiClient.get<Task[]>(`/api/tasks${toQueryString(filters)}`);

export interface CreateTaskInput {
  list_id: number;
  title: string;
  description?: string | null;
  status?: TaskStatus;
  due_date?: string | null;
  priority?: TaskPriority;
}

export const createTask = (input: CreateTaskInput) => apiClient.post<Task>("/api/tasks", input);

export interface UpdateTaskInput {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  due_date?: string | null;
  priority?: TaskPriority;
  clear_due_date?: boolean;
}

export const updateTask = (id: number, input: UpdateTaskInput) => apiClient.patch<Task>(`/api/tasks/${id}`, input);

export const deleteTask = (id: number) => apiClient.delete<void>(`/api/tasks/${id}`);

export const seedSampleData = () => apiClient.post<{ lists_created: number; tasks_created: number }>("/api/dev/seed");
