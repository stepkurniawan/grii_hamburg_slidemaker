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
import collections
import collections.abc

import datetime
import os
import sys
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
OPEN_BIBLE_FULL_VERSE = "Kejadian 1:2-3"
# 3. Pastor's title in Indonesian and German, and name
PASTOR_TITLE_ID = "Pdt."
PASTOR_TITLE_DE = "Pfr."
PASTOR_NAME = "Billy Kristanto"
# 4. Second (blue) offering purpose in Indonesian and German
SECOND_OFFERING_PURPOSE_ID = ["NONE", "P_PENGINJILAN", "P_SEKOLAH", "P_MANDAT", "P_PEMBANGUNAN", "P_DIAKONIA" ]
SELECTED_SECOND_OFFERING_PURPOSE_ID = "NONE"

########################################### Global variables##########################################
MY_SLIDE_WIDTH = Inches(16)
MY_SIDE_HEIGHT = Inches(9)
CURRENT_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FILE = os.path.join(CURRENT_DIR, 'master_slide_template.pptx')


########################################### Functions ##########################################

def processing_answers(data_array):
    # answer = ["161, 320, 93, 169", "Pdt. Billy Kristanto", "Keluaran 16:2-3", "Pfr."]
    global SONG_NUMBERS, PASTOR_TITLE_ID, PASTOR_NAME, OPEN_BIBLE_FULL_VERSE, PASTOR_TITLE_DE, SELECTED_SECOND_OFFERING_PURPOSE_ID
    
    SONG_NUMBERS = data_array[0].split(",")
    # remove whitespace
    SONG_NUMBERS = [song_number.strip() for song_number in SONG_NUMBERS]
    PASTOR_TITLE_ID = data_array[1].split(" ")[0]
    PASTOR_NAME = data_array[1].split(" ")[1] 
    # if there is a third word, then it is the last name
    if len(data_array[1].split(" ")) > 2:
        PASTOR_NAME += " " + data_array[1].split(" ")[2]
    OPEN_BIBLE_FULL_VERSE = data_array[2]
    PASTOR_TITLE_DE = data_array[3]

def sunday_date(formatted):
    # save file as with next sunday's date yyyymmdd.pptx
    # Get today's date
    today = datetime.date.today()
    # Calculate the number of days until the next Sunday (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
    days_until_sunday = (6 - today.weekday()) % 7
    # Calculate the date of the next Sunday
    next_sunday = today + datetime.timedelta(days=days_until_sunday)
    if formatted == "filename":
        next_sunday = str(next_sunday).replace("-", "")
    elif formatted == "slide":
        # return 12 July 2020
        next_sunday = str(next_sunday.strftime("%d %B %Y"))
    else:
        next_sunday = next_sunday
        
    return next_sunday

def main():

    """
    the structure of the slide is
    Presentation -> Layout name -> slide layout -> slide -> shapes -> placeholders
    """

    ##### ask for input from the user UI
    data = ask_for_input()
    processing_answers(data)

    #### check if all the songs are available locally if not, download from google drive
    for song_number in SONG_NUMBERS:
        # check if the song folder exists
        song_folder_path = os.path.join(CURRENT_DIR, 'Songs', str(song_number))
        if not os.path.exists(song_folder_path):
            # download the song folder from google drive
            download_new_song_pipeline(song_number)

    
    # create a test presentation file
    prs = Presentation(TEMPLATE_FILE)

    ##### TESTING PURPOSE test create_slides_from_folder
    # folder_path = os.path.join(CURRENT_DIR, 'Sample', '2', '2')
    # test_insert_slides_from_pict_folder(prs, folder_path)

    #### Slide creation starts here ####
    add_beginning_slide(prs)
    add_church_cover_page(prs, sunday_date("slide"))
    # check_placeholders_in_slide_index(prs, 4)

    # add first song
    print("Adding first song")
    first_song_folder_path = os.path.join(CURRENT_DIR, 'Songs', str(SONG_NUMBERS[0]))
    insert_slides_from_pict_folder(prs, first_song_folder_path)

    add_church_cover_page(prs, sunday_date("slide"))

    # add second song
    print("Adding second song")
    second_song_folder_path = os.path.join(CURRENT_DIR, 'Songs', str(SONG_NUMBERS[1]))
    insert_slides_from_pict_folder(prs, second_song_folder_path)

    print("Adding bible reading")
    add_bible_reading_page(prs, OPEN_BIBLE_FULL_VERSE)

    add_church_cover_page(prs, sunday_date("slide"))

    # add third song
    print("Adding third song")
    third_song_folder_path = os.path.join(CURRENT_DIR, 'Songs', str(SONG_NUMBERS[2]))
    insert_slides_from_pict_folder(prs, third_song_folder_path)

    add_church_cover_page(prs, sunday_date("slide"))

    print("Adding Lord's Prayer")
    add_doa_bapa_kami_page(prs)

    add_church_cover_page(prs, sunday_date("slide"))

    print("Adding Preacher")
    add_preacher_page(prs, PASTOR_TITLE_ID, PASTOR_TITLE_DE, PASTOR_NAME)

    add_church_cover_page(prs, sunday_date("slide"))

    print("Adding Apostles' Creed")
    add_appostle_creed_page(prs)

    add_church_cover_page(prs, sunday_date("slide"))

    print("Adding Offerings")
    secondary_purpose_id = decide_offering_purpose_layout_name(sunday_date("date"))
    add_secondary_offering_purpose_page(prs, secondary_purpose_id) 

    # add fourth song
    print("Adding fourth song")
    fourth_song_folder_path = os.path.join(CURRENT_DIR, 'Songs', str(SONG_NUMBERS[3]))
    insert_slides_from_pict_folder(prs, fourth_song_folder_path)

    add_church_cover_page(prs, sunday_date("slide"))

    print("Adding Puji Allah Bapa Putra")
    add_doxology_page(prs)

    add_church_cover_page(prs, sunday_date("slide"))

    add_amen_page(prs)

    add_church_cover_page(prs, sunday_date("slide"))

    add_bekantmachung_page(prs)

    output_folder = os.path.join(CURRENT_DIR, 'Output')
    # save in output folder
    prs.save(os.path.join(output_folder, sunday_date("filename") + ".pptx"))


if __name__ == "__main__":
    main()

