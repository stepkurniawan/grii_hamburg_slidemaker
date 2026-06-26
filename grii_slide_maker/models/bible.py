import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from grii_slide_maker.bible.translations import english_to_indonesian_bible


BIBLE_REFERENCE_PATTERN = re.compile(
    r"^(?P<book>(?:[1-3]\s+)?[A-Za-z][A-Za-z\s]+?)\s+"
    r"(?P<chapter>\d+):(?P<verse_start>\d+)-(?P<verse_end>\d+)$"
)


class BibleReference(BaseModel):
    """Parsed English Bible reference such as 'Genesis 1:2-3'."""

    original: str
    book: str
    chapter: int = Field(ge=1)
    verse_start: int = Field(ge=1)
    verse_end: int = Field(ge=1)

    @model_validator(mode="before")
    @classmethod
    def parse_reference(cls, value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            reference = " ".join(value.strip().split())
            match = BIBLE_REFERENCE_PATTERN.match(reference)
            if not match:
                raise ValueError(
                    "Bible reference must look like 'Genesis 1:2-3' or '1 Kings 1:1-2'"
                )
            return {
                "original": reference,
                "book": match.group("book"),
                "chapter": int(match.group("chapter")),
                "verse_start": int(match.group("verse_start")),
                "verse_end": int(match.group("verse_end")),
            }
        return value

    @field_validator("book")
    @classmethod
    def validate_book(cls, value: str) -> str:
        book = " ".join(value.strip().split())
        if book not in english_to_indonesian_bible:
            raise ValueError(f"Unknown English Bible book: {book}")
        return book

    @model_validator(mode="after")
    def validate_verse_range(self) -> "BibleReference":
        if self.verse_end < self.verse_start:
            raise ValueError("Bible verse range cannot go backwards")
        return self

    def as_reference_text(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse_start}-{self.verse_end}"

    def __str__(self) -> str:
        return self.as_reference_text()


class BibleSuperSearchVerse(BaseModel):
    id: int
    book: int
    chapter: int
    verse: int
    text: str
    italics: str | None = None
    claimed: bool | None = None


class BibleSuperSearchResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    book_id: int
    book_name: str
    book_short: str | None = None
    chapter_verse: str
    verses: dict[str, dict[str, dict[str, BibleSuperSearchVerse]]]
    verses_count: int = Field(ge=0)
    single_verse: bool | None = None


class BibleSuperSearchResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    hash: str | None = None
    errors: list[Any] = Field(default_factory=list)
    error_level: int = 0
    results: list[BibleSuperSearchResult] = Field(default_factory=list)

    @model_validator(mode="after")
    def ensure_usable_response(self) -> "BibleSuperSearchResponse":
        if self.error_level:
            raise ValueError(f"BibleSuperSearch returned error level {self.error_level}")
        if self.errors:
            raise ValueError(f"BibleSuperSearch returned errors: {self.errors}")
        if not self.results:
            raise ValueError("BibleSuperSearch returned no passage results")
        return self


class Footnote(BaseModel):
    """Model for a footnote in a Bible verse."""

    text: str = Field(..., description="The text of the footnote.")
    id_: str = Field(..., description="The unique identifier for the footnote.", alias="id")


class Verse(BaseModel):
    """Model for a collection of Bible verses."""

    chapter: int = Field(
        ...,
        ge=0,
        description="The chapter number within the book.",
    )
    number: int = Field(
        ...,
        ge=1,
        description="The verse number within the chapter.",
    )
    text: str = Field(
        ...,
        min_length=1,
        description="The text of the verse.",
    )
    heading: str | None = Field(
        None,
        description="The heading or title of the verse, if applicable.",
        examples=["For God So Loved the World"],
    )
    subheading: str | None = Field(
        None,
        description="The subheading or subtitle of the verse, if applicable.",
        examples=["Jesus and Nicodemus"],
    )
    footnotes: list[Footnote] | None = Field(
        None,
        description="A list of footnotes associated with the verse, if any.",
    )


class Passage(BaseModel):
    """Model for a Bible passage, including its reference and verses."""

    model_config = ConfigDict(populate_by_name=True)

    reference: str = Field(
        ...,
        min_length=1,
        description="The reference for the Bible passage, e.g., 'John 3:16'.",
    )
    verses: list[Verse] = Field(
        ...,
        min_length=1,
        description="The verses that make up the passage.",
    )
    copyright_: str | None = Field(
        None,
        description="Copyright information for the Bible translation used.",
        alias="copyright",
    )
    options: dict[str, bool] | None = Field(
        None,
        description="Options used for the request, such as whether footnotes or headings were included.",
    )


class EsvTextResponse(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="The original passage query sent to the ESV API.",
    )
    canonical: str | None = Field(
        None,
        description="The normalized canonical reference returned by the ESV API.",
    )
    parsed: list[list[int]] | None = Field(
        None,
        description="Parsed numeric reference metadata returned by the ESV API.",
    )
    passage_meta: list[dict] | None = Field(
        None,
        description="Additional metadata for the returned passages from the ESV API.",
    )
    passages: list[str] = Field(
        ...,
        min_length=1,
        description="The passage text blocks returned by the ESV API.",
    )
