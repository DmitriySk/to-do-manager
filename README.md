Personal To-Do Manager 
Task: Create a full-stack web app using Claude Code. 
Goal: Deliver a working MVP that demonstrates end-to-end product implementation (frontend + backend + persistence + tests) with Claude Code assistance. Developer chooses stack, database, UI library, and hosting approach (local run is required) 
Business scenario: A user manages personal work across multiple projects and wants a simple system to plan tasks, set priorities and deadlines, and quickly see what requires attention today and this week. 
 
1) Core rules 
The system supports multiple users 
Each user sees only their own data 
There is no sharing of any kind (no invites, no public links, no shared lists) 
 
2) Functional requirements 
2.1 Authentication and accounts (SSO only) 
User authentication must be implemented via SSO 
The app must support both providers 
Google OAuth (OpenID Connect) 
GitHub OAuth 
The app must support logout 
A logged-in user must stay authenticated across page refresh (session or token based) 
The backend must persist a user profile minimally containing 
provider (google or github) 
provider_user_id 
email (if provided by the provider) 
display_name 
avatar_url (optional) 
 
2.2 Lists / Projects 
A user can create a list/project 
A user can rename a list/project 
A user can delete a list/project 
Deleting a list/project must be handled by one approach and documented in README 
Cascade delete all tasks in the list 
Block deletion until tasks are removed 
2.3 Tasks 
Each task belongs to exactly one list/project and includes the following fields 
Title 
Description/notes 
Status: To Do, In Progress, Done 
Due date 
Priority: Low, Medium, High 
Task operations 
Create a task in a selected list 
Edit any task fields 
Delete a task 
Change status quickly from the task list view 
2.4 Search and filters 
Search tasks by title and description 
Filter tasks by status 
Filter tasks by priority 
Filter tasks by due date category: overdue, today, next 7 days, all 
 
      2.5 Real-time communication (WebSocket notifications) 
      The app must include two-way communication using WebSocket 
      Server → client notifications 
When the user is connected, the backend must push task notifications over WebSocket 
Notification types must include at least 
Overdue tasks (status is not Done and due date is before today) 
Due soon tasks (status is not Done and due date is within the next 3 days, inclusive) 
The client must display notifications in the UI (toast, banner, or a notification panel) 
Client → server messages (required to make it truly two-way) 
The client must send at least one meaningful WebSocket message, for example 
subscribe message after connection with user preferences like interval or enabled types 
ack message to mark a notification as read 
The chosen message(s) must be documented in README together with the message format 
Scheduling rule 
On WebSocket connect, server sends an initial notification batch 
While connected, server repeats the check periodically (developer chooses interval and documents it) 
 
3) UI requirements  (modern, styled, responsive, interactive) 
Authentication screen includes “Continue with Google” and “Continue with GitHub” 
Main layout with a left area for lists/projects and a main area for tasks 
Task list view for the selected list 
Task create and edit UI (modal, drawer, or separate page is acceptable) 
Search input and filter controls accessible from the task list view 
Notifications UI visible while connected to WebSocket 
Responsive behavior for narrow screens (sidebar collapses or becomes a menu) 
To make “modern and styled” checkable, the UI must include 
Consistent spacing and typography across screens 
Visible hover and focus states for interactive elements 
Clear empty states for lists with no tasks and for search with no results 
Loading state for at least one main screen or data block 
Client-side form validation feedback for task create/edit 
 
4) Backend requirements 
Provide a REST API (or equivalent HTTP API) that supports the UI flows 
Enforce authorization on every list/task operation 
Enforce authorization on WebSocket connections and notifications 
Validate inputs and return clear errors for invalid requests 
Implement SSO OAuth flows securely and document environment variables required for Google and GitHub providers 
 
5) Data requirements 
Persist data in a database chosen by the developer 
Provide a simple way to start with sample data (seed script or “create sample data” endpoint or documented manual steps) 
 
6) Quality requirements 
Automated tests must cover at least these cases 
SSO login success path in test mode using a mock or stub provider response 
A user can create a list and a task 
A user cannot access another user’s list/tasks (authorization test) 
WebSocket notifications are sent for overdue or due soon tasks (can be tested via an in-memory WS client or mocked clock) 
 
7) Deliverables 
Source code in a GitLab repository 
README with local run instructions for backend and frontend 
README section describing 
how to configure Google OAuth credentials 
how to configure GitHub OAuth credentials 
WebSocket message formats and notification rules 
Short API description (OpenAPI, Postman collection, or README section) 
Test command documented and runnable 
Optional deliverable 
Containerization (Dockerfile and or docker-compose) 
If containerization is not possible on the developer machine, it can be skipped and noted in README 
 
8)  Acceptance checklist 
A new user can log in with Google and GitHub 
A user can create lists, create tasks, and use search/filters 
Data is private per user and cannot be accessed cross-account 
While connected, the app receives real-time notifications for overdue and due soon tasks 
The WebSocket flow includes at least one client→server message that changes server behavior (subscribe or ack) 
Tests pass locally 
README is sufficient for another developer to run the app without guessing

