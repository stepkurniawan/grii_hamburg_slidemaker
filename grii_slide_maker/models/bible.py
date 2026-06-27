import re
from collections.abc import ItemsView, Iterator, KeysView, ValuesView
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator

from grii_slide_maker.bible.translations import english_to_indonesian_bible


# Regex to parse a standard English Bible reference like 'Genesis 1:2-3' or '1 Kings 2:1-3'.
# Groups:
#   book         - optional leading 1-3 and book name, allowing spaces in the book name
#   chapter      - the chapter number before the colon
#   verse_start  - the first verse in the range
#   verse_end    - the last verse in the range
BIBLE_REFERENCE_PATTERN = re.compile(
    r"^(?P<book>(?:[1-3]\s+)?[A-Za-z][A-Za-z\s]+?)\s+"
    r"(?P<chapter>\d+):(?P<verse_start>\d+)-(?P<verse_end>\d+)$"
)


class BibleReference(BaseModel):
    """Parsed English Bible reference such as 'Genesis 1:2-3'."""

    full_input: str = Field(
        ...,
        min_length=1,
        description="The fulls tring input reference string provided by the user, e.g. 'Genesis 1:2-3'.",
        examples=["Genesis 1:2-3", "1 Kings 2:1-3"],
    )
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
                "full_input": reference,
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


class BibleVerseDict(RootModel[dict[str, str]]):
    """Mapping of display Bible references to verse text."""

    root: dict[str, str] = Field(
        default_factory=dict,
        description="A mapping from display references like 'Genesis 1:1' to verse text.",
        examples=[{"Genesis 1:1": "In the beginning..."}],
    )

    @model_validator(mode="after")
    def ensure_valid_entries(self) -> "BibleVerseDict":
        for reference, text in self.root.items():
            if not reference.strip():
                raise ValueError("Bible verse reference cannot be blank")
            if not text.strip():
                raise ValueError(f"Bible verse text cannot be blank for {reference}")
        return self

    def __getitem__(self, key: str) -> str:
        return self.root[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def keys(self) -> KeysView[str]:
        return self.root.keys()

    def values(self) -> ValuesView[str]:
        return self.root.values()

    def items(self) -> ItemsView[str, str]:
        return self.root.items()

    def as_dict(self) -> dict[str, str]:
        return dict(self.root)


class BibleSuperSearchVerse(BaseModel):
    id: int = Field(
        ...,
        description="The unique identifier for the verse in the search results.",
    )
    book: int
    chapter: int
    verse: int
    text: str
    italics: str | None = Field(
        None,
        description="Text that should be rendered in italics, if applicable.",
    )
    claimed: bool | None = Field(
        None,
        description="Indicates if the verse has been marked as claimed in the search results.",
    )


class BibleSuperSearchResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    book_id: int = Field(
        ..., description="The numeric identifier for the book in Bible SuperSearch."
    )
    book_name: str = Field(
        ..., description="The full book name as returned by Bible SuperSearch."
    )
    book_short: str | None = Field(
        None,
        description="Optional shortened book name or abbreviation for the book."
    )
    chapter_verse: str = Field(
        ..., description="The chapter and verse reference string for this result."
    )
    verses: dict[str, dict[str, dict[str, BibleSuperSearchVerse]]] = Field(
        ...,
        description="Nested mapping of chapter numbers and verse numbers to verse details.",
        examples=[
            {
                "1": {
                    "1": {
                        "1": {
                            "id": 1,
                            "book": 1,
                            "chapter": 1,
                            "verse": 1,
                            "text": "In the beginning...",
                            "italics": None,
                            "claimed": False,
                        }
                    }
                }
            }
        ],
    )
    verses_count: int = Field(
        ge=0,
        description="The number of verses included in the search result."
    )
    single_verse: bool | None = Field(
        None,
        description="Indicates whether the result represents a single verse."
    )


class BibleSuperSearchResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    hash: str | None = Field(
        None,
        description="Optional response hash for idempotency or caching.",
        examples=["abc123def"]
    )
    errors: list[Any] = Field(
        default_factory=list,
        description="A list of errors returned by the upstream service, empty when successful.",
        examples=[[]]
    )
    error_level: int = Field(
        0,
        description="Numeric error severity level (0 = no error).",
        examples=[0]
    )
    results: list[BibleSuperSearchResult] = Field(
        default_factory=list,
        description="Search results containing passages and metadata.",
        examples=[
            {
                "query": "John 3:16",
                "verses_count": 1,
                "single_verse": True,
                "passages": [
                    {
                        "book": 43,
                        "chapter": 3,
                        "verse": 16,
                        "text": "For God so loved the world...",
                    }
                ]
            }
        ]
    )

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
