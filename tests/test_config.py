from app.config import load_settings


def test_load_settings_reads_env_file(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "MEMENTO_APP_NAME=Test Notes",
                "MEMENTO_APP_VERSION=9.9.9",
                "MEMENTO_LOG_LEVEL=DEBUG",
                "MEMENTO_STORAGE_DIR=/tmp/memento-test-notes",
                "MEMENTO_API_BASE_URL=http://localhost:9000",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("MEMENTO_APP_NAME", raising=False)
    monkeypatch.delenv("MEMENTO_APP_VERSION", raising=False)
    monkeypatch.delenv("MEMENTO_LOG_LEVEL", raising=False)
    monkeypatch.delenv("MEMENTO_STORAGE_DIR", raising=False)
    monkeypatch.delenv("MEMENTO_API_BASE_URL", raising=False)

    settings = load_settings(env_file)

    assert settings.app_name == "Test Notes"
    assert settings.app_version == "9.9.9"
    assert settings.log_level == "DEBUG"
    assert settings.storage_dir == "/tmp/memento-test-notes"
    assert settings.api_base_url == "http://localhost:9000"


def test_environment_variables_override_env_file(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MEMENTO_APP_NAME=File Notes", encoding="utf-8")
    monkeypatch.setenv("MEMENTO_APP_NAME", "Environment Notes")

    settings = load_settings(env_file)

    assert settings.app_name == "Environment Notes"
