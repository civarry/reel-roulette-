import tkinter as tk
from tkinter import ttk, messagebox
import requests
import webbrowser
import random

def make_api_request(endpoint):
    url = f"https://moviesminidatabase.p.rapidapi.com/{endpoint}"
    headers = {
        "X-RapidAPI-Key": "9b5feae1bcmshebad18bb555bdafp1d8685jsn66213597b831",
        "X-RapidAPI-Host": "moviesminidatabase.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_movies(event=None):
    genre = genre_var.get()
    try:
        movies_by_genre = make_api_request(f"movie/byGen/{genre}")
    except KeyError:
        movie_list.delete(0, tk.END)
        movie_list.insert(tk.END, "No movies found.")
        return
    
    movie_list.delete(0, tk.END)
    for movie_info in movies_by_genre.get('results', []):
        title = movie_info.get('title', 'N/A')
        movie_list.insert(tk.END, title)

def open_movie_link_double_click(event):
    selected_index = movie_list.curselection()
    if selected_index:
        title = movie_list.get(selected_index[0])
        title_with_hyphen = title.replace(" ", "-")
        url = f"https://sflix.to/search/{title_with_hyphen}"
        webbrowser.open(url)

def fetch_all_genres():
    try:
        list_genres = make_api_request("genres")
    except KeyError:
        list_genres = None
    return list_genres

def random_suggestion(root):
    list_genres = fetch_all_genres()

    if not list_genres or "results" not in list_genres:
        movie_list.delete(0, tk.END)
        movie_list.insert(tk.END, "No genres found.")
        return

    random_genre = random.choice(list_genres['results'])['genre']

    # Show the loading indicator while fetching movies
    movie_list.delete(0, tk.END)
    movie_list.insert(tk.END, "Loading...")
    root.update()

    try:
        movies_by_genre = make_api_request(f"movie/byGen/{random_genre}")
    except KeyError:
        movie_list.delete(0, tk.END)
        movie_list.insert(tk.END, "No movies found.")
        return

    if "results" not in movies_by_genre:
        movie_list.delete(0, tk.END)
        movie_list.insert(tk.END, "No movies found.")
        return

    # Check if there are at least 10 movies available for the random genre
    if len(movies_by_genre['results']) >= 10:
        random_movies = random.sample(movies_by_genre['results'], 10)
    else:
        random_movies = movies_by_genre['results']

    movie_list.delete(0, tk.END)
    for movie_info in random_movies:
        title = movie_info.get('title', 'N/A')
        movie_list.insert(tk.END, title)
    
    top_genre_label.config(text=f"Top 10 Movies: {random_genre}")

def top_10_latest_movies():
    try:
        list_movies = make_api_request("movie")
    except KeyError:
        movie_list.delete(0, tk.END)
        movie_list.insert(tk.END, "No movies found.")
        return
    
    if "results" not in list_movies:
        movie_list.delete(0, tk.END)
        movie_list.insert(tk.END, "No movies found.")
        return

    top_10_movies = sorted(list_movies['results'], key=lambda x: x.get('year', 0), reverse=True)[:10]
    movie_list.delete(0, tk.END)
    for movie_info in top_10_movies:
        title = movie_info.get('title', 'N/A')
        movie_list.insert(tk.END, title)
    
    top_genre_label.config(text="Top 10 Movies: Latest Releases")

def add_to_watchlist():
    selected_index = movie_list.curselection()
    if selected_index:
        title = movie_list.get(selected_index[0])
        if title not in watchlist:
            watchlist.append(title)
            messagebox.showinfo("Watchlist", f"{title} added to the watchlist.")
            save_watchlist_to_file()
        else:
            messagebox.showinfo("Watchlist", f"{title} is already in the watchlist.")

def show_watchlist():
    global watchlist
    if not watchlist:
        messagebox.showinfo("Watchlist", "Your watchlist is empty.")
        return

    def mark_as_done(event):
        selected_index = watchlist_listbox.curselection()
        if selected_index:
            selected_movie = watchlist_listbox.get(selected_index[0])
            if selected_movie.startswith("✓ "):
                selected_movie = selected_movie[2:]
            else:
                selected_movie = "✓ " + selected_movie

            watchlist[watchlist.index(watchlist_listbox.get(selected_index[0]))] = selected_movie

            update_watchlist_display()
            save_watchlist_to_file()

    def open_movie_link():
        selected_index = watchlist_listbox.curselection()
        if selected_index:
            title = watchlist_listbox.get(selected_index[0])
            if title.startswith("✓ "):
                title = title[2:]  # Remove the checkmark
            title_with_hyphen = title.replace(" ", "-")
            url = f"https://sflix.to/search/{title_with_hyphen}"
            webbrowser.open(url)

    def remove_from_watchlist():
        selected_index = watchlist_listbox.curselection()
        if selected_index:
            selected_movie = watchlist_listbox.get(selected_index[0])
            if selected_movie.startswith("✓ "):
                selected_movie = selected_movie[2:]
            watchlist.remove(selected_movie)
            update_watchlist_display()
            save_watchlist_to_file()

    def update_watchlist_display():
        watchlist_listbox.delete(0, tk.END)  # Clear the listbox
        for movie in watchlist:
            watchlist_listbox.insert(tk.END, movie)

    watchlist_window = tk.Toplevel(root)
    watchlist_window.title("Watchlist")
    watchlist_window.geometry("400x400")
    watchlist_window.configure(bg="#FFFFFF")

     # Configure row and column weights for the grid
    watchlist_window.grid_rowconfigure(1, weight=1)
    watchlist_window.grid_columnconfigure(0, weight=1)

    watchlist_label = ttk.Label(watchlist_window, text="Your Watchlist:", font=("Arial", 14, "bold"))
    watchlist_label.grid(row=0, column=0, columnspan=2, pady=10)

    watchlist_listbox = tk.Listbox(watchlist_window, selectmode=tk.SINGLE)
    watchlist_listbox.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)


    for movie in watchlist:
        watchlist_listbox.insert(tk.END, movie)

    # Bind double click event to mark_as_done function
    watchlist_listbox.bind("<Double-Button-1>", mark_as_done)

    # Add "View Link" button using grid
    view_link_button = ttk.Button(watchlist_window, text="View Link", command=open_movie_link)
    view_link_button.grid(row=2, column=0, pady=10, sticky=tk.NSEW)

    # Add "Remove" button using grid
    remove_button = ttk.Button(watchlist_window, text="Remove", command=remove_from_watchlist)
    remove_button.grid(row=2, column=1, pady=10, sticky=tk.NSEW)

