import os
# from alkitab_scraper import get_ayat_alkitab_dict
from pptx.util import Inches
from bible_translation import indonesian_to_german_bible
from bible_translation import lai_abbre_to_full
from Bible_API import get_verses_dict

def sort_by_number(file_name):
    # Custom sorting function to extract numbers from the file name and sort numerically
    key = int(''.join(filter(str.isdigit, file_name)))
    return key

# create slides from this folder. one slide for each file. The folder contains jpg files, and it should be scaled to fit the slide. 
def insert_slides_from_pict_folder(prs, folder_path):
    # get all files in the folder
    files = sorted(os.listdir(folder_path), key=sort_by_number)

    # loop through all files (picture only) can be png, jpg, jpeg, etc, or it can also be uppercase
    # it has to be sorted by name
    for file in files:
        # check if the file is a picture
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".JPG") or file.endswith(".PNG") or file.endswith(".JPEG"):
            # create a new slide
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            # add the picture to the slide
            pic = slide.shapes.add_picture(os.path.join(folder_path, file), Inches(0), Inches(0), height=prs.slide_height, width=prs.slide_width)

def add_slide_layout_from_layout_name(prs,layout_name):
    # Specify the layout name you want to use
    slide = None
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
    add_slide_layout_from_layout_name(prs, layout_name)



def add_church_cover_page(prs, sunday_date):
    # Specify the layout name you want to use
    layout_name = "COVER_2" # renamed in the master template pptx file
    
    # print("cover layout")
    slide_layout = add_slide_layout_from_layout_name(prs, layout_name)
    # check_placeholders_in_slide(prs,slide_layout)

    sundays_date_placeholder = slide_layout.placeholders[10]
    sundays_date_placeholder.text = sunday_date
    



def get_full_book_name(book_name):
    # if bible_book has less than 4 characters, then its the abbreviated version. the full version is in lai_abbre_to_full dictionary
    output = ""

    if len(book_name) < 4:
        output = lai_abbre_to_full[book_name]
    # if bible_book has 4 characters, but the first one is a number, then its the abbreviated version. the full version is in lai_abbre_to_full dictionary
    elif book_name[0].isdigit() & (len(book_name) == 4):
        output = lai_abbre_to_full[book_name]
    else:
        output = book_name
    return output

def add_bible_reading_page(prs, bible_verse_text = "Kejadian 1:2-3"):
    # Find the layout with the specified name
    layout_name_cover = "BIBLE_READING" # renamed in the master template pptx file
    slide_layout_cover = add_slide_layout_from_layout_name(prs, layout_name_cover)
    bible_book_ID = ""
    bible_book_DE = ""

    try: 
        # check_placeholders_in_slide(prs,slide_layout_cover)
        bible_verse = slide_layout_cover.placeholders[10]
        bible_verse.text = bible_verse_text 
    except IndexError:
        print("Invalid placeholder index.")

    # if bible_verse is started with a number, ex: 2 Sam 1:1, then the bible_book is "2 Sam", and not just "2"
    # normal example: Kej 1:1
    # bible_book = kej
    # bible_chapter = 1
    # bible_verse_start = 1
    # bible_verse_end = 1

    # special example: 2 Sam 1:1
    # bible_book = 2 Sam
    # bible_chapter = 1
    # bible_verse_start = 1
    # bible_verse_end = 1

    if bible_verse_text.split(" ")[0].isdigit():
        bible_book = bible_verse_text.split(" ")[0] + " " + bible_verse_text.split(" ")[1]
        bible_chapter = bible_verse_text.split(" ")[2].split(":")[0]
        bible_verse_start = bible_verse_text.split(" ")[2].split(":")[1].split("-")[0]
        bible_verse_end = bible_verse_text.split(" ")[2].split(":")[1].split("-")[1]
    else:
        bible_book = bible_verse_text.split(" ")[0]
        bible_chapter = bible_verse_text.split(" ")[1].split(":")[0]
        bible_verse_start = bible_verse_text.split(" ")[1].split(":")[1].split("-")[0]
        bible_verse_end = bible_verse_text.split(" ")[1].split(":")[1].split("-")[1]

    bible_book_ID = get_full_book_name(bible_book)

    # get the bible verse in german
    # bible_book_DE = indonesian_to_german_bible.get(bible_book_ID)

    id_bible_verse = get_verses_dict(bible_book_ID, bible_chapter, bible_verse_start, bible_verse_end, "ID") 
    de_bible_verse = get_verses_dict(bible_book_ID, bible_chapter, bible_verse_start, bible_verse_end, "DE")

    # count how many verse 
    verse_count = len(id_bible_verse)

    # loop so we add slide for each verse
    for id_key, de_key in zip(id_bible_verse.keys(), de_bible_verse.keys()):
        bible_verse_layout_name = "BIBLE_VERSE" # renamed in the master template pptx file
        slide_layout_bible_verse = add_slide_layout_from_layout_name(prs, bible_verse_layout_name)
        try:
            # print("bible verse layout")
            # check_placeholders_in_slide(prs,slide_layout_bible_verse)
            de_bible_verse_placeholder = slide_layout_bible_verse.placeholders[10]
            id_bible_verse_placeholder = slide_layout_bible_verse.placeholders[11]

            # Get the values corresponding to the current keys
            de_value = de_bible_verse[de_key]
            id_value = id_bible_verse[id_key]

            de_bible_verse_placeholder.text = de_key + " : " + de_value
            id_bible_verse_placeholder.text = id_key + " : " + id_value
            
        except IndexError:
            print("Invalid placeholder index.")
    



