#!/usr/bin/env python3
"""
File Collector GUI Launcher
Launcher script to choose between different GUI versions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class GUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("File Collector - GUI Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create launcher interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Collector", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Choose Your Interface", 
                                  font=('Arial', 12))
        subtitle_label.pack(pady=(0, 30))
        
        # Basic GUI option
        basic_frame = ttk.LabelFrame(main_frame, text="Basic GUI", padding="15")
        basic_frame.pack(fill=tk.X, pady=(0, 15))
        
        basic_desc = ttk.Label(basic_frame, text="""• Simple and clean interface
• Individual file destination mapping
• Basic copy/move operations
• Progress tracking
• Perfect for everyday use""", justify=tk.LEFT)
        basic_desc.pack(anchor=tk.W)
        
        ttk.Button(basic_frame, text="Launch Basic GUI", 
                  command=self.launch_basic_gui,
                  style='Accent.TButton').pack(pady=(10, 0))
        
        # Extended GUI option
        extended_frame = ttk.LabelFrame(main_frame, text="Extended GUI (Pro)", padding="15")
        extended_frame.pack(fill=tk.X, pady=(0, 15))
        
        extended_desc = ttk.Label(extended_frame, text="""• Advanced tabbed interface
• Filter presets and custom patterns
• Batch operations and tools
• Comprehensive logging
• Configuration management
• Professional features""", justify=tk.LEFT)
        extended_desc.pack(anchor=tk.W)
        
        ttk.Button(extended_frame, text="Launch Extended GUI", 
                  command=self.launch_extended_gui,
                  style='Accent.TButton').pack(pady=(10, 0))
        
        # Command line option
        cli_frame = ttk.LabelFrame(main_frame, text="Command Line", padding="15")
        cli_frame.pack(fill=tk.X, pady=(0, 15))
        
        cli_desc = ttk.Label(cli_frame, text="""• Powerful command-line interface
• Automation and scripting support
• Batch processing capabilities
• Configuration files""", justify=tk.LEFT)
        cli_desc.pack(anchor=tk.W)
        
        cli_button_frame = ttk.Frame(cli_frame)
        cli_button_frame.pack(pady=(10, 0))
        
        ttk.Button(cli_button_frame, text="Show CLI Help", 
                  command=self.show_cli_help).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cli_button_frame, text="Open Terminal", 
                  command=self.open_terminal).pack(side=tk.LEFT)
        
        # Web interface option
        web_frame = ttk.LabelFrame(main_frame, text="Web Interface", padding="15")
        web_frame.pack(fill=tk.X)
        
        web_desc = ttk.Label(web_frame, text="""• Browser-based interface
• Cross-platform compatibility
• Generate CLI commands""", justify=tk.LEFT)
        web_desc.pack(anchor=tk.W)
        
        ttk.Button(web_frame, text="Open Web Interface", 
                  command=self.open_web_interface).pack(pady=(10, 0))
        
    def launch_basic_gui(self):
        """Launch the basic GUI"""
        try:
            subprocess.Popen([sys.executable, 'file_collector_gui.py'])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch basic GUI: {e}")
            
    def launch_extended_gui(self):
        """Launch the extended GUI"""
        try:
            subprocess.Popen([sys.executable, 'file_collector_gui_extended.py'])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch extended GUI: {e}")
            
    def show_cli_help(self):
        """Show CLI help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Command Line Help")
        help_window.geometry("700x500")
        help_window.transient(self.root)
        
        # Help content
        help_text = """File Collector - Command Line Interface

BASIC USAGE:
python3 file_collector.py SOURCE_DIR -d DESTINATION_DIR

EXAMPLES:
# Copy all files
python3 file_collector.py /home/user/documents -d /backup/docs

# Copy specific file types
python3 file_collector.py /source -d /dest -e pdf txt docx

# Copy files matching patterns
python3 file_collector.py /source -d /dest -p "*.log" "report_*"

# Dry run (preview only)
python3 file_collector.py /source -d /dest --dry-run

# Move files instead of copying
python3 file_collector.py /source -d /dest -m move

# Preserve directory structure
python3 file_collector.py /source -d /dest --preserve-structure

# Generate detailed report
python3 file_collector.py /source -d /dest --report operation_report.txt

# Use configuration file
python3 file_collector.py /source -d /dest -c config.json

OPTIONS:
-d, --destination    Destination directory (required)
-p, --patterns       File patterns with wildcards
-e, --extensions     File extensions to include
-x, --exclude        Patterns to exclude
--min-size          Minimum file size in bytes
--max-size          Maximum file size in bytes
-m, --mode          Copy mode: copy, move, hardlink
--preserve-structure Preserve directory structure
--dry-run           Preview operation only
-c, --config        Configuration file path
--report            Generate report file
--create-config     Create sample configuration

For more help, see the README.md file."""
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
    def open_terminal(self):
        """Open terminal/command prompt"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['cmd'], cwd=os.getcwd())
            elif os.name == 'posix':  # macOS and Linux
                if sys.platform == 'darwin':  # macOS
                    subprocess.Popen(['open', '-a', 'Terminal', os.getcwd()])
                else:  # Linux
                    # Try different terminal emulators
                    terminals = ['gnome-terminal', 'konsole', 'xterm', 'lxterminal']
                    for terminal in terminals:
                        try:
                            subprocess.Popen([terminal], cwd=os.getcwd())
                            break
                        except FileNotFoundError:
                            continue
                    else:
                        messagebox.showwarning("Warning", "Could not find a terminal emulator")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open terminal: {e}")
            
    def open_web_interface(self):
        """Open web interface"""
        try:
            import webbrowser
            html_file = os.path.abspath('file_collector.html')
            if os.path.exists(html_file):
                webbrowser.open(f'file://{html_file}')
            else:
                messagebox.showerror("Error", "Web interface file not found: file_collector.html")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open web interface: {e}")

def main():
    root = tk.Tk()
    
    # Configure ttk styles
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
    app = GUILauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()