#!/usr/bin/env python3

import os
import sys
import curses
import threading
import subprocess
import time

# --- Globals for thread communication ---
thread_lock = threading.Lock()
results_buffer = None  # The worker thread puts results here
search_thread = None   # A reference to the running thread

def search_worker(query, path):
    """
    Searches the filesystem in a background thread.
    Results are placed in the global `results_buffer`.
    """
    global results_buffer
    
    # Split the user's query into a list of keywords
    keywords = [word for word in query.lower().split() if word]
    results = []

    if keywords:
        # The current thread is passed so we can check if it's been cancelled
        current_thread = threading.current_thread()
        for root, dirs, files in os.walk(path, topdown=True):
            # If the main loop started a new search, this thread is obsolete; stop it.
            if not getattr(current_thread, 'is_active', True):
                return

            # Optimization: Exclude common irrelevant directories
            dirs[:] = [d for d in dirs if not (d.startswith('.') or d in {'__pycache__', 'node_modules', '.git'})]

            # Combine files and dirs for a single loop
            for name in files + dirs:
                full_path = os.path.join(root, name)
                # Match only if the path contains ALL keywords
                if all(word in full_path.lower() for word in keywords):
                    item_type = "[F]" if name in files else "[D]"
                    results.append((item_type, full_path))

    with thread_lock:
        results_buffer = results

def main_loop(stdscr):
    """The main function to draw the UI and handle the event loop."""
    global results_buffer, search_thread
    
    # --- Curses Initialization ---
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Make getch() non-blocking
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    HIGHLIGHT_STYLE = curses.color_pair(1)

    # --- Application State ---
    query = ''
    results = []
    selected_index = 0
    scroll_top = 0

    while True:
        # --- Handle incoming results from the search thread ---
        with thread_lock:
            if results_buffer is not None:
                results = results_buffer
                results_buffer = None
                selected_index = 0
                scroll_top = 0

        # --- Draw the UI ---
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.addstr(0, 0, f'Search: {query}')
        stdscr.hline(1, 0, curses.ACS_HLINE, width)

        for i in range(height - 2):
            list_index = scroll_top + i
            if list_index < len(results):
                item_type, item_path = results[list_index]
                display_text = f'{item_type} {item_path}'[:width - 1]
                style = HIGHLIGHT_STYLE if list_index == selected_index else 0
                stdscr.addstr(i + 2, 0, display_text, style)
        stdscr.refresh()

        # --- Handle User Input ---
        key = stdscr.getch()
        if 32 <= key <= 126:  # Printable characters
            query += chr(key)
        elif key in {curses.KEY_BACKSPACE, 127}:
            query = query[:-1]
        elif key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(results) - 1, selected_index + 1)
        elif key in {curses.KEY_ENTER, 10, 13} and results:
            # Open the selected item's parent directory
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.Popen([opener, os.path.dirname(results[selected_index][1])])
        
        # --- Scrolling Logic ---
        # Scroll up if selection moves above the visible area
        if selected_index < scroll_top:
            scroll_top = selected_index
        # Scroll down if selection moves below the visible area
        if selected_index >= scroll_top + height - 2:
            scroll_top = selected_index - height + 3

        # --- Thread Management: Trigger a new search on text change ---
        if 32 <= key <= 126 or key in {curses.KEY_BACKSPACE, 127}:
            if search_thread:
                search_thread.is_active = False  # Signal the old thread to stop

            if len(query) > 2:
                search_thread = threading.Thread(target=search_worker, args=(query, os.path.expanduser('~')))
                search_thread.is_active = True
                search_thread.start()
            else:
                results = []  # Clear results for short queries
        
        time.sleep(0.01)  # Prevent 100% CPU usage

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        curses.wrapper(main_loop)
    except KeyboardInterrupt:
        print('NoThreeCLI exited.')
    finally:
        print('NoThreeCLI exited.')
