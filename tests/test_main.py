import pytest
import requests
from click.testing import CliRunner

from gi_tool import main


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
        self.ok = status_code < 400
        self.reason = "Not Found" if status_code == 404 else "OK"
        self.encoding = None


@pytest.fixture
def api(monkeypatch):
    """Replace requests.get; records requested URLs and serves canned responses."""
    calls = []
    responses = {}

    def fake_get(url, timeout=None, headers=None):
        assert timeout, "requests must always set a timeout"
        calls.append(url)
        path = url[len(main.API_URL):]
        return responses.get(path, FakeResponse("### Default ###\n*.tmp\n"))

    monkeypatch.setattr(main.requests, "get", fake_get)
    return calls, responses


def run(*args):
    return CliRunner().invoke(main.generate, list(args))


def test_prints_to_stdout(api):
    calls, _ = api
    result = run("Python", "node,python")
    assert result.exit_code == 0
    assert result.output == "### Default ###\n*.tmp\n"
    assert calls == [main.API_URL + "python,node"]


def test_requires_template(api):
    result = run()
    assert result.exit_code == 2
    assert "at least one template" in result.output


@pytest.mark.parametrize("name", ["../etc", "py?x=1", "a/b", "#frag", "py thon", "-x"])
def test_rejects_invalid_names(api, name):
    calls, _ = api
    result = run("--", name)
    assert result.exit_code == 2
    assert "invalid template name" in result.output
    assert calls == []


def test_unknown_template(api):
    _, responses = api
    responses["python,nope"] = FakeResponse(
        "#!! ERROR: nope is undefined. Use list command to see defined gitignore types !!#\n", 404
    )
    result = run("python", "nope")
    assert result.exit_code == 1
    assert "Unknown template(s): nope" in result.output


def test_http_error(api):
    _, responses = api
    responses["python"] = FakeResponse("Bad gateway", 502)
    result = run("python")
    assert result.exit_code == 1
    assert "HTTP 502" in result.output


def test_network_error(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.exceptions.ConnectionError("offline")

    monkeypatch.setattr(main.requests, "get", boom)
    result = run("python")
    assert result.exit_code == 1
    assert "Could not reach gitignore.io" in result.output


def test_list(api):
    _, responses = api
    responses["list?format=lines"] = FakeResponse("java\njavascript\npython\n")
    assert run("--list").output == "java\njavascript\npython\n"
    assert run("--list", "JAVA").output == "java\njavascript\n"


def test_output_file(api, tmp_path):
    target = tmp_path / ".gitignore"
    result = run("python", "-o", str(target))
    assert result.exit_code == 0
    assert target.read_bytes() == b"### Default ###\n*.tmp\n"


def test_output_refuses_overwrite(api, tmp_path):
    target = tmp_path / ".gitignore"
    target.write_text("keep me\n")
    result = run("python", "-o", str(target))
    assert result.exit_code == 1
    assert "already exists" in result.output
    assert target.read_text() == "keep me\n"


def test_output_force(api, tmp_path):
    target = tmp_path / ".gitignore"
    target.write_text("old\n")
    assert run("python", "-o", str(target), "--force").exit_code == 0
    assert target.read_text() == "### Default ###\n*.tmp\n"


def test_output_append(api, tmp_path):
    target = tmp_path / ".gitignore"
    target.write_text("custom")
    assert run("python", "-o", str(target), "--append").exit_code == 0
    assert target.read_text() == "custom\n### Default ###\n*.tmp\n"


@pytest.mark.parametrize("flags", [["--force"], ["--append"], ["-a", "-f", "-o", "x"]])
def test_flag_validation(api, flags):
    assert run("python", *flags).exit_code == 2
