import os
import time
import openai
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

# Note: The openai-python library support for Azure OpenAI is in preview.
openai.api_type = "azure"
openai.api_base = st.secrets["AZURE_OPENAI_ENDPOINT"] 
openai.api_version = "2023-03-15-preview"
openai.api_key = st.secrets["OPENAI_API_KEY_AZURE2"]


bible_id_book = "Keluaran 2:3"
query_id = "Di Alkitab terjemahan baru, isi {} adalah".format(bible_id_book)


def querry_chatGPT(query):
    response = openai.ChatCompletion.create(
        engine="GPT35TURBO",
        messages=[{"role": "system", "content": "You are very introverted AI assistant that answers people questions promptly. You only answer the content of the bible asked, and provides no context nor comments. By default you reference Alkitab Terjemahan Baru if the quesion is in Indonesian, and refer Lutherbibel 1912 if the question is in German. "},
                {"role": "user", "content": "Sebutkan di alkitab terjemahan baru, isi Kejadian 1:1\n"},
                {"role": "assistant",
                    "content": "Pada mulanya Allah menciptakan langit dan bumi."},
                {"role": "user", "content": "in Lutherbibel 1912, was ist Galaters 4 : 5 ? "},
                {"role": "assistant", "content": "auf daß er die, so unter dem Gesetz waren, erlöste, daß wir die Kindschaft empfingen."},
                {"role": "user", "content": "{}".format(query)},],
        temperature=0.0,
        max_tokens=2800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    return response

def get_content_of_bible_from_chatGPT(bible_verses, language="ID"):
    output = ""

    if language == "ID":
        query = "Di Alkitab terjemahan baru, isi {} adalah".format(
            bible_verses)
    elif language == "DE":
        query = "in Lutherbibel 1912, was ist in {} ? Bitte auf Deutsch".format(
            bible_verses)
        
    print("chatGPT is querying: ", query)

    for i in range(3):
        try:
            response = querry_chatGPT(query)
            output = response['choices'][0]['message']['content'] 
            break

        except:
            print("chatGPT failed to query: ", query, "trying again in 3 seconds")
            output = ""
            time.sleep(3)
            continue

    # print(response)
    # print("Isi alkitab" ,response.choices[0].message["content"])
    # output = response.choices[0].message["content"] # old version
    st.write("response", response)

    print("get_content_of_bible_from_chatGPT with this {} was successful".format(bible_verses))

    return output


def get_ayat_alkitab_one_by_one_dict(book, chapter, verse_start : int, verse_end : int, language="ID"):
    output_dict = {}
    verse_start = int(verse_start)
    verse_end = int(verse_end)

    # calculate how many verses to get
    verse_count = verse_end - verse_start + 1
    print("There is " + str(verse_count) + " verses ")


    for i in range(verse_count):
        current_ayat_alkitab = book + " " + str(chapter) + ":" + str(verse_start + i)
        output_dict[current_ayat_alkitab] = get_content_of_bible_from_chatGPT(current_ayat_alkitab, language)

        

    print("get_ayat_alkitab_one_by_one_dict with {} {}:{}-{} was successful".format(book, chapter, verse_start, verse_end))
    return output_dict

# get_ayat_alkitab_one_by_one_dict("Kejadian", 1, 1, 5, "ID")
# get_ayat_alkitab_one_by_one_dict("Galater", 4, 5, 7, "DE")