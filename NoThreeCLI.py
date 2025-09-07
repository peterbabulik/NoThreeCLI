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
    
    keywords = [word for word in query.lower().split() if word]
    results = []

    if keywords:
        current_thread = threading.current_thread()
        for root, dirs, files in os.walk(path, topdown=True):
            if not getattr(current_thread, 'is_active', True):
                return

            dirs[:] = [d for d in dirs if not (d.startswith('.') or d in {'__pycache__', 'node_modules', '.git'})]

            for name in files + dirs:
                full_path = os.path.join(root, name)
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
    
    # --- MAJOR CHANGE #1: Use a timeout instead of nodelay ---
    # This makes getch() a blocking call, which is the key to reducing CPU usage.
    # It will wait for 100ms for a keypress before timing out.
    # stdscr.nodelay(1)  # OLD METHOD: Caused high CPU usage
    stdscr.timeout(100) # NEW METHOD: Low CPU usage
    
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    HIGHLIGHT_STYLE = curses.color_pair(1)

    # --- Application State ---
    query = ''
    results = []
    selected_index = 0
    scroll_top = 0

    while True:
        # --- Handle incoming results from the search thread ---
        # This check now runs approximately 10 times per second instead of continuously.
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
        # This call will now BLOCK, waiting for a key or the 100ms timeout.
        key = stdscr.getch()
        
        # We only process if a key was actually pressed (getch() returns -1 on timeout)
        if key != -1:
            if 32 <= key <= 126:
                query += chr(key)
            elif key in {curses.KEY_BACKSPACE, 127}:
                query = query[:-1]
            elif key == curses.KEY_UP:
                selected_index = max(0, selected_index - 1)
            elif key == curses.KEY_DOWN:
                selected_index = min(len(results) - 1, selected_index + 1)
            elif key in {curses.KEY_ENTER, 10, 13} and results:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.Popen([opener, os.path.dirname(results[selected_index][1])])
            
            # --- Scrolling and Thread Management only happen on a keypress ---
            if selected_index < scroll_top:
                scroll_top = selected_index
            if selected_index >= scroll_top + height - 2:
                scroll_top = selected_index - height + 3

            if 32 <= key <= 126 or key in {curses.KEY_BACKSPACE, 127}:
                if search_thread:
                    search_thread.is_active = False

                if len(query) > 2:
                    search_thread = threading.Thread(target=search_worker, args=(query, os.path.expanduser('~')))
                    search_thread.is_active = True
                    search_thread.start()
                else:
                    results = []
        
        # --- MAJOR CHANGE #2: The manual sleep is no longer needed ---
        # The blocking nature of `stdscr.timeout()` handles the "pausing".
        # time.sleep(0.01) # REMOVED

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        curses.wrapper(main_loop)
    except KeyboardInterrupt:
        pass # The finally block will handle the exit message
    finally:
        print('NoThreeCLI exited.')
