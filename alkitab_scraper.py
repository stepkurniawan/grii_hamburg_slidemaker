"""
this scraper will go to bible.com and then use selenium to search in the search bar some verses
and return a text of that verse
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


def get_ayat_alkitab_dict(book, chapter, verse_start, verse_end, language="ID"):
    """
    this function will return a dictionary of verses from the bible
    input: bible book, chapter, verse_start, verse_end

    output dict= {verse_number: verse_text}
    """
    output_dict= {}
    verse_start = int(verse_start)
    verse_end = int(verse_end)

    # IF INDONESIAN
    if language == "ID":
        # Set up the WebDriver (Edge in this example)
        driver = webdriver.Edge()
        driver.get("https://www.bible.com/bible/306/GEN.1.TB") # link to indonesian bible

    # IF GERMAN
    elif language == "DE":
        # Set up the WebDriver (Edge in this example)
        driver = webdriver.Edge()
        driver.get("https://www.bible.com/bible/51/GEN.1.DELUT")

    # calculate how many verses to get
    verse_count = verse_end - verse_start + 1
    print("There is " + str(verse_count) + " verses ")

    # loop through the verses
    for i in range(verse_count):
        # Find the search input field and enter the verse
        time.sleep(3)
        try:
            search_input = driver.find_element_by_xpath("/html/body/div/div/header/div/div[2]/div/input")
        except:
            search_input = driver.find_element(By.XPATH, "/html/body/div/div/header/div/div[2]/div/input")
        search_input.clear()
        # Clear the text by sending an empty string
        search_input.send_keys(Keys.CONTROL + "a")  # Select all text
        search_input.send_keys(Keys.BACKSPACE)  # Delete the selected text
        current_ayat_alkitab = book + " " + str(chapter) + ":" + str(verse_start + i)
        search_input.send_keys(current_ayat_alkitab)
        search_input.send_keys(Keys.ENTER)

        # Wait for the search results to load (you may need to adjust the time depending on your internet speed)
        time.sleep(3) # Wait for 5 seconds (adjust as needed)

        # Get the search results
        try:
            bible_verse_element = driver.find_element_by_xpath("/html/body/div/div/main/div[1]/div/div/div/div/div[2]/div/div[1]/div/p")
        except:
            try:
                bible_verse_element = driver.find_element(By.XPATH, "/html/body/div/div/main/div[1]/div/div/div/div/div[2]/div/div[1]/div/p")
            except:
                # search by using JS path
                bible_verse_element = driver.find_element(By.CSS_SELECTOR, "p.text-text-light.dark\\:text-text-dark.font-aktiv-grotesk.mbe-1:first-child")

        bible_verse_element_text = bible_verse_element.text
        print(bible_verse_element_text)

        # add the verse to the output array
        output_dict[current_ayat_alkitab] = bible_verse_element_text
        
    # wait until I close it
    # input("Press Enter to continue...")

    # Close the browser
    driver.quit()

    return output_dict
