"""initial schema: users, lists, tasks

Revision ID: 0001
Revises:
Create Date: 2026-08-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_status = sa.Enum("todo", "in_progress", "done", name="task_status")
task_priority = sa.Enum("low", "medium", "high", name="task_priority")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("provider_user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_user_provider_identity"),
    )

    op.create_table(
        "lists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lists_user_id", "lists", ["user_id"])

    # task_status/task_priority are created implicitly by create_table below
    # (SQLAlchemy emits CREATE TYPE for Enum columns automatically); creating
    # them explicitly here as well would raise "type already exists".
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("list_id", sa.Integer(), sa.ForeignKey("lists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status, nullable=False, server_default="todo"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("priority", task_priority, nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tasks_list_id", "tasks", ["list_id"])
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"])


def downgrade() -> None:
    op.drop_table("tasks")
    task_priority.drop(op.get_bind(), checkfirst=True)
    task_status.drop(op.get_bind(), checkfirst=True)
    op.drop_index("ix_lists_user_id", table_name="lists")
    op.drop_table("lists")
    op.drop_table("users")
