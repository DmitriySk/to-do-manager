-- Runs once when the postgres container's data volume is first created.
-- POSTGRES_DB already creates the main "todo" database; this adds the
-- separate database used only by the backend's automated test suite.
CREATE DATABASE todo_test OWNER todo;
