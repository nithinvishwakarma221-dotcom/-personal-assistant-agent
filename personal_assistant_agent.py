import json
import re
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("assistant_tasks.json")


def load_tasks():
    """Load saved tasks from a JSON file."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read saved tasks. Starting with an empty list.")
        return []


def save_tasks(tasks):
    """Save tasks to a JSON file."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4, ensure_ascii=False)


def add_task(tasks, description=None, due=None):
    """Add a task, asking for details when they were not supplied."""
    if not description:
        description = input("What do you need to do? ").strip()

    if not description:
        return "Task was not added because the description is empty."

    if not due:
        due = input("When? (e.g. 2026-11-01 18:00, or leave blank): ").strip()

    if due:
        try:
            datetime.strptime(due, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Please use the date/time format YYYY-MM-DD HH:MM. Task not added."

    task = {
        "id": max((item.get("id", 0) for item in tasks), default=0) + 1,
        "description": description,
        "due": due or "Not set",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tasks.append(task)
    save_tasks(tasks)
    return f"Added task #{task['id']}: {description} | Due: {task['due']}"


def view_tasks(tasks):
    """Show all saved tasks."""
    if not tasks:
        return "You have no saved tasks yet."

    lines = ["Your tasks:"]
    for task in tasks:
        lines.append(
            f"  #{task.get('id', '?')} — {task.get('description', '(no description)')} "
            f"| Due: {task.get('due', 'Not set')}"
        )
    return "\n".join(lines)


def delete_task(tasks, task_id=None):
    """Delete a task by its ID."""
    if task_id is None:
        raw_id = input("Enter the task ID to delete: ").strip()
        if not raw_id.isdigit():
            return "Please enter a numeric task ID."
        task_id = int(raw_id)

    for index, task in enumerate(tasks):
        if task.get("id") == task_id:
            removed = tasks.pop(index)
            save_tasks(tasks)
            return f"Deleted task #{task_id}: {removed.get('description', '')}"

    return f"I couldn't find task #{task_id}."


def study_plan():
    """Create a simple study plan from subjects and available study time."""
    subjects_text = input("Enter subjects separated by commas: ").strip()
    if not subjects_text:
        return "No subjects entered."

    subjects = [subject.strip() for subject in subjects_text.split(",") if subject.strip()]
    minutes_text = input("How many minutes can you study today? ").strip()

    if not minutes_text.isdigit() or int(minutes_text) <= 0:
        return "Please enter a positive number of minutes."

    total_minutes = int(minutes_text)
    base, extra = divmod(total_minutes, len(subjects))

    lines = ["Your study plan:"]
    for index, subject in enumerate(subjects):
        minutes = base + (1 if index < extra else 0)
        lines.append(f"  {index + 1}. {subject}: {minutes} minutes")
    lines.append(f"Total: {total_minutes} minutes")
    return "\n".join(lines)


def show_help():
    return (
        "I can help with these commands:\n"
        "  add task            - create a task\n"
        "  show tasks          - list saved tasks\n"
        "  delete task         - remove a task by ID\n"
        "  study plan          - divide study time across subjects\n"
        "  help                - show commands\n"
        "  exit                - close the assistant\n\n"
        "Examples: 'add task', 'show tasks', 'study plan'"
    )


def personal_assistant(user_message, tasks):
    """Basic rule-based agent: interpret a message and choose an action."""
    message = user_message.lower().strip()

    if message in {"exit", "quit", "bye"}:
        return "Goodbye! Your saved tasks will still be here next time."

    if message in {"help", "commands"} or "what can you do" in message:
        return show_help()

    if any(word in message for word in ("show tasks", "view tasks", "list tasks", "my tasks")):
        return view_tasks(tasks)

    if "delete task" in message or "remove task" in message:
        match = re.search(r"(?:delete|remove)\s+task\s+#?(\d+)", message)
        task_id = int(match.group(1)) if match else None
        return delete_task(tasks, task_id)

    if "study plan" in message or "study schedule" in message:
        return study_plan()

    if message == "add task" or message.startswith("add task "):
        description = message[len("add task"):].strip(" :-")
        return add_task(tasks, description or None)

    if any(word in message for word in ("schedule", "remind", "task", "todo", "to-do")):
        print("I think you want to add a task.")
        return add_task(tasks)

    return (
        "I'm not sure what you mean yet. Type 'help' to see what I can do.\n"
        "Tip: try 'add task', 'show tasks', or 'study plan'."
    )


def main():
    tasks = load_tasks()
    print("=" * 42)
    print("       PERSONAL ASSISTANT AGENT")
    print("=" * 42)
    print("Hello! I can manage tasks and help plan study time.")
    print("Type 'help' for commands or 'exit' to quit.")

    while True:
        try:
            user_message = input("\nYou: ").strip()
            if not user_message:
                continue

            response = personal_assistant(user_message, tasks)
            print(f"\nAssistant: {response}")

            if user_message.lower() in {"exit", "quit", "bye"}:
                break
        except (KeyboardInterrupt, EOFError):
            print("\nAssistant: Goodbye! Your saved tasks will still be here next time.")
            break
        except OSError as error:
            print(f"\nAssistant: A file operation failed: {error}")


if __name__ == "__main__":
    main()
