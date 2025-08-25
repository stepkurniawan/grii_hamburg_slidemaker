"""
Wrapper around ESV API to fetch Bible passages.
https://api.esv.org/docs/passage-text/
"""

import re
from pydantic import BaseModel, Field
from typing import List
from bs4 import BeautifulSoup, Tag, NavigableString


import requests
from settings import Settings

settings = Settings()


class Footnote(BaseModel):
    """Model for a footnote in a Bible verse."""
    text: str = Field(..., description="The text of the footnote.")
    id_: str = Field(..., description="The unique identifier for the footnote.", alias="id")

class Verse(BaseModel):
    """Model for a collection of Bible verses."""
    chapter: int = Field(..., description="The chapter number within the book.")
    number: int = Field(..., description="The verse number within the chapter.")
    text: str = Field(..., description="The text of the verse.")
    heading: str | None = Field(None, description="The heading or title of the verse, if applicable.")
    subheading: str | None = Field(None, description="The subheading or subtitle of the verse, if applicable.")
    footnotes: List[Footnote] | None = Field(None, description="A list of footnotes associated with the verse, if any.")

class Passage(BaseModel):
    """Model for a Bible passage, including its reference and verses."""
    reference : str = Field(..., description="The reference for the Bible passage, e.g., 'John 3:16'")
    verses : List[Verse] = Field(..., description="A list of verses in the passage, each represented as a dictionary with keys 'number' and 'text'.")
    copyright_ : str | None = Field(None, description="Copyright information for the Bible translation used.", alias = "copyright")
    options : dict[str, bool] | None = Field(None, description="Options used for the request, such as 'include-footnotes'.")



class EsvService: 
    def __init__(self):
        self.http_session = requests.Session()
        self.http_session.headers.update({"Authorization": f'Token {settings.ESV_BIBLE_API_KEY}'})

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
            "include_verse_anchors": "false",
            "include_headings": "true",
            "include_subheadings": "true",
            "include_footnotes": "false",
            "include_footnote_body": "false",
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

        passage_html = "".join(json_payload.get("passages", []))
        canonical_reference = json_payload.get("canonical", reference)

        verse_models = self._parse_passage_verse(passage_html)
        used_option_flags = {name: (value == "true") for name, value in request_params.items() if name != "q"}

        return Passage(
            reference=canonical_reference,
            verses=verse_models,
            options=used_option_flags,
        )
        
    def _parse_passage_verse(self, passage_html: str) -> tuple[list[Verse]]:
        soup = BeautifulSoup(passage_html, 'html.parser')
        verses_list: List[Verse] = []

        # Find all verse markers in the document in the order they appear.
        verse_markers = soup.find_all('b', class_=['chapter-num', 'verse-num'])
        
        current_chapter = 0 # Initialize chapter number

        for marker in verse_markers:
            # --- 1. Extract chapter, verse number, and text ---
            marker_text = marker.get_text(strip=True)
            
            # If the marker text contains ':', it's a chapter:verse format
            if ':' in marker_text:
                chapter_str, verse_str = marker_text.split(':')
                current_chapter = int(re.sub(r'\D', '', chapter_str))
                verse_number = int(re.sub(r'\D', '', verse_str))
            else: # Otherwise, it's just a verse number
                verse_number = int(re.sub(r'\D', '', marker_text))

            verse_text_parts = []
            for sibling in marker.next_siblings:
                if isinstance(sibling, Tag) and sibling.get('class') and ('verse-num' in sibling.get('class') or 'chapter-num' in sibling.get('class')):
                    break
                if isinstance(sibling, NavigableString):
                    verse_text_parts.append(sibling.strip())
                elif isinstance(sibling, Tag):
                    verse_text_parts.append(sibling.get_text(strip=True))
            
            verse_text = ' '.join(filter(None, verse_text_parts)).strip()

            # --- 2. Determine the heading for this specific verse ---
            current_heading = None
            parent_p = marker.find_parent('p')

            if parent_p:
                # A heading applies only if this is the FIRST verse marker in the paragraph.
                is_first_verse_in_p = not marker.find_previous_sibling('b', class_=['chapter-num', 'verse-num'])

                if is_first_verse_in_p:
                    # If it's the first verse, check if the paragraph's immediate predecessor is an <h3>.
                    prev_tag = parent_p.find_previous_sibling(name=True)
                    if prev_tag and prev_tag.name == 'h3':
                        current_heading = prev_tag.get_text(strip=True)

            # --- 3. Create the Verse object and add to the list ---
            verses_list.append(Verse(
                chapter=current_chapter,
                number=verse_number,
                text=verse_text,
                heading=current_heading,
            ))

        return verses_list
