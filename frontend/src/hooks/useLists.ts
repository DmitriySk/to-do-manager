import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createList, deleteList, fetchLists, renameList } from "../api/lists";

export const listsQueryKey = ["lists"] as const;

export function useLists() {
  return useQuery({ queryKey: listsQueryKey, queryFn: fetchLists });
}

export function useCreateList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => createList(name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: listsQueryKey }),
  });
}

export function useRenameList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => renameList(id, name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: listsQueryKey }),
  });
}

export function useDeleteList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteList(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: listsQueryKey });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}
