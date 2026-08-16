from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "ahootsa.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
