
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