"""
Create a Bible API that can be used to search for verses, chapters, and books.
it will use https://api.biblesupersearch.com/api as the source of the data.
Examples
Look up Romans 4:1 - 2
https://api.biblesupersearch.com/api?bible=kjv&reference=Rom 4:1-2
Result: 
{"hash":"o176n01dop","disambiguation":[],"strongs":[],"paging":[],"errors":[],"error_level":0,"results":[{"book_id":45,"book_name":"Romans","book_short":"Rom","book_raw":"Rom","chapter_verse":"4:1 - 2","chapter_verse_raw":null,"verse_index":{"4":[1,2]},"verses":{"kjv":{"4":{"1":{"id":28024,"book":45,"chapter":4,"verse":1,"text":"\u00b6 What shall we say then that Abraham our father, as pertaining to the flesh, hath found?","italics":"","claimed":true},"2":{"id":28025,"book":45,"chapter":4,"verse":2,"text":"For if Abraham were justified by works, he hath whereof to glory; but not before God.","italics":"","claimed":true}}}},"verses_count":2,"single_verse":false,"nav":{"prev_book":"Acts","next_book":"1 Corinthians","next_chapter":"Romans 5","ncb_name":"Romans","prev_chapter":"Romans 3","pcb_name":"Romans","cur_chapter":"Romans 4","ccb_name":"Romans","ncb":45,"ncc":5,"pcb":45,"pcc":3,"ccb":45,"ccc":4,"nb":46,"pb":44}}]}


for english bible, use kjv
for indonesian bible, use indo_tb
for german bible, use luther
"""

import requests
import json
import os
import re
from bible_translation import indonesian_to_english_bible, indonesian_to_german_bible

######### GLOBAL VARIABLES #########
BASE_URL = "https://api.biblesupersearch.com/api"

LANG = "de"
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
    data = response.json()
    
    return data



def get_verses_dict(book, chapter, verse_start, verse_end, language="ID"):
    """
    param:
    book (string): ex: "Kejadian"
    chapter (string): ex: "1"
    verse_start (string): ex: "1"
    verse_end (string): ex: "2"

    return:
    verses_dict (dictionary): ex: {"Kejadian 1:1" : "In the beginning God created the heaven and the earth.",

    """
    verses_dict = {}
    
    if language == "EN":
        BIBLE_VERSION = "kjv"
    elif language == "ID":
        BIBLE_VERSION = "indo_tb"
    elif language == "DE":
        BIBLE_VERSION = "luther_1912"
    
    # create a dictionary from the verses
    # {"Romans 4:1" : "What shall we say then that Abraham our father, as pertaining to the flesh, hath found?",
    # "Romans 4:2" : "For if Abraham were justified by works, he hath whereof to glory; but not before God."}
    german_book = indonesian_to_german_bible[book]
    english_book = translate_ind_to_eng(book)
    reference = f"{english_book} {chapter}:{verse_start}-{verse_end}"

    result = fetch_bible_passage(BIBLE_VERSION, reference)
    

    for i in range(0, len(result["results"])):
        verse_result = result["results"][i]["verses"][BIBLE_VERSION]
        for verse in verse_result[chapter]:
            if language == "DE":
                verses_dict[f"{german_book} {chapter}:{verse}"] = verse_result[chapter][verse]["text"]
            elif language == "ID":
                verses_dict[f"{book} {chapter}:{verse}"] = verse_result[chapter][verse]["text"]
            else:
                verses_dict[f"{english_book} {chapter}:{verse}"] = verse_result[chapter][verse]["text"]

    return verses_dict

def translate_ind_to_eng(bible_book_full_indo):
    """
    parameter: bible_book_full_indo (string), ex: "Kejadian"
    """
    return indonesian_to_english_bible[bible_book_full_indo]








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


