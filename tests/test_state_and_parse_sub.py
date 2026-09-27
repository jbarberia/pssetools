import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pssetools"))

from state import ApplicationState, WorkspaceState
from utils import parse_sub


def test_workspace_state_ensure_workspace_exists_creates_paths_and_changes_cwd(tmp_path):
    workdir = tmp_path / "work"
    output_dir = tmp_path / "output"
    temp_dir = tmp_path / "temp"
    workdir.mkdir()

    state = WorkspaceState()
    state.working_dir = str(workdir)
    state.output_dir = str(output_dir)
    state.temp_dir = str(temp_dir)

    state.ensure_workspace_exists()

    assert output_dir.exists()
    assert temp_dir.exists()
    assert str(tmp_path / "work") == str(workdir)


def test_application_state_save_and_load_roundtrip(tmp_path):
    config_file = tmp_path / "state.json"

    state = ApplicationState()
    state.workspace.working_dir = str(tmp_path / "working")
    state.programs = {"my_program": {"key": "value"}}
    state.ui.last_program = "my_program"
    state.save(str(config_file))

    loaded = ApplicationState()
    assert loaded.load(str(config_file)) is True

    assert loaded.workspace.working_dir == str(tmp_path / "working")
    assert loaded.programs == {"my_program": {"key": "value"}}
    assert loaded.ui.last_program == "my_program"


def test_application_state_load_returns_false_for_missing_or_invalid_file(tmp_path):
    missing = tmp_path / "missing.json"
    assert ApplicationState().load(str(missing)) is False

    invalid = tmp_path / "invalid.json"
    invalid.write_text("{not-json}", encoding="utf-8")
    assert ApplicationState().load(str(invalid)) is False


def test_remove_comments_strips_only_com_lines():
    content = "LINE1\n COM this is a comment\nLINE2\nCOM and another\n"

    cleaned = parse_sub.remove_comments(content)

    assert cleaned == "LINE1\nLINE2"


def test_parse_buses_respects_ranges_and_skip(monkeypatch):
    buses = [
        parse_sub.Bus(100, 1, 1, 1, 132.0),
        parse_sub.Bus(201, 1, 1, 1, 132.0),
        parse_sub.Bus(202, 1, 1, 1, 132.0),
        parse_sub.Bus(203, 1, 1, 1, 132.0),
        parse_sub.Bus(300, 1, 1, 1, 132.0),
    ]
    monkeypatch.setattr(parse_sub, "extract_buses", lambda only_in_service=True: buses)

    block = "BUS 100\nBUSES 200 204\n SKIP BUS 202"
    assert parse_sub.parse_buses(block) == {100, 201, 203}


def test_parse_area_owner_zone_and_kv_filters(monkeypatch):
    buses = [
        parse_sub.Bus(1, 1, 10, 100, 132.0),
        parse_sub.Bus(2, 2, 11, 101, 220.0),
        parse_sub.Bus(3, 3, 12, 102, 500.0),
    ]
    monkeypatch.setattr(parse_sub, "extract_buses", lambda only_in_service=True: buses)

    assert parse_sub.parse_areas("AREAS 1 2") == {1, 2}
    assert parse_sub.parse_owners("OWNER 12") == {3}
    assert parse_sub.parse_zones("ZONES 100 101") == {1, 2}
    assert parse_sub.parse_kv("KV 220") == {2}
    assert parse_sub.parse_kv("KVRANGE 200 500") == {2, 3}


def test_parse_sub_reads_named_subsystem(monkeypatch, tmp_path):
    buses = [
        parse_sub.Bus(10, 1, 1, 1, 132.0),
        parse_sub.Bus(11, 1, 1, 1, 132.0),
    ]
    monkeypatch.setattr(parse_sub, "extract_buses", lambda only_in_service=True: buses)

    sub_file = tmp_path / "sample.sub"
    sub_file.write_text(
        """
COM ignore this
SUBSYSTEM 'TEST_SUB'
BUS 10
BUS 11
END
""".strip(),
        encoding="utf-8",
    )

    parsed = parse_sub.parse_sub(str(sub_file))

    assert set(parsed["TEST_SUB"]) == {10, 11}
