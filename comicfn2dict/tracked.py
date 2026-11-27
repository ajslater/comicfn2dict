"""Text that remembers where each character sat in the filename."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from re import Match, Pattern


@dataclass(frozen=True, slots=True)
class TrackedText:
    """
    A string and, for each character, its index in the source filename.

    Every rewrite of the unparsed path goes through these methods, so a match
    found in the rewritten text can still be placed in the original name. An
    inserted character takes the index of the text it replaces.
    """

    text: str
    origins: tuple[int, ...]

    @classmethod
    def from_source(cls, text: str) -> TrackedText:
        """Track a string from its own start."""
        return cls(text, tuple(range(len(text))))

    @classmethod
    def join(cls, delimiter: str, parts: Iterable[TrackedText]) -> TrackedText:
        """Join parts. A delimiter takes the origin of the part after it."""
        texts: list[str] = []
        origins: list[int] = []
        for part in parts:
            if texts:
                origins += (part.origin(0),) * len(delimiter)
            texts.append(part.text)
            origins += part.origins
        return cls(delimiter.join(texts), tuple(origins))

    def __getitem__(self, key: slice) -> TrackedText:
        """Slice the text and its origins together."""
        return TrackedText(self.text[key], self.origins[key])

    def origin(self, index: int) -> int:
        """Index in the source of the character at index, or just past the end."""
        if index < len(self.origins):
            return self.origins[index]
        return self.origins[-1] + 1 if self.origins else 0

    def strip(self) -> TrackedText:
        """Strip surrounding whitespace."""
        start = len(self.text) - len(self.text.lstrip())
        return self[start : len(self.text.rstrip())]

    def sub(
        self, regex: Pattern, replacement: str | Callable[[Match], str], count: int = 0
    ) -> TrackedText:
        """Do regex.sub(). A replacement takes the origin of its match's start."""
        texts: list[str] = []
        origins: list[int] = []
        position = 0
        for number, match in enumerate(regex.finditer(self.text)):
            if count and number >= count:
                break
            new = (
                match.expand(replacement)
                if isinstance(replacement, str)
                else replacement(match)
            )
            texts += (self.text[position : match.start()], new)
            origins += self.origins[position : match.start()]
            if new == match.group():
                # Text that a replacement leaves as it was keeps its origins.
                origins += self.origins[match.start() : match.end()]
            else:
                origins += (self.origin(match.start()),) * len(new)
            position = match.end()
        texts.append(self.text[position:])
        origins += self.origins[position:]
        return TrackedText("".join(texts), tuple(origins))

    def split(self, delimiter: str) -> list[TrackedText]:
        """Split on a delimiter string."""
        parts: list[TrackedText] = []
        start = 0
        while (end := self.text.find(delimiter, start)) != -1:
            parts.append(self[start:end])
            start = end + len(delimiter)
        parts.append(self[start:])
        return parts
