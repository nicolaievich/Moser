from app import auth


def test_storage_writable_creates_private_database(tmp_path, monkeypatch):
    data_dir = tmp_path / "private-data"
    monkeypatch.setattr(auth, "DATA_DIR", data_dir)
    monkeypatch.setattr(auth, "DB_PATH", data_dir / "moser.db")

    auth.check_storage_writable()

    assert (data_dir / "moser.db").is_file()
    assert auth.user_exists() is False
