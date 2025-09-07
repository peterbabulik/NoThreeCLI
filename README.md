# NoThreeCLI

> A lightning-fast, CPU-silent, interactive file searcher for your terminal.

NoThreeCLI is a powerful yet simple tool designed to find files and folders on your system instantly. It combines the speed of a command-line utility with the interactive feel of a modern application, all without leaving your terminal.

## ✨ Features

*   **Instantaneous Results:** Live, as-you-type search that starts delivering results in milliseconds.
*   **Powerful Multi-Keyword Search:** Find any file or folder by typing parts of its name and parts of its path. For example, `report Q3` will find `/home/user/documents/2025/Quarterly_Report_Q3.pdf`.
*   **Zero Dependencies:** Written in pure Python 3 using only standard libraries. No `pip install` needed. It just works.
*   **Hyper-Efficient:** Uses a non-blocking, event-driven model that consumes **~0% CPU** when idle. Your laptop battery will thank you.
*   **Interactive TUI:** Uses a clean, intuitive Text-based User Interface that you can navigate with your keyboard.
*   **Smart & Simple:** Automatically excludes hidden files and common clutter like `node_modules` and `.git` to keep results relevant.

## ⚙️ Requirements

*   **Python 3** (typically pre-installed on Linux and macOS)
*   A terminal that supports `curses` (most terminals do).

## 🚀 Installation

Installation is just two steps:

1.  **Download the script:**
    Save the code as a file named `NoThreeCLI.py`.

2.  **Make it executable:**
    Open your terminal and run this command to grant execution permissions:
    ```bash
    chmod +x NoThreeCLI.py
    ```

That's it! You can now move the `NoThreeCLI` file to a directory in your `$PATH` (like `/usr/local/bin`) to make it runnable from anywhere.

## ⌨️ Usage

Simply run the script from your terminal:

```bash
./NoThreeCLI.py
```

The application will launch, taking over your terminal screen.

### Controls

| Key           | Action                                        |
| :------------ | :-------------------------------------------- |
| **Any Text**  | Type to search live.                          |
| **Backspace** | Delete characters from your search query.     |
| **Up Arrow**  | Move selection up.                            |
| **Down Arrow**| Move selection down.                          |
| **Enter**     | Open the parent folder of the selected item.  |
| **Ctrl+C**    | Exit the application.                         |

## 🛠️ How It Works

NoThreeCLI achieves its high performance and low resource usage through two key Python libraries:
1.  **`curses`**: Renders the entire interactive interface within the terminal, handling all drawing and user input efficiently.
2.  **`threading`**: The file search (`os.walk`) runs in a separate background thread, ensuring the UI never freezes, even while searching massive directories. The main loop is event-driven (`stdscr.timeout`), which allows it to sleep when there is no user input, dropping CPU usage to zero.

---
