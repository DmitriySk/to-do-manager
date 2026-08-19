export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskPriority = "low" | "medium" | "high";
export type DueCategory = "overdue" | "today" | "next_7_days" | "all";

export interface User {
  id: number;
  provider: "google" | "github";
  email: string | null;
  display_name: string;
  avatar_url: string | null;
  created_at: string;
}

export interface ListProject {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  task_count: number;
}

export interface Task {
  id: number;
  list_id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  due_date: string | null;
  priority: TaskPriority;
  created_at: string;
  updated_at: string;
}

export interface TaskFilters {
  list_id?: number;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_category?: DueCategory;
  q?: string;
}

export interface NotificationItem {
  id: string;
  task_id: number;
  list_id: number;
  kind: "overdue" | "due_soon";
  title: string;
  due_date: string;
  priority: TaskPriority;
}

export interface NotificationBatchMessage {
  type: "notification_batch";
  generated_at: string;
  notifications: NotificationItem[];
}

export interface SubscribedMessage {
  type: "subscribed";
  interval_seconds: number;
  enabled_types: string[];
}

export type ServerMessage = NotificationBatchMessage | SubscribedMessage;
