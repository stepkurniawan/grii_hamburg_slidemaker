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
import streamlit as st
from io import BytesIO


# from alkitab_scraper import *
from pptx_creator import *
# from user_input import *
from Pujian import download_new_song_pipeline
from Pujian import SONGS_FOLDER
from Pujian import download_all_songs
from Pujian import creds
# from Pujian import service
from google_auth import *
from Pujian import *

from footer import footer

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
ADD_ONS_DIR = os.path.join(CURRENT_DIR, "add_ons")

HOME_DIR = os.path.expanduser("~")
DOWNLOAD_FOLDER = os.path.join(HOME_DIR, "Downloads")
# print("HOME_DIR: " + HOME_DIR)

OUTPUT_DIR = os.path.join(DOWNLOAD_FOLDER, "GRII" ,"GRII_Slides")
# OUTPUT_DIR = "C:\\Program Files"
output_file = ""
binary_output_file = BytesIO()

def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        # Running from PyInstaller executable, use sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # Running from source code
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

TEMPLATE_FILE = get_resource_path('master_slide_template.pptx')


########################################### Functions ##########################################


def processing_answers(data_array):
    # answer = ["161, 320, 93, 169", "Pdt. Billy Kristanto", "Keluaran 16:2-3", "Pfr."]
    global SONG_NUMBERS, PASTOR_TITLE_ID, PASTOR_NAME, OPEN_BIBLE_FULL_VERSE, PASTOR_TITLE_DE, SELECTED_SECOND_OFFERING_PURPOSE_ID
    
    SONG_NUMBERS = data_array[0].split(",")
    # remove whitespace
    SONG_NUMBERS = [song_number.strip() for song_number in SONG_NUMBERS]
    OPEN_BIBLE_FULL_VERSE = data_array[1]
    PASTOR_TITLE_ID = data_array[2].split(" ")[0]
    PASTOR_NAME = data_array[2].split(" ")[1] 
    # if there is a third word, then it is the last name
    if len(data_array[2].split(" ")) > 2:
        PASTOR_NAME += " " + data_array[2].split(" ")[2]
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


def create_website():
    # website title
    page_title = "MRII Europe Automatic Slide Maker"

    st.set_page_config( page_icon=":church:", page_title=page_title)

    # website description
    # heading
    st.title(page_title)
    # subheading
    st.subheader("Welcome to ☁️ MRII Europe Automatic Slide Maker")
    st.write("This website is used to create a powerpoint presentation for Sunday service.")
    st.write("It is tweaked for Hamburg Church, which is bilingual (Indonesian and German).")

    # subheading
    st.subheader("How to use this website")
    st.write("1. Enter the song numbers separated by comma on the left sidebar")
    st.write("2. Enter the Bible verse. Feel free to use Indonesian abbreviation like Kej for Kejadian")
    st.write("3. (Optional) Enter the pastor name ")
    st.write("4. (Optional) Enter the pastor title in German ")
    st.write("5. Click the submit button")
    
    # subheading
    st.subheader("Where are the songs?")
    st.write("The songs are downloaded from the database to the server.")
    st.write("It is stored in the folder, in the server: " + SONGS_FOLDER)

    # st.write("The button below can update the songs database. BUT it will take a long time to download all the songs. (couple of hours)")
    # update_song_button = st.button("Update the songs database")
    # if update_song_button:
    #     connect_service_account_streamlit(creds)
    #     download_all_songs()

    st.subheader("Where is the Slide?")
    st.markdown("After the main process is finished, the **Download Button** will appear on the **left sidebar**")
    st.markdown("You can save the slide by clicking on the **Download Button**")
    st.markdown("The file name is the date of the **next Sunday** service")

    # ask for user input as parameters on the side bar
    # ask for song numbers
    st.sidebar.subheader("Song numbers")
    st.sidebar.write("Please enter the song numbers separated by comma")
    st.sidebar.write("Example: 161, 320, 93, 169")
    song_numbers = st.sidebar.text_input("Song numbers")

    # ask for Bible verse
    st.sidebar.subheader("Bible verse")
    st.sidebar.write("Please enter the Bible verse")
    st.sidebar.write("Example: Keluaran 16:2-3")
    bible_verse = st.sidebar.text_input("Bible verse")
    
    # ask for pastor name
    st.sidebar.subheader("Pastor name")
    st.sidebar.write("Please enter the pastor name")
    st.sidebar.write("Default Example: Pdt. Billy Kristanto")
    pastor_name = st.sidebar.text_input("Pastor name")

    # if pastor_name is empty, then use default value
    if pastor_name == "":
        pastor_name = "Pdt. Billy Kristanto"

    # ask for pastor title in German
    st.sidebar.subheader("Pastor title in German")
    st.sidebar.write("Please enter the pastor title in German")
    st.sidebar.write("Default Example: Pfr.")
    # default is Pfr.
    pastor_title_de = st.sidebar.text_input("Pastor title in German")

    # if pastor_title_de is empty, then use default value
    if pastor_title_de == "":
        pastor_title_de = "Pfr."


    # create a submit button
    submit_button = st.sidebar.button("Submit")
    # if submit button is clicked
    if submit_button:
        # send the data to main.py
        # 1. song numbers
        # 2. Bible verse
        # 3. pastor name
        # 4. pastor title in German
        data_array = [song_numbers, bible_verse, pastor_name, pastor_title_de]
        st.write("Data sent to main.py")
        st.write(data_array)
        processing_answers(data_array)
        with st.spinner('Generating the slide...'):
            main()
            st.balloons()
            st.sidebar.success("Slide generated successfully in " + OUTPUT_DIR + ":tada:")

            st.sidebar.download_button(
                label="Download slide!",
                data=binary_output_file.getvalue(),
                file_name=sunday_date("filename")+ ".pptx",
            )

                
    footer()


