import json
from datetime import datetime, date, time
from pathlib import Path

import streamlit as st

DATA_FILE = Path("assistant_tasks.json")


def load_tasks():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_tasks(tasks):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def add_task(description, due):
    tasks = load_tasks()
    next_id = max((t.get("id", 0) for t in tasks), default=0) + 1
    tasks.append({
        "id": next_id,
        "description": description.strip(),
        "due": due or "Not set",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_tasks(tasks)


def build_study_plan(subjects_text, total_minutes):
    subjects = [s.strip() for s in subjects_text.split(",") if s.strip()]
    if not subjects:
        return []
    base, extra = divmod(total_minutes, len(subjects))
    return [
        (subject, base + (1 if i < extra else 0))
        for i, subject in enumerate(subjects)
    ]


st.set_page_config(page_title="Personal Assistant Agent", page_icon="🤖", layout="centered")

st.title("🤖 Personal Assistant Agent")
st.caption("A simple task manager and study planner built with Python + Streamlit.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose a feature", ["Dashboard", "Add a task", "Study planner", "Manage tasks"])
    st.divider()
    st.caption("Beginner project • Python • Streamlit")

tasks = load_tasks()

if page == "Dashboard":
    st.subheader("Welcome!")
    col1, col2 = st.columns(2)
    col1.metric("Saved tasks", len(tasks))
    upcoming = sum(1 for t in tasks if t.get("due") and t["due"] != "Not set")
    col2.metric("Tasks with due dates", upcoming)

    st.markdown("### What I can do")
    st.write("- Add and view tasks")
    st.write("- Delete completed or unwanted tasks")
    st.write("- Split study time across subjects")

    st.markdown("### Recent tasks")
    if tasks:
        for task in sorted(tasks, key=lambda t: t.get("id", 0), reverse=True)[:5]:
            st.write(f"**#{task['id']} — {task['description']}**")
            st.caption(f"Due: {task.get('due', 'Not set')}")
    else:
        st.info("No tasks yet. Choose **Add a task** from the sidebar to get started.")

elif page == "Add a task":
    st.subheader("➕ Add a task")
    with st.form("add_task_form", clear_on_submit=True):
        description = st.text_input("Task description", placeholder="e.g. Complete Python assignment")
        set_due = st.checkbox("Add a due date and time")
        due_value = ""
        if set_due:
            due_date = st.date_input("Due date", value=date.today())
            due_time = st.time_input("Due time", value=time(18, 0))
            due_value = datetime.combine(due_date, due_time).strftime("%Y-%m-%d %H:%M")
        submitted = st.form_submit_button("Save task", type="primary")

    if submitted:
        if not description.strip():
            st.error("Please enter a task description.")
        else:
            add_task(description, due_value)
            st.success("Task saved!")
            st.rerun()

elif page == "Study planner":
    st.subheader("📚 Study planner")
    subjects_text = st.text_input(
        "Subjects (separate them with commas)",
        placeholder="Python, Mathematics, Machine Learning",
    )
    total_minutes = st.slider("Available study time (minutes)", min_value=15, max_value=480, value=60, step=15)
    if st.button("Create study plan", type="primary"):
        plan = build_study_plan(subjects_text, total_minutes)
        if not plan:
            st.error("Enter at least one subject.")
        else:
            st.success("Your study plan is ready.")
            for subject, minutes in plan:
                st.write(f"- **{subject}:** {minutes} minutes")
            st.caption(f"Total planned time: {sum(m for _, m in plan)} minutes")

elif page == "Manage tasks":
    st.subheader("🗂️ Manage tasks")
    tasks = load_tasks()
    if not tasks:
        st.info("No tasks to manage yet.")
    else:
        for task in tasks:
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"**#{task['id']} — {task['description']}**")
                st.caption(f"Due: {task.get('due', 'Not set')}")
            with right:
                if st.button("Delete", key=f"delete_{task['id']}"):
                    tasks = [t for t in tasks if t.get("id") != task["id"]]
                    save_tasks(tasks)
                    st.rerun()
            st.divider()

st.caption("Note: This demo stores tasks in a local JSON file. On hosted cloud services, local files may not be permanent across restarts or rebuilds. Use a database for reliable long-term storage.")
