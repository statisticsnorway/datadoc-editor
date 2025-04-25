"""Smoke tests."""

from datadoc_editor import state
from datadoc_editor.app import get_app


def test_get_app(
    subject_mapping_fake_statistical_structure,
    code_list_fake_structure,
    thread_pool_executor,
):
    state.statistic_subject_mapping = subject_mapping_fake_statistical_structure
    state.code_list = code_list_fake_structure

    app, _ = get_app(thread_pool_executor)
    assert app.config["name"] == "Datadoc"
    assert len(app.callback_map.items()) > 0