def main():

    """
    the structure of the slide is
    Presentation -> Layout name -> slide layout -> slide -> shapes -> placeholders
    """

    ########################################### ASKING USER DATA ##########################################
    ##### ask for input from the user UI
    # use this input if not using STREAMLIT
    # data = ask_for_input()
    # processing_answers(data)


    ########################################### CHECKING SONGS ##########################################

    #### check if all the songs are available locally if not, download from google drive
    for song_number in SONG_NUMBERS:
        # check if the song folder exists
        song_folder_path = os.path.join(SONGS_FOLDER, str(song_number))
        if not os.path.exists(song_folder_path):
            # download the song folder from google drive
            download_new_song_pipeline(song_number)

    
    ########################################### CREATE SLIDES ##########################################
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
    first_song_folder_path = os.path.join(SONGS_FOLDER, str(SONG_NUMBERS[0]))
    insert_slides_from_pict_folder(prs, first_song_folder_path)

    add_church_cover_page(prs, sunday_date("slide"))

    # add second song
    print("Adding second song")
    second_song_folder_path = os.path.join(SONGS_FOLDER, str(SONG_NUMBERS[1]))
    insert_slides_from_pict_folder(prs, second_song_folder_path)

    print("Adding bible reading")
    add_bible_reading_page(prs, OPEN_BIBLE_FULL_VERSE) # TODO: uncomment this

    add_church_cover_page(prs, sunday_date("slide"))

    # add third song
    print("Adding third song")
    third_song_folder_path = os.path.join(SONGS_FOLDER, str(SONG_NUMBERS[2]))
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
    fourth_song_folder_path = os.path.join(SONGS_FOLDER, str(SONG_NUMBERS[3]))
    insert_slides_from_pict_folder(prs, fourth_song_folder_path)

    add_church_cover_page(prs, sunday_date("slide"))

    print("Adding Puji Allah Bapa Putra")
    add_doxology_page(prs)

    add_church_cover_page(prs, sunday_date("slide"))

    add_amen_page(prs)

    add_church_cover_page(prs, sunday_date("slide"))

    add_bekantmachung_page(prs)

    try:

        # create the output folder if it doesnt exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print("output folder created")
    except:
        print("cannot create output folder")


    # save presentation as binary output
    prs.save(binary_output_file)
    # save in output folder
    output_file = os.path.join(OUTPUT_DIR, sunday_date("filename") + ".pptx")
    prs.save(output_file)
    print("saved in " + OUTPUT_DIR)




# if __name__ == "__main__":
#     create_website()

