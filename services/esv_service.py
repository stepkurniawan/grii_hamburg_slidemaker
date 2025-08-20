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
        self.http_session = requests.Session()
        self.http_session.headers.update({"Authorization": f'Token {settings.esv_api_key}'})

    def get_passage(self, reference: str, **override_flag_values: bool) -> Passage:
        """
        Fetch a Bible passage from the ESV API.
        
        Args:
            reference (str): The Bible reference to fetch, e.g., 'John 3:16'.
            **override_flag_values: Optional flags to override default behavior, such as 'include-footnotes'.
        
        Returns:
            Passage: A Passage object containing the reference, verses, copyright information, and options.
        """

        request_params = {
            "q": reference,
            "include_verse_numbers": "true",
            "include_verse_anchors": "true",
            "include_headings": "true",
            "include_subheadings": "true",
            "include_footnotes": "true",
            "include_footnote_body": "true",
            "include_copyright": "false",
            "include_short_copyright": "false",
        }
        for flag_name, flag_value in override_flag_values.items():
            request_params[flag_name] = "true" if flag_value else "false"

        response = self.http_session.get(
            settings.ESV_HTML_API_URL,
            params=request_params,
            timeout=30
        )
        response.raise_for_status()

        json_payload = response.json()


esv_service = EsvService()
esv_service.get_passage("John 3:16")  # Example usage, can be removed or modified as needed

    