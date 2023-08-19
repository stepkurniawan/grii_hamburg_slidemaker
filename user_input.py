import tkinter as tk

DEFAULT_PASTOR_NAME = "Pdt. Billy Kristanto"
DEFAULT_PASTOR_TITLE_DE = "Pfr."

def ask_for_input():
    global root, entry_song_numbers, entry_pastor_name, entry_votum_bible_verse, entry_pastor_title_de, data_array

    # Create the main Tkinter window
    # V1.4 : using bible API to get bible verses
    # V2.0 : adding choice for english or german song
    root = tk.Tk()
    root.title("GRII Slide Maker - A1 V2.0") 

    root.option_add("*Font", "Helvetica 24")

    # Create labels and entry widgets for user input
    label_song_numbers = tk.Label(root, text="4 song numbers or name: [161, 320, 93, 169]")
    entry_song_numbers = tk.Entry(root, width=30)

    label_votum_bible_verse = tk.Label(root, text="votum bible verse: [2Sam 1:2-3]")
    entry_votum_bible_verse = tk.Entry(root, width=30)

    label_pastor_name = tk.Label(root, text="pastor name: [Pdt. Billy Kristanto]")
    entry_pastor_name = tk.Entry(root, width=30)

    label_pastor_title_de = tk.Label(root, text="pastor title in DE: [Pfr.]")
    entry_pastor_title_de = tk.Entry(root, width=30)

    # Create a Submit button
    submit_button = tk.Button(root, text="Submit", command=submit)

    # Pack the labels, entry widgets, and Submit button in the main window
    label_song_numbers.pack()
    entry_song_numbers.pack()

    label_votum_bible_verse.pack()
    entry_votum_bible_verse.pack()

    label_pastor_name.pack()
    entry_pastor_name.pack()

    label_pastor_title_de.pack()
    entry_pastor_title_de.pack()

    submit_button.pack()

    # Bind the Return key press event to the submit function
    root.bind('<Return>', lambda event: submit())

    # Run the Tkinter main loop
    root.mainloop()

    # if entry_pastor_name and / or entry_pastor_title_de is/are empty, then use default value
    try:
        if entry_pastor_name.get().strip() == "":
            entry_pastor_name.insert(0, DEFAULT_PASTOR_NAME)
    except tk.TclError:
        # The widget has been destroyed (window was closed), handle gracefully with default value
        data_array[1] = DEFAULT_PASTOR_NAME

    try:
        if entry_pastor_title_de.get().strip() == "":
            entry_pastor_title_de.insert(0, DEFAULT_PASTOR_TITLE_DE)
    except tk.TclError:
        # The widget has been destroyed (window was closed), handle gracefully with default value
        data_array[3] = DEFAULT_PASTOR_TITLE_DE

    return data_array
    

def submit():
    global data_array

    song_numbers = entry_song_numbers.get().strip()
    votum_bible_verse = entry_votum_bible_verse.get().strip()
    pastor_name = entry_pastor_name.get().strip()
    pastor_title_de = entry_pastor_title_de.get().strip()

    # Do whatever you want with the collected data
    data_array = [song_numbers, pastor_name, votum_bible_verse, pastor_title_de ]
    print(data_array)

    # Close the window
    root.destroy()

    
    return data_array

    
