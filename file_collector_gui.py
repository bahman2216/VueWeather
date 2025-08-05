#!/usr/bin/env python3
"""
File Collector GUI Application
A visual interface for collecting and copying files with individual destination control.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
import shutil
import threading
import json
from pathlib import Path
from datetime import datetime
import logging
import sys

class FileCollectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Collector - GUI")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Data storage
        self.file_mappings = []  # List of {'source': path, 'destination': path, 'selected': bool}
        self.config = self.load_config()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize GUI
        self.setup_styles()
        self.create_widgets()
        self.bind_events()
        
    def setup_logging(self):
        """Setup logging for the GUI application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_collector_gui.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load configuration from file"""
        try:
            config_file = 'file_collector_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load config: {e}")
        
        return {
            'default_destination': str(Path.home() / 'collected_files'),
            'preserve_structure': False,
            'copy_mode': 'copy',
            'window_geometry': '1200x800'
        }
    
    def save_config(self):
        """Save current configuration"""
        try:
            self.config['window_geometry'] = self.root.geometry()
            with open('file_collector_config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def setup_styles(self):
        """Setup ttk styles for better appearance"""
        style = ttk.Style()
        
        # Configure styles
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Collector - Individual Destination Control", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Source files section
        self.create_source_section(main_frame)
        
        # File mappings table
        self.create_mappings_table(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
        
        # Progress and status
        self.create_status_section(main_frame)
        
        # Options frame
        self.create_options_section(main_frame)
        
    def create_source_section(self, parent):
        """Create source file selection section"""
        source_frame = ttk.LabelFrame(parent, text="Source Files", padding="10")
        source_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        source_frame.columnconfigure(1, weight=1)
        
        # Add files button
        ttk.Button(source_frame, text="Add Files", 
                  command=self.add_files, style='Action.TButton').grid(row=0, column=0, padx=(0, 10))
        
        # Add folder button
        ttk.Button(source_frame, text="Add Folder", 
                  command=self.add_folder, style='Action.TButton').grid(row=0, column=1, padx=(0, 10))
        
        # Clear all button
        ttk.Button(source_frame, text="Clear All", 
                  command=self.clear_all, style='Action.TButton').grid(row=0, column=2, padx=(0, 10))
        
        # Quick filters
        ttk.Label(source_frame, text="Quick Filter:").grid(row=0, column=3, padx=(20, 5))
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(source_frame, textvariable=self.filter_var, width=15)
        filter_combo['values'] = ('All Files', '*.txt', '*.pdf', '*.jpg', '*.png', '*.docx', '*.xlsx')
        filter_combo.set('All Files')
        filter_combo.grid(row=0, column=4, padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
    def create_mappings_table(self, parent):
        """Create the file mappings table with treeview"""
        mappings_frame = ttk.LabelFrame(parent, text="File Mappings", padding="10")
        mappings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        mappings_frame.columnconfigure(0, weight=1)
        mappings_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(mappings_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('selected', 'source', 'size', 'destination', 'status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.tree.heading('selected', text='✓')
        self.tree.heading('source', text='Source File')
        self.tree.heading('size', text='Size')
        self.tree.heading('destination', text='Destination')
        self.tree.heading('status', text='Status')
        
        self.tree.column('selected', width=30, anchor='center')
        self.tree.column('source', width=300, anchor='w')
        self.tree.column('size', width=80, anchor='e')
        self.tree.column('destination', width=300, anchor='w')
        self.tree.column('status', width=100, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Context menu
        self.create_context_menu()
        
        # Table action buttons
        table_buttons_frame = ttk.Frame(mappings_frame)
        table_buttons_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(table_buttons_frame, text="Set Destination", 
                  command=self.set_destination).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(table_buttons_frame, text="Set Default Dest", 
                  command=self.set_default_destination).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(table_buttons_frame, text="Toggle Selection", 
                  command=self.toggle_selection).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(table_buttons_frame, text="Remove Selected", 
                  command=self.remove_selected).grid(row=0, column=3, padx=(0, 10))
        
    def create_context_menu(self):
        """Create context menu for the treeview"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Set Destination", command=self.set_destination)
        self.context_menu.add_command(label="Set Default Destination", command=self.set_default_destination)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Selection", command=self.toggle_selection)
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_command(label="Deselect All", command=self.deselect_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove", command=self.remove_selected)
        self.context_menu.add_command(label="Open Source Folder", command=self.open_source_folder)
        self.context_menu.add_command(label="Open Destination Folder", command=self.open_destination_folder)
        
    def create_action_buttons(self, parent):
        """Create main action buttons"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(action_frame, text="Preview Operation", 
                  command=self.preview_operation, style='Action.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(action_frame, text="Start Collection", 
                  command=self.start_collection, style='Action.TButton').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(action_frame, text="Save Mappings", 
                  command=self.save_mappings).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(action_frame, text="Load Mappings", 
                  command=self.load_mappings).grid(row=0, column=3, padx=(0, 10))
        
    def create_status_section(self, parent):
        """Create progress and status section"""
        status_frame = ttk.LabelFrame(parent, text="Status & Progress", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Progress bar
        ttk.Label(status_frame, text="Progress:").grid(row=0, column=0, sticky=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=1, column=0, columnspan=2, 
                                                                  sticky=tk.W, pady=(5, 0))
        
    def create_options_section(self, parent):
        """Create options section"""
        options_frame = ttk.LabelFrame(parent, text="Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Copy mode
        ttk.Label(options_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.copy_mode_var = tk.StringVar(value=self.config.get('copy_mode', 'copy'))
        mode_combo = ttk.Combobox(options_frame, textvariable=self.copy_mode_var, 
                                 values=('copy', 'move', 'hardlink'), state='readonly', width=10)
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Preserve structure
        self.preserve_structure_var = tk.BooleanVar(value=self.config.get('preserve_structure', False))
        ttk.Checkbutton(options_frame, text="Preserve directory structure", 
                       variable=self.preserve_structure_var).grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # Overwrite existing
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Overwrite existing files", 
                       variable=self.overwrite_var).grid(row=0, column=3, sticky=tk.W)
        
    def bind_events(self):
        """Bind event handlers"""
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)  # Right click
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def add_files(self):
        """Add individual files to the collection"""
        files = filedialog.askopenfilenames(
            title="Select files to collect",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Document files", "*.docx *.xlsx *.pptx"),
            ]
        )
        
        for file_path in files:
            self.add_file_mapping(file_path)
            
    def add_folder(self):
        """Add all files from a folder"""
        folder = filedialog.askdirectory(title="Select folder to collect files from")
        if folder:
            # Ask for file pattern
            pattern = tk.simpledialog.askstring(
                "File Pattern", 
                "Enter file pattern (e.g., *.txt, *.*, or leave empty for all files):",
                initialvalue="*.*"
            )
            if pattern is None:
                pattern = "*.*"
                
            # Collect files matching pattern
            folder_path = Path(folder)
            if pattern == "*.*" or pattern == "":
                files = list(folder_path.rglob("*"))
            else:
                files = list(folder_path.rglob(pattern))
                
            for file_path in files:
                if file_path.is_file():
                    self.add_file_mapping(str(file_path))
                    
    def add_file_mapping(self, source_path):
        """Add a file mapping to the collection"""
        # Check if file already exists
        for mapping in self.file_mappings:
            if mapping['source'] == source_path:
                return
                
        # Get file size
        try:
            size = os.path.getsize(source_path)
            size_str = self.format_file_size(size)
        except:
            size_str = "Unknown"
            
        # Default destination
        filename = os.path.basename(source_path)
        default_dest = os.path.join(self.config.get('default_destination', './collected_files'), filename)
        
        # Create mapping
        mapping = {
            'source': source_path,
            'destination': default_dest,
            'selected': True,
            'size': size_str,
            'status': 'Ready'
        }
        
        self.file_mappings.append(mapping)
        self.refresh_tree()
        
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def refresh_tree(self):
        """Refresh the treeview with current mappings"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add mappings
        for i, mapping in enumerate(self.file_mappings):
            selected_mark = "✓" if mapping['selected'] else ""
            values = (
                selected_mark,
                mapping['source'],
                mapping['size'],
                mapping['destination'],
                mapping['status']
            )
            self.tree.insert('', 'end', values=values, tags=(str(i),))
            
    def apply_filter(self, event=None):
        """Apply file filter"""
        filter_value = self.filter_var.get()
        if filter_value == 'All Files':
            return
            
        # Remove files that don't match filter
        if filter_value.startswith('*.'):
            extension = filter_value[2:]
            self.file_mappings = [
                mapping for mapping in self.file_mappings
                if mapping['source'].lower().endswith(f'.{extension.lower()}')
            ]
            self.refresh_tree()
            
    def clear_all(self):
        """Clear all file mappings"""
        if messagebox.askyesno("Confirm", "Remove all file mappings?"):
            self.file_mappings.clear()
            self.refresh_tree()
            
    def get_selected_indices(self):
        """Get indices of selected items in tree"""
        selection = self.tree.selection()
        indices = []
        for item in selection:
            tags = self.tree.item(item, 'tags')
            if tags:
                indices.append(int(tags[0]))
        return indices
        
    def set_destination(self):
        """Set destination for selected items"""
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showinfo("Info", "Please select files to set destination for")
            return
            
        # Get destination from user
        destination = filedialog.askdirectory(title="Select destination folder")
        if destination:
            for index in indices:
                if index < len(self.file_mappings):
                    filename = os.path.basename(self.file_mappings[index]['source'])
                    self.file_mappings[index]['destination'] = os.path.join(destination, filename)
            self.refresh_tree()
            
    def set_default_destination(self):
        """Set default destination for selected items"""
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showinfo("Info", "Please select files to set destination for")
            return
            
        default_dest = self.config.get('default_destination', './collected_files')
        for index in indices:
            if index < len(self.file_mappings):
                filename = os.path.basename(self.file_mappings[index]['source'])
                self.file_mappings[index]['destination'] = os.path.join(default_dest, filename)
        self.refresh_tree()
        
    def toggle_selection(self):
        """Toggle selection state of selected items"""
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showinfo("Info", "Please select files to toggle")
            return
            
        for index in indices:
            if index < len(self.file_mappings):
                self.file_mappings[index]['selected'] = not self.file_mappings[index]['selected']
        self.refresh_tree()
        
    def select_all(self):
        """Select all files"""
        for mapping in self.file_mappings:
            mapping['selected'] = True
        self.refresh_tree()
        
    def deselect_all(self):
        """Deselect all files"""
        for mapping in self.file_mappings:
            mapping['selected'] = False
        self.refresh_tree()
        
    def remove_selected(self):
        """Remove selected items from tree"""
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showinfo("Info", "Please select files to remove")
            return
            
        if messagebox.askyesno("Confirm", f"Remove {len(indices)} selected file(s)?"):
            # Remove in reverse order to maintain indices
            for index in sorted(indices, reverse=True):
                if index < len(self.file_mappings):
                    del self.file_mappings[index]
            self.refresh_tree()
            
    def on_double_click(self, event):
        """Handle double click on tree item"""
        self.set_destination()
        
    def on_right_click(self, event):
        """Handle right click on tree item"""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def open_source_folder(self):
        """Open source folder in file explorer"""
        indices = self.get_selected_indices()
        if indices:
            source_path = self.file_mappings[indices[0]]['source']
            folder_path = os.path.dirname(source_path)
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # macOS and Linux
                    os.system(f'open "{folder_path}"' if sys.platform == 'darwin' else f'xdg-open "{folder_path}"')
            except:
                messagebox.showerror("Error", "Could not open folder")
                
    def open_destination_folder(self):
        """Open destination folder in file explorer"""
        indices = self.get_selected_indices()
        if indices:
            dest_path = self.file_mappings[indices[0]]['destination']
            folder_path = os.path.dirname(dest_path)
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # macOS and Linux
                    os.system(f'open "{folder_path}"' if sys.platform == 'darwin' else f'xdg-open "{folder_path}"')
            except:
                messagebox.showerror("Error", "Could not open folder")
                
    def preview_operation(self):
        """Preview the copy operation"""
        selected_mappings = [m for m in self.file_mappings if m['selected']]
        if not selected_mappings:
            messagebox.showinfo("Info", "No files selected for operation")
            return
            
        # Create preview window
        self.show_preview_window(selected_mappings)
        
    def show_preview_window(self, mappings):
        """Show preview window with operation details"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Operation Preview")
        preview_window.geometry("800x600")
        preview_window.transient(self.root)
        preview_window.grab_set()
        
        # Content frame
        content_frame = ttk.Frame(preview_window, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Summary
        summary_text = f"""
Operation Summary:
- Mode: {self.copy_mode_var.get().upper()}
- Files to process: {len(mappings)}
- Preserve structure: {self.preserve_structure_var.get()}
- Overwrite existing: {self.overwrite_var.get()}

File Operations:
"""
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        text_widget.insert(tk.END, summary_text)
        
        for i, mapping in enumerate(mappings, 1):
            operation_text = f"{i}. {mapping['source']}\n   → {mapping['destination']}\n\n"
            text_widget.insert(tk.END, operation_text)
            
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(button_frame, text="Start Operation", 
                  command=lambda: [preview_window.destroy(), self.start_collection()]).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=preview_window.destroy).pack(side=tk.LEFT)
                  
    def start_collection(self):
        """Start the file collection process"""
        selected_mappings = [m for m in self.file_mappings if m['selected']]
        if not selected_mappings:
            messagebox.showinfo("Info", "No files selected for operation")
            return
            
        # Confirm operation
        mode = self.copy_mode_var.get()
        if not messagebox.askyesno("Confirm", f"Start {mode} operation for {len(selected_mappings)} files?"):
            return
            
        # Start operation in thread
        self.progress_var.set(0)
        self.status_var.set("Starting operation...")
        
        thread = threading.Thread(target=self.perform_collection, args=(selected_mappings,))
        thread.daemon = True
        thread.start()
        
    def perform_collection(self, mappings):
        """Perform the actual file collection (runs in thread)"""
        total_files = len(mappings)
        successful = 0
        failed = 0
        
        mode = self.copy_mode_var.get()
        overwrite = self.overwrite_var.get()
        
        for i, mapping in enumerate(mappings):
            try:
                # Update status
                self.root.after(0, lambda: self.status_var.set(f"Processing: {os.path.basename(mapping['source'])}"))
                
                # Create destination directory
                dest_dir = os.path.dirname(mapping['destination'])
                os.makedirs(dest_dir, exist_ok=True)
                
                # Check if destination exists
                if os.path.exists(mapping['destination']) and not overwrite:
                    # Generate unique filename
                    base, ext = os.path.splitext(mapping['destination'])
                    counter = 1
                    while os.path.exists(mapping['destination']):
                        mapping['destination'] = f"{base}_{counter}{ext}"
                        counter += 1
                
                # Perform operation
                if mode == 'copy':
                    shutil.copy2(mapping['source'], mapping['destination'])
                elif mode == 'move':
                    shutil.move(mapping['source'], mapping['destination'])
                elif mode == 'hardlink':
                    os.link(mapping['source'], mapping['destination'])
                
                mapping['status'] = 'Completed'
                successful += 1
                
            except Exception as e:
                mapping['status'] = f'Error: {str(e)}'
                failed += 1
                self.logger.error(f"Failed to process {mapping['source']}: {e}")
                
            # Update progress
            progress = ((i + 1) / total_files) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            
        # Update final status
        final_status = f"Completed: {successful} successful, {failed} failed"
        self.root.after(0, lambda: self.status_var.set(final_status))
        self.root.after(0, self.refresh_tree)
        
        # Show completion message
        self.root.after(0, lambda: messagebox.showinfo("Operation Complete", final_status))
        
    def save_mappings(self):
        """Save current mappings to file"""
        filename = filedialog.asksaveasfilename(
            title="Save mappings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.file_mappings, f, indent=2)
                messagebox.showinfo("Success", "Mappings saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save mappings: {e}")
                
    def load_mappings(self):
        """Load mappings from file"""
        filename = filedialog.askopenfilename(
            title="Load mappings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.file_mappings = json.load(f)
                self.refresh_tree()
                messagebox.showinfo("Success", "Mappings loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load mappings: {e}")
                
    def on_closing(self):
        """Handle application closing"""
        self.save_config()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FileCollectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()