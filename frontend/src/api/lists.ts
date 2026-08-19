import { apiClient } from "./client";
import type { ListProject } from "../types";

export const fetchLists = () => apiClient.get<ListProject[]>("/api/lists");

export const createList = (name: string) => apiClient.post<ListProject>("/api/lists", { name });

export const renameList = (id: number, name: string) => apiClient.patch<ListProject>(`/api/lists/${id}`, { name });

export const deleteList = (id: number) => apiClient.delete<void>(`/api/lists/${id}`);
