from app.config import load_settings


def test_load_settings_reads_env_file(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "MEMENTO_APP_NAME=Test Notes",
                "MEMENTO_APP_VERSION=9.9.9",
                "MEMENTO_LOG_LEVEL=DEBUG",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("MEMENTO_APP_NAME", raising=False)
    monkeypatch.delenv("MEMENTO_APP_VERSION", raising=False)
    monkeypatch.delenv("MEMENTO_LOG_LEVEL", raising=False)

    settings = load_settings(env_file)

    assert settings.app_name == "Test Notes"
    assert settings.app_version == "9.9.9"
    assert settings.log_level == "DEBUG"


def test_environment_variables_override_env_file(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MEMENTO_APP_NAME=File Notes", encoding="utf-8")
    monkeypatch.setenv("MEMENTO_APP_NAME", "Environment Notes")

    settings = load_settings(env_file)

    assert settings.app_name == "Environment Notes"
