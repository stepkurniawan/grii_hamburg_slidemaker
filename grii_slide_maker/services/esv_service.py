"""
Wrapper around ESV API to fetch Bible passages.
https://api.esv.org/docs/passage-text/
"""

import re
from typing import List


import requests
from grii_slide_maker.config import Settings
from grii_slide_maker.models import EsvTextResponse, Passage, Verse


class EsvService: 
    def __init__(self):
        settings = Settings()
        self.settings = settings
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
            "include_headings": "false",
            "include_subheadings": "false",
            "include_footnotes": "false",
            "include_footnote_body": "false",
            "include_copyright": "false",
            "include_short_copyright": "false",
        }
        for flag_name, flag_value in override_flag_values.items():
            request_params[flag_name] = "true" if flag_value else "false"

        response = self.http_session.get(
            # settings.ESV_HTML_API_URL,
            self.settings.ESV_TEXT_API_URL,
            params=request_params,
            timeout=30
        )
        response.raise_for_status()

        json_payload = EsvTextResponse.model_validate(response.json())

        passage_response = "".join(json_payload.passages)
        canonical_reference = json_payload.canonical or reference

        verse_models = self._parse_passage_verse_text(passage_response)
        used_option_flags = {name: (value == "true") for name, value in request_params.items() if name != "q"}

        return Passage(
            reference=canonical_reference,
            verses=verse_models,
            options=used_option_flags,
        )
    
    # TEXT
    def _split_get_book(self, passage_text: str) -> str:
        """
        This function extracts the book name from the passage text.
        The book name is just the string from the beginning to the first \n\n.

        Args:
            passage_text (str): The full passage text. 
                example: Job 23:1–10\n\nJob Replies: Where Is God?\n\n  [1] Then Job answered and said:\n\n    [2] 

        Returns:
            str: The book name. Job 23:1–10

        """
        book_name = passage_text.split('\n\n')[0].strip()
        return book_name
    
    def _split_get_title(self, passage_text: str) -> str | None:
        """
        This function extracts the title from the passage text.
        The title is just the string between the first \n\n and the second \n\n.
        And it has to be before the first verse [i].

        Args:
            passage_text (str): The full passage text. 
                example: Job 23:1–10\n\nJob Replies: Where Is God?\n\n  [1] Then Job answered and said:\n\n    [2] 

        Returns:
            str | None: The title. Job Replies: Where Is God?
        """
        parts = passage_text.split('\n\n')
        if len(parts) > 2:
            title_candidate = parts[1].strip()
            if not re.match(r'^\s*\[\d+\]', title_candidate):
                return title_candidate
        return None
    
    def _parse_passage_verse_text(self, passage_text: str) -> list[Verse]:
        """
        This function parses the passage text into a list of Verse objects. The verse always starts with [i].

        Args:
            passage_text (str): The full passage text. 
                example: Job 23:1–10\n\nJob Replies: Where Is God?\n\n  [1] Then Job answered and said:\n\n    [2] 

        Returns:
            tuple[list[Verse]]: A tuple containing a list of Verse objects.
        """
        verses_list: List[Verse] = []

        book_name = self._split_get_book(passage_text)
        chapter_match = re.search(r'\b(\d+)(?=:|$)', book_name)
        chapter_number = int(chapter_match.group(1)) if chapter_match else 0

        title = self._split_get_title(passage_text)

        # Find all verse markers in the document in the order they appear.
        verse_markers = list(re.finditer(r'\[(\d+)\]', passage_text))  # Convert to a list to avoid skipping
        for i, match in enumerate(verse_markers):
            verse_number = int(match.group(1))
            start_index = match.end()
            end_index = verse_markers[i + 1].start() if i + 1 < len(verse_markers) else len(passage_text)
            verse_text = passage_text[start_index:end_index].strip()

            verses_list.append(Verse(
                chapter=chapter_number,
                number=verse_number,
                text=verse_text,
                heading=title,
            ))
            title = None  # Only the first verse gets the title

        return verses_list
        

#### TESTING + DEBUGGING ####
# esv_service = EsvService()
# test = esv_service.get_passage("Job 23:3-5")
# print(test)
