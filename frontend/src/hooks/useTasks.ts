import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createTask, deleteTask, fetchTasks, updateTask, type CreateTaskInput, type UpdateTaskInput } from "../api/tasks";
import type { TaskFilters } from "../types";
import { listsQueryKey } from "./useLists";

export function tasksQueryKey(filters: TaskFilters) {
  return ["tasks", filters] as const;
}

export function useTasks(filters: TaskFilters) {
  return useQuery({ queryKey: tasksQueryKey(filters), queryFn: () => fetchTasks(filters) });
}

function useInvalidateTasksAndLists() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: ["tasks"] });
    queryClient.invalidateQueries({ queryKey: listsQueryKey });
  };
}

export function useCreateTask() {
  const invalidate = useInvalidateTasksAndLists();
  return useMutation({
    mutationFn: (input: CreateTaskInput) => createTask(input),
    onSuccess: invalidate,
  });
}

export function useUpdateTask() {
  const invalidate = useInvalidateTasksAndLists();
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: UpdateTaskInput }) => updateTask(id, input),
    onSuccess: invalidate,
  });
}

export function useDeleteTask() {
  const invalidate = useInvalidateTasksAndLists();
  return useMutation({
    mutationFn: (id: number) => deleteTask(id),
    onSuccess: invalidate,
  });
}
