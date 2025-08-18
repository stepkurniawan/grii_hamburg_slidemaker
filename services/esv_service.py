"""
Wrapper around ESV API to fetch Bible passages.
https://api.esv.org/docs/passage-text/
"""

from pydantic import BaseModel, Field
from typing import List

import requests
from settings import Settings

settings = Settings()


class Footnote(BaseModel):
    """Model for a footnote in a Bible verse."""
    text: str = Field(..., description="The text of the footnote.")
    id_: str = Field(..., description="The unique identifier for the footnote.", alias="id")

class Verse(BaseModel):
    """Model for a collection of Bible verses."""
    number: int = Field(..., description="The verse number within the chapter.")
    text: str = Field(..., description="The text of the verse.")
    heading: str | None = Field(..., description="The heading or title of the verse, if applicable.")
    subheading: str | None = Field(..., description="The subheading or subtitle of the verse, if applicable.")
    footnotes: List[Footnote] | None = Field(..., description="A list of footnotes associated with the verse, if any.")

class Passage(BaseModel):
    """Model for a Bible passage, including its reference and verses."""
    reference : str = Field(..., description="The reference for the Bible passage, e.g., 'John 3:16'")
    verses : List(Verse) = Field(..., description="A list of verses in the passage, each represented as a dictionary with keys 'number' and 'text'.")
    copyright_ : str | None = Field(..., description="Copyright information for the Bible translation used.", alias = "copyright")
    options : dict[str, bool] | None = Field(..., description="Options used for the request, such as 'include-footnotes'.")



class EsvService: 
    def __init__(self):
        self.base_url = settings.API_URL
        self.api_key = settings.API_KEY
        self.headers = f"Authorization: Token {self.api_key}"
        self.base_params = {
            "include-footnotes": True,
            "include-headings": True,
            "include-subheadings": True,
            "include-verse-numbers": True,
            "include-heading-horizontal-lines" : True,
        }

    def get_passage(self, reference: str) -> Passage:
        """
        Fetches a Bible passage by its reference.

        Args:
            reference (str): The reference for the Bible passage, e.g., "John 3:16".

        Returns:
            Passage: A Passage object containing the reference and verses.
        """
        params = self.base_params.copy()
        params['q'] = reference

        response = requests.get(self.base_url, headers=self.headers, params=params)
        response.raise_for_status()

        return Passage.model_validate(response.json())

    