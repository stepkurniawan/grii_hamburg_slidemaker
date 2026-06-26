"""Fetch and format Bible passages for the slide generator."""

import requests
from bible_translation import english_to_indonesian_bible, english_to_german_bible
from models import BibleReference, BibleSuperSearchResponse
from services.esv_service import EsvService

######### GLOBAL VARIABLES #########
BASE_URL = "https://api.biblesupersearch.com/api"

LANG = "en"
BIBLE_VERSION = ""

reference = "Genesis 1:1-2"

######### FUNCTIONS #########

def fetch_bible_passage(bible_version, reference):
    # reference = "Rom 4:1-2", always in english
    params = {
        "bible": bible_version,
        "reference": reference
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    return BibleSuperSearchResponse.model_validate(data)



def get_verses_dict(english_book, chapter, verse_start, verse_end, language="ID"):
    """
    param:
    english_book (string): ex: "Genesis"
    chapter (string): ex: "1"
    verse_start (string): ex: "1"
    verse_end (string): ex: "2"

    return:
    verses_dict (dictionary): ex: {"Kejadian 1:1" : "In the beginning God created the heaven and the earth.",

    """
    bible_reference = BibleReference.model_validate(
        f"{english_book} {chapter}:{verse_start}-{verse_end}"
    )
    verses_dict = {}

    if language == "EN":
        bible_version = "asv"
    elif language == "ID":
        bible_version = "indo_tb"
    elif language == "DE":
        bible_version = "luther_1912"
    else:
        raise ValueError(f"Unsupported Bible language: {language}")
    
    # create a dictionary from the verses
    # {"Romans 4:1" : "What shall we say then that Abraham our father, as pertaining to the flesh, hath found?",
    # "Romans 4:2" : "For if Abraham were justified by works, he hath whereof to glory; but not before God."}
    german_book = english_to_german_bible.get(bible_reference.book)
    indonesian_book = english_to_indonesian_bible.get(bible_reference.book)
    reference = bible_reference.as_reference_text()

    result = fetch_bible_passage(bible_version, reference)

    esv_service = EsvService()
    esv_passage = esv_service.get_passage(reference)
    

    for bible_result in result.results:
        # get all the verses in the chapter of this bible
        verse_result = bible_result.verses[bible_version]
        chapter_key = str(bible_reference.chapter)

        for verse in verse_result[chapter_key]:
            if language == "DE":
                verses_dict[f"{german_book} {chapter_key}:{verse}"] = verse_result[chapter_key][verse].text
            elif language == "ID":
                verses_dict[f"{indonesian_book} {chapter_key}:{verse}"] = verse_result[chapter_key][verse].text
            
    for verse in esv_passage.verses:
        verses_dict[f"{bible_reference.book} {verse.chapter}:{verse.number}"] = verse.text

    return verses_dict




################# TESTING + DEBUGGING #################
# result = fetch_bible_passage(BIBLE_VERSION, reference)
# print("Result:", result)
# book = result["results"][0]["book_name"]
# chapter = result["results"][0]["chapter_verse"].split(":")[0]
# verses = result["results"][0]["verses"]["kjv"]
# print("Book:", book)
# print("Chapter:", chapter)
# print("Verses:", verses)


# get_verses_dict("Keluaran", "1", "1", "2", "DE")

# print("Verses:", verses)
# print("Verses type:", type(verses))
# print("Verses keys:", verses.keys())


