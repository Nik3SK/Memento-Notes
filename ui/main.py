from datetime import datetime
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.config import load_settings
from ui.api_client import MementoApiClient, MementoApiError


st.set_page_config(
    page_title="Memento Notes",
    page_icon="M",
    layout="wide",
)


def parse_tags(value: str) -> list[str]:
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def format_timestamp(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


settings = load_settings()
client = MementoApiClient(settings.api_base_url)

st.title("Memento Notes")
st.caption("Minimal local notes workspace")

try:
    client.health()
except MementoApiError as error:
    st.error(f"API is unavailable: {error}")
    st.stop()
    raise SystemExit(1)

if "selected_note_id" not in st.session_state:
    st.session_state.selected_note_id = None

with st.sidebar:
    st.subheader("Filters")
    search_query = st.text_input("Search", placeholder="Title, text, or tag")

    try:
        tags = client.list_tags()
    except MementoApiError as error:
        st.error(str(error))
        tags = []

    tag_options = ["All tags", *tags]
    selected_tag = st.selectbox("Tag", tag_options)
    active_tag = None if selected_tag == "All tags" else selected_tag

    st.divider()
    st.subheader("New note")
    with st.form("create-note", clear_on_submit=True):
        new_title = st.text_input("Title")
        new_content = st.text_area("Content", height=160)
        new_tags = st.text_input("Tags", placeholder="work, ideas")
        create_submitted = st.form_submit_button("Create")

    if create_submitted:
        try:
            note = client.create_note(new_title, new_content, parse_tags(new_tags))
            st.session_state.selected_note_id = note["id"]
            st.rerun()
        except MementoApiError as error:
            st.error(str(error))

try:
    if search_query.strip():
        notes = client.search_notes(search_query)
        if active_tag:
            notes = [note for note in notes if active_tag in note["tags"]]
    else:
        notes = client.list_notes(tag=active_tag)
except MementoApiError as error:
    st.error(str(error))
    st.stop()

if notes and st.session_state.selected_note_id not in {note["id"] for note in notes}:
    st.session_state.selected_note_id = notes[0]["id"]

list_column, editor_column = st.columns([0.36, 0.64], gap="large")

with list_column:
    st.subheader("Notes")
    if not notes:
        st.info("No notes found.")
    for note in notes:
        is_selected = note["id"] == st.session_state.selected_note_id
        label = note["title"] or "Untitled"
        if st.button(label, key=f"select-{note['id']}", use_container_width=True):
            st.session_state.selected_note_id = note["id"]
            st.rerun()
        caption_parts = [format_timestamp(note["updated_at"])]
        if note["tags"]:
            caption_parts.append(", ".join(note["tags"]))
        if is_selected:
            caption_parts.append("selected")
        st.caption(" | ".join(part for part in caption_parts if part))

selected_note = next(
    (note for note in notes if note["id"] == st.session_state.selected_note_id),
    None,
)

with editor_column:
    if selected_note is None:
        st.subheader("Select or create a note")
        st.write("Your note editor will appear here.")
    else:
        st.subheader("Editor")
        with st.form(f"edit-note-{selected_note['id']}"):
            title = st.text_input("Title", value=selected_note["title"])
            content = st.text_area("Content", value=selected_note["content"], height=360)
            tags_value = ", ".join(selected_note["tags"])
            tags_input = st.text_input("Tags", value=tags_value)
            confirm_delete = st.checkbox("Confirm delete")

            save_column, delete_column = st.columns([0.72, 0.28])
            save_submitted = save_column.form_submit_button("Save")
            delete_submitted = delete_column.form_submit_button("Delete")

        if save_submitted:
            try:
                updated_note = client.update_note(
                    selected_note["id"],
                    title,
                    content,
                    parse_tags(tags_input),
                )
                st.session_state.selected_note_id = updated_note["id"]
                st.rerun()
            except MementoApiError as error:
                st.error(str(error))

        if delete_submitted:
            if not confirm_delete:
                st.warning("Confirm delete before removing the note.")
                st.stop()
            try:
                client.delete_note(selected_note["id"])
                st.session_state.selected_note_id = None
                st.rerun()
            except MementoApiError as error:
                st.error(str(error))