def save_watchlist_to_file():
    with open("watchlist.txt", "w", encoding="utf-8") as file:
        for movie in watchlist:
            file.write(f"{movie}\n")

def load_watchlist_from_file():
    try:
        with open("watchlist.txt", "r", encoding="utf-8") as file:
            for line in file:
                movie = line.strip()
                watchlist.append(movie)
    except FileNotFoundError:
        pass

def main():
    global genre_var, movie_list, top_genre_label, root, watchlist
    watchlist = []

    load_watchlist_from_file()

    root = tk.Tk()
    root.title("Reel Roulette")
    
    # Set the window size and position it at the center of the screen
    width = 800
    height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Use grid layout for responsiveness
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Style configuration for modern look
    style = ttk.Style()
    style.theme_use('default')  # Choose a modern theme (clam, alt, default, etc.)

    style.configure('TLabel', background='#FFFFFF', foreground='#263238', font=("Arial", 12))
    style.configure('TCombobox', background='#37474F', foreground='#263238', font=("Arial", 12))
    style.configure('TListbox', background='#37474F', foreground='#263238', font=("Arial", 14), selectbackground='#0D47A1', selectforeground='#FFFFFF')
    style.configure('TButton', background='#0D47A1', foreground='#FFFFFF', font=("Arial", 12))  # Changed button color

    top_genre_label = ttk.Label(root, text="", font=("Arial", 12, "bold"))
    top_genre_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")

    genre_placeholder = "Select Genre"
    genre_var = tk.StringVar()
    genre_dropdown = ttk.Combobox(root, textvariable=genre_var, width=20, values=[], state="readonly")
    genre_dropdown.grid(row=0, column=0, columnspan=3, pady=5, padx=5, sticky="e")

    genre_dropdown.set(genre_placeholder)  # Set the initial placeholder text

    list_genres = fetch_all_genres()
    if list_genres and "results" in list_genres:
        genre_choices = [genre_info['genre'] for genre_info in list_genres['results']]
        genre_dropdown['values'] = genre_choices

    genre_dropdown.bind("<<ComboboxSelected>>", fetch_movies)
    
    movie_list = tk.Listbox(root, width=80, selectmode=tk.SINGLE)
    movie_list.grid(row=1, column=0, columnspan=3, pady=5, padx=5, sticky="news")

    # Bind open_movie_link_double_click function to the double-click event of movie_list
    movie_list.bind("<Double-Button-1>", open_movie_link_double_click)

    # Add "Random Suggestion and Top 10 Movies" button
    btn_suggestion = ttk.Button(root, text="Random Suggestion and Top 10 Movies", command=lambda: random_suggestion(root), width=30)
    btn_suggestion.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")

    # Add to Watchlist and Show Watchlist buttons in the same column
    add_to_watchlist_button = ttk.Button(root, text="Add to Watchlist", command=add_to_watchlist, width=20)
    add_to_watchlist_button.grid(row=2, column=1, pady=5, padx=5, sticky="nsew")

    show_watchlist_button = ttk.Button(root, text="Show Watchlist", command=show_watchlist, width=20)
    show_watchlist_button.grid(row=2, column=2, pady=5, padx=5, sticky="nsew")

    # Set resizable to False in both directions
    root.resizable(False, False)
    root.configure(bg="#FFFFFF")
    root.mainloop()

if __name__ == "__main__":
    main()

