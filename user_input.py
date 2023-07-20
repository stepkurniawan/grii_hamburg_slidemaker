import tkinter as tk

def ask_for_input():
    global root, entry_song_numbers, entry_pastor_name, entry_votum_bible_verse, entry_pastor_title_de

    # Create the main Tkinter window
    root = tk.Tk()
    root.title("User Input UI")

    # Create labels and entry widgets for user input
    label_song_numbers = tk.Label(root, text="4 song numbers or name:")
    entry_song_numbers = tk.Entry(root, width=30)

    label_pastor_name = tk.Label(root, text="pastor name:")
    entry_pastor_name = tk.Entry(root, width=30)

    label_votum_bible_verse = tk.Label(root, text="votum bible verse:")
    entry_votum_bible_verse = tk.Entry(root, width=30)

    label_pastor_title_de = tk.Label(root, text="pastor title in DE:")
    entry_pastor_title_de = tk.Entry(root, width=30)

    # Create a Submit button
    submit_button = tk.Button(root, text="Submit", command=submit)

    # Pack the labels, entry widgets, and Submit button in the main window
    label_song_numbers.pack()
    entry_song_numbers.pack()

    label_pastor_name.pack()
    entry_pastor_name.pack()

    label_votum_bible_verse.pack()
    entry_votum_bible_verse.pack()

    label_pastor_title_de.pack()
    entry_pastor_title_de.pack()

    submit_button.pack()

    # Run the Tkinter main loop
    root.mainloop()
    return data_array

def submit():
    global data_array

    song_numbers = entry_song_numbers.get().strip()
    pastor_name = entry_pastor_name.get().strip()
    votum_bible_verse = entry_votum_bible_verse.get().strip()
    pastor_title_de = entry_pastor_title_de.get().strip()

    # Do whatever you want with the collected data
    data_array = [song_numbers, pastor_name, votum_bible_verse, pastor_title_de]
    print(data_array)

    # Close the window
    root.destroy()
    return data_array

    