def add_doa_bapa_kami_page(prs):
    add_slide_layout_from_layout_name(prs, "BAPA_KAMI_1")
    add_slide_layout_from_layout_name(prs, "BAPA_KAMI_2")
    add_slide_layout_from_layout_name(prs, "BAPA_KAMI_3")




def add_preacher_page(prs, PASTOR_TITLE_ID, PASTOR_TITLE_DE, PASTOR_NAME):
    layout_name = "PREACHER" # renamed in the master template pptx file
    slide_layout = add_slide_layout_from_layout_name(prs, layout_name)

    print("preacher layout")
    # check_placeholders_in_slide(prs,slide_layout)

    de_preacher_placeholder = slide_layout.placeholders[10]
    id_preacher_placeholder = slide_layout.placeholders[11]

    de_preacher_placeholder.text = PASTOR_TITLE_DE + " " + PASTOR_NAME
    id_preacher_placeholder.text = PASTOR_TITLE_ID + " " + PASTOR_NAME




def add_appostle_creed_page(prs):
    #loop and search for layout with the name "0_APOSTLE_CREED_1", "1_APOSTLE_CREED_1" until "5_APOSTLE_CREED_1"
    for i in range(0,6):
        layout_name = str(i) + "_APOSTLE_CREED_1"
        slide_layout = add_slide_layout_from_layout_name(prs, layout_name)
        print( str(i) + " apostle creed layout")

def decide_offering_purpose_layout_name(next_sunday_date):
    # if next sunday is the first sunday of the month, then its "P_PENGINJILAN"
    # second sunday, then its "P_SEKOLAH"
    # third sunday, then its "P_MANDAT"
    # fourth sunday, then its "P_PEMBANGUNAN"
    # fifth sunday, then its "P_DIAKONIA"
    output = ""
    if next_sunday_date.day <= 7:
        output = "P_PENGINJILAN"
    elif next_sunday_date.day <= 14:
        output = "P_SEKOLAH"
    elif next_sunday_date.day <= 21:
        output = "P_MANDAT"
    elif next_sunday_date.day <= 28:
        output = "P_PEMBANGUNAN"
    else:
        output = "P_DIAKONIA"
    return output
    

def add_secondary_offering_purpose_page(prs, offering_purpose):
    # if offering_purpose is P_PENGINJILAN, then add slide with layout name "P_PENGINJILAN"
    # if offering_purpose is P_SEKOLAH, then add slide with layout name "P_SEKOLAH"
    layout_name = offering_purpose
    slide_layout = add_slide_layout_from_layout_name(prs, layout_name)




def add_doxology_page(prs):
    add_slide_layout_from_layout_name(prs, "0_DOXOLOGY")
    add_slide_layout_from_layout_name(prs, "1_DOXOLOGY")
    add_slide_layout_from_layout_name(prs, "2_DOXOLOGY")

def add_amen_page(prs):
    add_slide_layout_from_layout_name(prs, "3_DOXOLOGY")



def add_bekantmachung_page(prs):
    for i in range(0,7): # 0,1,2,3,4,5,6
        layout_name = "WARTA_" + str(i) 
        add_slide_layout_from_layout_name(prs, layout_name)






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
    folder_path = os.path.join(os.path.dirname(__file__), 'Sample', '2', '2')
    insert_slides_from_pict_folder(prs, folder_path)