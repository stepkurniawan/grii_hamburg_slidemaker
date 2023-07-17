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
import time
import sys
import pptx # pip install python-pptx
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.dml import MSO_THEME_COLOR_INDEX
from pptx.enum.dml import MSO_FILL

########################################### INPUTS ##########################################
# 1. 4 song's numbers
SONG_NUMBERS = []
# 2. Opening Bible verse
OPEN_BIBLE_BOOK = ""
OPEN_BIBLE_CHAPTER = ""
OPEN_BIBLE_VERSE_START = ""
OPEN_BIBLE_VERSE_END = ""
# 3. Pastor's title in Indonesian and German, and name
PASTOR_TITLE_ID = ""
PASTOR_TITLE_DE = ""
PASTOR_NAME = ""
# 4. Second (blue) offering purpose in Indonesian and German
SECOND_OFFERING_PURPOSE_ID = ""
SECOND_OFFERING_PURPOSE_DE = ""


########################################### Global variables##########################################
MY_SLIDE_WIDTH = Inches(16)
MY_SIDE_HEIGHT = Inches(9)
CURRENT_DIR = os.path.dirname(__file__)
TEMPLATE_FILE = 'master_slide_template.pptx'


########################################### Functions ##########################################

def main():

    """
    the structure of the slide is
    Presentation -> Layout name -> slide layout -> slide -> shapes -> placeholders
    """
    
    # create a test presentation file
    prs = Presentation(TEMPLATE_FILE)

    # set height and width
    # prs.slide_width = MY_SLIDE_WIDTH
    # prs.slide_height = MY_SIDE_HEIGHT

    # create a title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    # set the title and subtitle
    title.text = "Hello, World!"
    subtitle.text = "python-pptx was here!"

    # test create_slides_from_folder
    folder_path = os.path.join(CURRENT_DIR, 'Sample', '2', '2')
    # test_insert_slides_from_pict_folder(prs, folder_path)
    add_beginning_slide(prs)
    add_church_cover_page(prs)

    check_placeholders_in_slide_index(prs, 4)
    add_bible_reading_page(prs)

    # save file
    prs.save('test.pptx')

# create slides from this folder. one slide for each file. The folder contains jpg files, and it should be scaled to fit the slide. 
def insert_slides_from_pict_folder(prs, folder_path):
    # get all files in the folder
    files = os.listdir(folder_path)
    # loop through all files
    for file in files:
        # create a new slide
        blank_slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_slide_layout)
        # add image to the slide
        file_path = os.path.join(folder_path, file)
        pic = slide.shapes.add_picture(file_path, Inches(0), Inches(0), width=prs.slide_width, height=prs.slide_height)

def get_slide_layout_from_layout_name(prs,layout_name):
    
    # Specify the layout name you want to use
    slide_layout = None
    for layout in prs.slide_master.slide_layouts:
        if layout.name == layout_name:
            slide_layout = layout
            break

    # Check if the layout was found
    if slide_layout is not None:
        # Add a slide based on the layout
        slide = prs.slides.add_slide(slide_layout)

    return slide

def add_beginning_slide(prs):
    # Specify the layout name you want to use
    layout_name = "beginning" # renamed in the master template pptx file
    get_slide_layout_from_layout_name(prs, layout_name)



def add_church_cover_page(prs):
    # Specify the layout name you want to use
    layout_name = "church_cover" # renamed in the master template pptx file
    get_slide_layout_from_layout_name(prs, layout_name)



def add_bible_reading_page(prs):
    # Find the layout with the specified name
    layout_name_cover = "BIBLE_READING" # renamed in the master template pptx file
    slide_layout_cover = get_slide_layout_from_layout_name(prs, layout_name_cover)
    try: 
        # check_placeholders_in_slide(prs,slide_layout_cover)
        bible_verse = slide_layout_cover.placeholders[10]
        bible_verse.text = "Jesaya 55:6-11" #TOOD: get from input	
    except IndexError:
        print("Invalid placeholder index.")


    bible_verse_layout_name = "BIBLE_VERSE" # renamed in the master template pptx file
    slide_layout_bible_verse = get_slide_layout_from_layout_name(prs, bible_verse_layout_name)
    try:
        print("bible verse layout")
        check_placeholders_in_slide(prs,slide_layout_bible_verse)
        
    except IndexError:
        print("Invalid placeholder index.")
    
    


######## Helper functions ####################################################

def check_placeholders_in_slide_index(prs, layout_index):
    slide = prs.slides.add_slide(prs.slide_layouts[layout_index])
    print('in layout %d :' % layout_index)
    for shape in slide.placeholders:
        if shape.is_placeholder:
            phf = shape.placeholder_format
            print('id: %d, name: %s' % (phf.idx, phf.type))
    print('check done. Remember, the id is more important than the position')

def check_placeholders_in_slide(prs, slide):
    print('in slide %s' % slide)
    for shape in slide.placeholders:
        if shape.is_placeholder:
            phf = shape.placeholder_format
            print('id: %d, name: %s' % (phf.idx, phf.type))
    print('check done. Remember, the id is more important than the position')

#### TEST FUNCTIONS ############################################################

def test_insert_slides_from_pict_folder(prs, folder_path):
    folder_path = os.path.join(CURRENT_DIR, 'Sample', '2', '2')
    insert_slides_from_pict_folder(prs, folder_path)

if __name__ == "__main__":
    main()

