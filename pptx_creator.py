from alkitab_scraper import *


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



def add_church_cover_page(prs):
    # Specify the layout name you want to use
    layout_name = "church_cover" # renamed in the master template pptx file
    add_slide_layout_from_layout_name(prs, layout_name)



def add_bible_reading_page(prs):
    # Find the layout with the specified name
    layout_name_cover = "BIBLE_READING" # renamed in the master template pptx file
    slide_layout_cover = add_slide_layout_from_layout_name(prs, layout_name_cover)
    try: 
        # check_placeholders_in_slide(prs,slide_layout_cover)
        bible_verse = slide_layout_cover.placeholders[10]
        bible_verse.text = "Jesaya 55:6-11" #TOOD: get from input	
    except IndexError:
        print("Invalid placeholder index.")

    id_bible_verse = get_ayat_alkitab_dict("Kejadian", 2, 1, 5, "ID") #TDOD: get from input
    de_bible_verse = get_ayat_alkitab_dict("Kejadian", 2, 1, 5, "DE") #TDOD: get from input

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
    check_placeholders_in_slide(prs,slide_layout)

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

def add_secondary_offering_purpose_page(prs, offering_purpose):
    # if offering_purpose is P_PENGINJILAN, then add slide with layout name "P_PENGINJILAN"
    # if offering_purpose is P_SEKOLAH, then add slide with layout name "P_SEKOLAH"
    layout_name = offering_purpose
    slide_layout = add_slide_layout_from_layout_name(prs, layout_name)

def add_doxology_page(prs):
    add_slide_layout_from_layout_name(prs, "0_DOXOLOGY")
    add_slide_layout_from_layout_name(prs, "1_DOXOLOGY")
    add_slide_layout_from_layout_name(prs, "2_DOXOLOGY")
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
    folder_path = os.path.join(CURRENT_DIR, 'Sample', '2', '2')
    insert_slides_from_pict_folder(prs, folder_path)