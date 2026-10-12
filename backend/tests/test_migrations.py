import subprocess
import sys
from pathlib import Path


def test_alembic_offline_sql_contains_all_tables():
    """Valida la cadena de migraciones sin conectarse a ninguna base."""
    backend_dir = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    sql = result.stdout
    assert "0003_monitoring" in sql
    assert "CREATE TABLE installations" in sql
    assert "CREATE TABLE health_checks" in sql
    assert "CREATE TABLE alert_states" in sql
