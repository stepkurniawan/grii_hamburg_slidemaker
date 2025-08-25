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
    number: int = Field(..., description="The verse number within the chapter.")
    text: str = Field(..., description="The text of the verse.")
    heading: str | None = Field(..., description="The heading or title of the verse, if applicable.")
    subheading: str | None = Field(..., description="The subheading or subtitle of the verse, if applicable.")
    footnotes: List[Footnote] | None = Field(..., description="A list of footnotes associated with the verse, if any.")

class Passage(BaseModel):
    """Model for a Bible passage, including its reference and verses."""
    reference : str = Field(..., description="The reference for the Bible passage, e.g., 'John 3:16'")
    verses : List[Verse] = Field(..., description="A list of verses in the passage, each represented as a dictionary with keys 'number' and 'text'.")
    copyright_ : str | None = Field(None, description="Copyright information for the Bible translation used.", alias = "copyright")
    options : dict[str, bool] | None = Field(..., description="Options used for the request, such as 'include-footnotes'.")



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

        # 2. vind all verse markesers (b tags with chapter-num or verse-num class)
        verse_markers = soup.find_all('b', class_=['chapter-num', 'verse-num'])

        for marker in verse_markers:
            # 3. Extract the verse number
            # Handles formats like "3:1 " and "2 " -> gets the number after the colon or the number itself.
            verse_num_str = marker.get_text(strip=True).split(':')[-1]
            verse_number = int(re.sub(r'\D', '', verse_num_str)) # Remove non-digit characters

            # 4. Gather the verse text from all subsequent siblings
            verse_text_parts = []
            for sibling in marker.next_siblings:
                # Stop if we hit the next verse marker
                if isinstance(sibling, Tag) and sibling.get('class') and ('verse-num' in sibling.get('class') or 'chapter-num' in sibling.get('class')):
                    break
                # If it's a NavigableString (plain text)
                if isinstance(sibling, NavigableString):
                    verse_text_parts.append(sibling.strip())
                # If it's another tag (like the <span>), get all its text
                elif isinstance(sibling, Tag):
                    verse_text_parts.append(sibling.get_text(strip=True))
            
            # Join the parts, filtering out any empty strings
            verse_text = ' '.join(filter(None, verse_text_parts)).strip()
        
            # --- 5. Determine the heading for this specific verse ---
            current_heading = None
            parent_p = marker.find_parent('p')

            if parent_p:
            # A heading applies only if this is the FIRST verse marker in the paragraph.
                is_first_verse_in_p = not marker.find_previous_sibling('b', class_=['chapter-num', 'verse-num'])

                if is_first_verse_in_p:
                    # If it's the first verse, check if the paragraph's immediate predecessor is an <h3>.
                    # We use find_previous_sibling(name=True) to skip over whitespace nodes.
                    prev_tag = parent_p.find_previous_sibling(name=True)
                    if prev_tag and prev_tag.name == 'h3':
                        current_heading = prev_tag.get_text(strip=True)

            # 5. Create the Pydantic Verse object
            verse_obj = Verse(
                number=verse_number,
                text=verse_text,
                heading=current_heading,
                subheading=None, # No subheadings in the provided HTML
                footnotes=None   # No footnotes in the provided HTML
            )
            verses_list.append(verse_obj)

        return verses_list
