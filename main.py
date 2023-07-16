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
2. International Reformed Evangelical Church - page (Static)
3. First song
4. International Reformed Evangelical Church - page
5. Second song
6. Opening Bible vers (in German), ex: Subtitel: Bibellesung, Titel: Jesaja 43,1-7 
    - German Translation with the verse number
    - Indonesian Translation with the verse number
7. International Reformed Evangelical Church - page
8. Third song
9. International Reformed Evangelical Church - page
10. Lord's Prayer (in German and Indonesian) -  3 slides - Static, we have it
11. International Reformed Evangelical Church - page
12. Predigt - page
    - Title: <Pastor's title in German>. <Pastor's name>
    - Subtitle: <Pastor's title in Indonesian>. <Pastor's name>
13. International Reformed Evangelical Church - page
14. Apostles' Creed (in German and Indonesian) - 6 slides - Static, we have it
15. International Reformed Evangelical Church - page
16. Offerings - page
    - Small Title: Kollekte
    - Title: MRII Hamburg (rot) & <Second offering purpose in German> (blau)
    - SubTitle: MRII Hamburg (merah) & <Second offering purpose in Indonesian> (biru)
17. Fourth song
18. International Reformed Evangelical Church - page
19. Puji Allah Bapa Putra - page - 3 slides - Static, we have it
20. International Reformed Evangelical Church - page
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
import sys
import pptx
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.dml import MSO_THEME_COLOR_INDEX
from pptx.enum.dml import MSO_FILL


# Global variables
MY_SLIDE_WIDTH = Inches(16)
MY_SIDE_HEIGHT = Inches(9)


def main():
    
    # create a test presentation file
    prs = Presentation()

    # create a title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    # set the title and subtitle
    title.text = "Hello, World!"
    subtitle.text = "python-pptx was here!"

    # set height and width
    prs.slide_width = MY_SLIDE_WIDTH
    prs.slide_height = MY_SIDE_HEIGHT


    # save file
    
    prs.save('test.pptx')

# create slides from this folder. one slide for each file. The folder contains jpg files, and it should be scaled to fit the slide. 
def create_slides_from_folder(prs, folder_path):
    # get all files in the folder
    files = os.listdir(folder_path)
    # loop through all files
    for file in files:
        # create a new slide
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        # add image to the slide
        pic = slide.shapes.add_picture(folder_path + file, Inches(0), Inches(0), width=prs.slide_width, height=prs.slide_height)
    # save the file
    prs.save('test.pptx')

if __name__ == "__main__":
    main()
