"""Persistent, per-chat-thread task management tool."""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from typing import Optional

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


_DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatbot.db")


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(_DATABASE_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 15000")
    return connection


def _initialize_database() -> None:
    with closing(_connect()) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                task TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_tasks_thread "
            "ON chat_tasks(thread_id, completed, id)"
        )


_initialize_database()


@tool
def manage_tasks(
    action: str,
    task: Optional[str] = None,
    task_id: Optional[int] = None,
    config: RunnableConfig = None,
) -> dict:
    """Manage tasks saved for the current chat. Actions: add, list, complete, delete.

    Use add with a task description; list to show saved tasks; complete or
    delete with the numeric task_id shown by list. Tasks are scoped to this
    conversation thread and persist in the local SQLite database.
    """
    configurable = (config or {}).get("configurable", {})
    thread_id = configurable.get("thread_id")
    if thread_id is None:
        return {"error": "This task tool needs a conversation thread ID."}
    thread_id = str(thread_id)
    action = action.strip().lower()

    if action == "add":
        if not task or not task.strip():
            return {"error": "Provide a non-empty task description."}
        task_text = task.strip()
        if len(task_text) > 500:
            return {"error": "Task descriptions must be 500 characters or fewer."}
        with closing(_connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT INTO chat_tasks (thread_id, task) VALUES (?, ?)",
                (thread_id, task_text),
            )
            return {"status": "added", "task_id": cursor.lastrowid, "task": task_text}

    if action == "list":
        with closing(_connect()) as connection, connection:
            rows = connection.execute(
                "SELECT id, task, created_at, completed FROM chat_tasks "
                "WHERE thread_id = ? ORDER BY completed, id",
                (thread_id,),
            ).fetchall()
        return {"tasks": [dict(row) for row in rows], "count": len(rows)}

    if action in {"complete", "delete"}:
        if task_id is None:
            return {"error": f"Provide the task_id to {action} a task."}
        with closing(_connect()) as connection, connection:
            if action == "complete":
                cursor = connection.execute(
                    "UPDATE chat_tasks SET completed = 1 "
                    "WHERE id = ? AND thread_id = ?",
                    (task_id, thread_id),
                )
            else:
                cursor = connection.execute(
                    "DELETE FROM chat_tasks WHERE id = ? AND thread_id = ?",
                    (task_id, thread_id),
                )
        if cursor.rowcount == 0:
            return {"error": "Task not found in this conversation."}
        return {"status": "completed" if action == "complete" else "deleted", "task_id": task_id}

    return {"error": "Unsupported action. Choose add, list, complete, or delete."}
