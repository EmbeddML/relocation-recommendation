from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR.joinpath("data")
RAW_DATA_DIR = DATA_DIR.joinpath("raw")
PROCESSED_DATA_DIR = DATA_DIR.joinpath("processed")
GENERATED_DATA_DIR = DATA_DIR.joinpath("generated")
BOUNDARIES_DATA_DIR = DATA_DIR.joinpath("boundaries")

ASSETS_DIR = PROJECT_DIR.joinpath("assets")
KEPLER_DIR = ASSETS_DIR.joinpath("kepler")

FUNCTIONAL_DATA_DIR = RAW_DATA_DIR.joinpath("functional")