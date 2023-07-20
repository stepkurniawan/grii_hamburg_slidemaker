"""
This program is to make a powerpoint presentation for Sunday service.
It is tweaked for Hamburg Church, which is bilingual (Indonesian and German).
The inputs that are changed every week:
1. 4 song's numbers 
2. Opening Bible verse
3. Pastor's title in Indonesian and German, and name
4. Second (blue) offering purpose in Indonesian and German

The songs are stored in google drive as a jpg. 
So we just have to use that picture as a slide. 

The slide will be generated based on this structure:
1. Our service is about to start page
2. church cover - page (Static)
3. First song
4. church cover - page
5. Second song
6. Opening Bible vers (in German), ex: Subtitel: Bibellesung, Titel: Jesaja 43,1-7 
    - German Translation with the verse number
    - Indonesian Translation with the verse number
7. church cover - page
8. Third song
9. church cover - page
10. Lord's Prayer (in German and Indonesian) -  3 slides - Static, we have it
11. church cover - page
12. Predigt - page
    - Title: <Pastor's title in German>. <Pastor's name>
    - Subtitle: <Pastor's title in Indonesian>. <Pastor's name>
13. church cover - page
14. Apostles' Creed (in German and Indonesian) - 6 slides - Static, we have it
15. church cover - page
16. Offerings - page
    - Small Title: Kollekte
    - Title: MRII Hamburg (rot) & <Second offering purpose in German> (blau)
    - SubTitle: MRII Hamburg (merah) & <Second offering purpose in Indonesian> (biru)
17. Fourth song
18. church cover - page
19. Puji Allah Bapa Putra - page - 3 slides - Static, we have it
20. church cover - page
21. A...Men - page - 1 slide - Static, we have it
22. Annoucement - page - 1 slide - Static
23. Persekutuan Doa - page - 1 slide - Static
24. Seminar - page - 1 slide - Static
25. Ibadah Minggu Depan - page - 1 slide - Static
26. Sekolah Minggu - page - 1 slide - Static
27. Happy Birthday - page - 1 slide - Static
28. Coffee Time - page - 1 slide - Static
    
"""

# Importing libraries
import os
import pptx # pip install python-pptx
from pptx import Presentation
from pptx.util import Inches

from alkitab_scraper import *
from pptx_creator import *
from user_input import *
from Pujian import download_new_song_pipeline

########################################### INPUTS ##########################################
# 1. 4 song's numbers
SONG_NUMBERS = [161, 320, 93, 169]
# 2. Opening Bible verse
OPEN_BIBLE_BOOK = ""
OPEN_BIBLE_CHAPTER = ""
OPEN_BIBLE_VERSE_START = ""
OPEN_BIBLE_VERSE_END = ""
# 3. Pastor's title in Indonesian and German, and name
PASTOR_TITLE_ID = "Pdt."
PASTOR_TITLE_DE = "Pfr."
PASTOR_NAME = "Test"
# 4. Second (blue) offering purpose in Indonesian and German
SECOND_OFFERING_PURPOSE_ID = ["none", "P_PENGINJILAN", "P_SEKOLAH", "P_MANDAT", "P_PEMBANGUNAN", "P_DIAKONIA" ]


########################################### Global variables##########################################
MY_SLIDE_WIDTH = Inches(16)
MY_SIDE_HEIGHT = Inches(9)
CURRENT_DIR = os.path.dirname(__file__)
TEMPLATE_FILE = 'master_slide_template.pptx'


########################################### Functions ##########################################

def processing_answers(data_array):
    # answer = ["161, 320, 93, 169", "Pdt. Billy Kristanto", "Keluaran 16:2-3", "Pfr."]
    global SONG_NUMBERS, PASTOR_TITLE_ID, PASTOR_NAME, OPEN_BIBLE_BOOK, OPEN_BIBLE_CHAPTER, OPEN_BIBLE_VERSE_START, OPEN_BIBLE_VERSE_END, PASTOR_TITLE_DE
    
    SONG_NUMBERS = data_array[0].split(",")
    PASTOR_TITLE_ID = data_array[1].split(" ")[0]
    PASTOR_NAME = data_array[1].split(" ")[1]
    OPEN_BIBLE_BOOK = data_array[2].split(" ")[0]
    OPEN_BIBLE_CHAPTER = data_array[2].split(" ")[1].split(":")[0]
    OPEN_BIBLE_VERSE_START = data_array[2].split(" ")[1].split(":")[1].split("-")[0]
    OPEN_BIBLE_VERSE_END = data_array[2].split(" ")[1].split(":")[1].split("-")[1]
    PASTOR_TITLE_DE = data_array[3]


def main():

    """
    the structure of the slide is
    Presentation -> Layout name -> slide layout -> slide -> shapes -> placeholders
    """

    ##### ask for input from the user UI
    ##### TODO: uncomment this
    # data = ask_for_input()
    # processing_answers(data)

    #### check if all the songs are available locally if not, download from google drive
    for song_number in SONG_NUMBERS:
        # check if the song folder exists
        song_folder_path = os.path.join(CURRENT_DIR, 'Songs', str(song_number))
        if not os.path.exists(song_folder_path):
            # download the song folder from google drive
            download_new_song_pipeline(song_number)

    
    # create a test presentation file
    prs = Presentation(TEMPLATE_FILE)

    # set height and width
    # prs.slide_width = MY_SLIDE_WIDTH
    # prs.slide_height = MY_SIDE_HEIGHT

    # test create_slides_from_folder
    folder_path = os.path.join(CURRENT_DIR, 'Sample', '2', '2')
    # test_insert_slides_from_pict_folder(prs, folder_path)

    #### Slide creation starts here ####
    add_beginning_slide(prs)
    add_church_cover_page(prs)
    # check_placeholders_in_slide_index(prs, 4)

    # add first song
    first_song_folder_path = os.path.join(CURRENT_DIR, 'Songs', str(SONG_NUMBERS[0]))
    insert_slides_from_pict_folder(prs, first_song_folder_path)

    # add_bible_reading_page(prs)
    add_doa_bapa_kami_page(prs)
    add_preacher_page(prs, PASTOR_TITLE_ID, PASTOR_TITLE_DE, PASTOR_NAME)
    add_appostle_creed_page(prs)
    add_secondary_offering_purpose_page(prs, "none") # TODO: change this to the actual offering purpose
    add_bekantmachung_page(prs)

    # save file
    prs.save('test.pptx')


if __name__ == "__main__":
    main()

