---
name: code-preferences
description: Coding style and formatting preferences for this project
---

## Formatting

- No emojis in code, comments, commit messages, or responses.

## Code Style

- Keep code concise. Avoid unnecessary abstractions, wrappers, or verbose patterns.
- Try not to have more than two layers of is-a inheritance in Python/OOP codebases.
- Write all imports at the top of the file. Do not use inline or deferred imports unless there is a specific technical reason (e.g., circular dependency).
- Generate docstrings for all new methods and functions. Keep descriptions to a single concise sentence when possible.

## Refactoring

- When refactoring existing code, ask before generating new methods or extracting functions. Do not introduce new abstractions without confirmation.

## Environment

- Unless told otherwise, assume the working environment is a Linux/Ubuntu VM.
- Use Linux-compatible commands, paths, and tooling by default.
- Use `python3` to run Python code (not `python`).
- This project uses `uv` as the package manager in a uv environment.

## Project-Specific Patterns

### Data Classes

- Use `@dataclass(frozen=True)` for immutable configuration/style classes (e.g., `ScheduleStyles`, `ScheduleDimensions`).
- Use `@dataclass(frozen=True, eq=False)` when the class only holds reusable style objects and identity comparison is not needed.
- Use mutable `@dataclass` for classes that manage state or resources (e.g., `BaseCreator`).
- Use `field(default_factory=...)` for mutable default values like dicts, lists, or objects.

### Models

- Use Pydantic `BaseModel` for data validation schemas (e.g., `InspectionEntry`).
- Use `StrEnum` for string enumeration types.

### Logging

- Initialize logging at module level with `basicConfig(level=DEBUG)` and `getLogger(__name__)`.
- Use `logger.info()` for major operations and `logger.debug()` for detailed steps.

### Type Hints

- Use explicit type hints for all function parameters and return types.
- Use `Literal` for fields with a fixed set of string values (e.g., `Literal["Y", "N"]`).
- Use `|` union syntax for optional types (e.g., `str | None`).

### Constants

- Define module-level constants in uppercase (e.g., `COUNTY_MAP`).

### Excel/openpyxl

- Store reusable style objects (Font, Border, Alignment) in a frozen dataclass for efficiency.
- Apply borders, fonts, and alignment consistently using helper methods like `style_cell()`.

### File Paths

- Use `pathlib.Path` for all file path operations.
- Resolve paths relative to `__file__` for project directory detection.
