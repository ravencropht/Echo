"""Character model and profile parser."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.config import config


@dataclass
class Character:
    """Character profile data."""

    name: str
    personality: str
    background: str
    relationships: str
    example_dialogue: str

    def build_system_prompt(self) -> str:
        """Build a system prompt for the LLM based on character profile."""
        return f"""You are {self.name}. Respond in character, maintaining their personality, speaking style, and mannerisms.

PERSONALITY: {self.personality}

BACKGROUND: {self.background}

RELATIONSHIPS: {self.relationships}

EXAMPLE DIALOGUE:
{self.example_dialogue}

Always stay in character. Your responses should reflect {self.name}'s voice, knowledge, and perspective."""

    @classmethod
    def from_profile_file(cls, profile_path: Optional[Path] = None) -> "Character":
        """Parse profile.txt and create a Character instance.

        Args:
            profile_path: Path to profile.txt. If None, uses config path.

        Returns:
            Character instance

        Raises:
            FileNotFoundError: If profile file doesn't exist
            ValueError: If required fields are missing
        """
        if profile_path is None:
            profile_path = config.get_profile_path()

        if not profile_path.exists():
            raise FileNotFoundError(f"Profile file not found: {profile_path}")

        content = profile_path.read_text()

        # Parse the profile file
        fields = {
            "name": "",
            "personality": "",
            "background": "",
            "relationships": "",
            "example_dialogue": "",
        }

        current_field = None
        current_value = []

        for line in content.split("\n"):
            line = line.rstrip()

            # Check if line starts a new field (field name before colon is uppercase)
            if ":" in line:
                field_name = line.split(":", 1)[0].strip()
                if field_name.isupper():
                    # Save previous field if any
                    if current_field:
                        fields[current_field] = "\n".join(current_value).strip()

                    # Start new field
                    current_field = field_name.lower()
                    value_part = line.split(":", 1)[1] if ":" in line else ""

                    if value_part.strip():
                        current_value = [value_part.strip()]
                    else:
                        current_value = []
                elif current_field:
                    current_value.append(line)
            elif current_field:
                current_value.append(line)

        # Save last field
        if current_field:
            fields[current_field] = "\n".join(current_value).strip()

        # Validate required fields
        if not fields["name"]:
            raise ValueError("Required field 'NAME' is missing from profile.txt")

        return cls(
            name=fields["name"],
            personality=fields.get("personality", "A unique character with a distinctive personality."),
            background=fields.get("background", ""),
            relationships=fields.get("relationships", ""),
            example_dialogue=fields.get("example_dialogue", ""),
        )

    def to_dict(self) -> dict:
        """Convert character to dictionary for API responses."""
        return {
            "name": self.name,
            "personality": self.personality,
            "background": self.background,
            "relationships": self.relationships,
            "example_dialogue": self.example_dialogue,
        }
