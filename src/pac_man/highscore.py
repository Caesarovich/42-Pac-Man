from logging import getLogger
from pathlib import Path

from pydantic import BaseModel, Field, RootModel, ValidationError

logger = getLogger(__name__)


HIGH_SCORE_FILE = Path("highscore.json")


class HighscoreEntry(BaseModel):
    name: str = Field(min_length=3, max_length=10, description="The name of the player")
    score: int = Field(ge=0, description="The score achieved by the player")


class HighscoreEntries(RootModel[list[HighscoreEntry]]):
    root: list[HighscoreEntry]

    @classmethod
    def validate_json(cls, json_str: str) -> list[HighscoreEntry]:
        return cls.model_validate_json(json_str).root

    @classmethod
    def dump_json(
        cls,
        entries: list[HighscoreEntry],
        indent: int | None = None,
    ) -> str:
        return cls(root=entries).model_dump_json(indent=indent)


class Highscore:
    @classmethod
    def load(cls) -> list[HighscoreEntry]:
        logger.info(f"Loading high scores from '{HIGH_SCORE_FILE.absolute()}'...")
        if not HIGH_SCORE_FILE.exists():
            logger.info("High score file does not exist. Returning empty list.")
            return []
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                content = f.read()
                entries = HighscoreEntries.validate_json(content)
                logger.info("High scores loaded successfully.")
                return entries
        except (OSError, ValidationError) as e:
            logger.error(f"Error occurred while loading high scores: {e}")
            logger.warning("Returning empty list due to error.")
            return []

    @classmethod
    def save(cls, entries: list[HighscoreEntry]) -> None:
        logger.info("Saving high scores...")
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(
                HighscoreEntries.dump_json(
                    entries,
                    indent=4,
                )
            )
        logger.info("High scores saved successfully.")

    @classmethod
    def add_entry(cls, entry: HighscoreEntry) -> None:
        logger.info("Adding high score entry...")
        entries = cls.load()
        entries.append(entry)
        entries.sort(key=lambda e: e.score, reverse=True)
        cls.save(entries[:10])


if __name__ == "__main__":
    highscore = Highscore()
    highscore.add_entry(HighscoreEntry(name="Norminette", score=100))
    highscore.add_entry(HighscoreEntry(name="Xavier", score=150))
    highscore.add_entry(HighscoreEntry(name="Moulinette", score=120))

    print("Current High Scores:")
    for entry in highscore.load():
        print(f"{entry.name}: {entry.score}")
