"""
Wrapper around ESV API to fetch Bible passages.
https://api.esv.org/docs/passage-text/
"""

from pydantic import BaseModel, Field
from typing import List
from bs4 import BeautifulSoup, Tag


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
            "include_verse_numbers": "false",
            "include_verse_anchors": "false",
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

        passage_html = "".join(json_payload.get("passages", []))
        canonical_reference = json_payload.get("canonical", reference)

        verse_models, copyright_text = self._parse_passage_html(passage_html)
        used_option_flags = {name: (value == "true") for name, value in reference.items() if name != "q"}

        return Passage(
            reference=canonical_reference,
            verses=verse_models,
            copyright=copyright_text,
            options=used_option_flags,
        )
        
    def _parse_passage_html(self, passage_html: str) -> tuple[list[Verse], str | None]:
            """Best-effort parser for the ESV HTML payload into Verse/Footnote models."""
            soup_document = BeautifulSoup(passage_html, "html.parser")

            # 1) Build a map from footnote HTML id -> full footnote text
            footnote_text_by_id: dict[str, str] = {}
            for footnote_container_element in soup_document.select("ol, ul, div"):
                container_class_names = " ".join(footnote_container_element.get("class", [])).lower()
                if "footnote" in container_class_names or "footnotes" in container_class_names:
                    for footnote_item_element in footnote_container_element.find_all(["li", "div"], recursive=False):
                        footnote_id = footnote_item_element.get("id")
                        if footnote_id:
                            footnote_text = footnote_item_element.get_text(" ", strip=True)
                            footnote_text_by_id[footnote_id] = footnote_text

            # 2) Stream the document and track headings/subheadings while assembling verses
            current_heading_text: str | None = None
            current_subheading_text: str | None = None
            verse_models: list[Verse] = []

            document_flow_elements: list[Tag] = list(soup_document.find_all(True, recursive=True))
            for html_element in document_flow_elements:
                tag_name = html_element.name or ""
                element_class_names = " ".join(html_element.get("class", [])).lower()

                # Update heading/subheading state
                if tag_name in {"h2", "h3", "h4", "h5"}:
                    heading_text = html_element.get_text(" ", strip=True)
                    if "subheading" in element_class_names:
                        current_subheading_text = heading_text or None
                    else:
                        current_heading_text = heading_text or None
                        current_subheading_text = None
                    continue

                # Detect verse boundary via verse-number tag
                if tag_name == "b" and "verse-num" in element_class_names:
                    verse_number_tag = html_element
                    try:
                        verse_number = int(verse_number_tag.get_text("", strip=True))
                    except ValueError:
                        continue

                    verse_container_element = verse_number_tag.find_parent(["p", "div"]) or verse_number_tag.parent

                    # Collect footnote references BEFORE stripping the markup
                    footnote_models: list[Footnote] = []
                    for anchor_element in verse_container_element.select('a[href^="#"]'):
                        footnote_id = anchor_element.get("href", "")[1:]
                        if footnote_id and footnote_id in footnote_text_by_id:
                            footnote_models.append(Footnote(id=footnote_id, text=footnote_text_by_id[footnote_id]))

                    # Prepare a copy for text cleanup (remove numbers/callouts)
                    verse_container_copy = BeautifulSoup(str(verse_container_element), "html.parser")
                    for removable_element in verse_container_copy.find_all(["b", "a", "sup"]):
                        removable_classes_string = " ".join(removable_element.get("class", [])).lower()
                        if "verse-num" in removable_classes_string or "footnote" in removable_classes_string:
                            removable_element.extract()
                    verse_text = verse_container_copy.get_text(" ", strip=True)

                    verse_models.append(
                        Verse(
                            number=verse_number,
                            text=verse_text,
                            heading=current_heading_text,
                            subheading=current_subheading_text,
                            footnotes=footnote_models or None,
                        )
                    )




esv_service = EsvService()
esv_service.get_passage("John 3:16")  # Example usage, can be removed or modified as needed

    