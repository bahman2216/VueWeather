#!/usr/bin/env python3
"""
File Collector GUI Application - Extended Version
Enhanced visual interface with advanced configuration and file management features.
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
import glob
import re

class FileCollectorGUIExtended:
    def __init__(self, root):
        self.root = root
        self.root.title("File Collector Pro - Advanced GUI")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Data storage
        self.file_mappings = []
        self.config = self.load_config()
        self.saved_filters = self.load_saved_filters()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize GUI
        self.setup_styles()
        self.create_menu()
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
            config_file = 'file_collector_gui_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load config: {e}")
        
        return {
            'default_destination': str(Path.home() / 'collected_files'),
            'preserve_structure': False,
            'copy_mode': 'copy',
            'window_geometry': '1400x900',
            'auto_refresh': True,
            'confirm_operations': True,
            'default_patterns': ['*.*'],
            'recent_destinations': [],
            'theme': 'default'
        }
    
    def load_saved_filters(self):
        """Load saved filter presets"""
        try:
            filters_file = 'saved_filters.json'
            if os.path.exists(filters_file):
                with open(filters_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            'Documents': {'patterns': ['*.pdf', '*.docx', '*.txt'], 'extensions': ['pdf', 'docx', 'txt']},
            'Images': {'patterns': ['*.jpg', '*.png', '*.gif'], 'extensions': ['jpg', 'jpeg', 'png', 'gif', 'bmp']},
            'Videos': {'patterns': ['*.mp4', '*.avi', '*.mkv'], 'extensions': ['mp4', 'avi', 'mkv', 'mov']},
            'Archives': {'patterns': ['*.zip', '*.rar', '*.7z'], 'extensions': ['zip', 'rar', '7z', 'tar']}
        }
    
    def save_config(self):
        """Save current configuration"""
        try:
            self.config['window_geometry'] = self.root.geometry()
            self.config['copy_mode'] = self.copy_mode_var.get()
            self.config['preserve_structure'] = self.preserve_structure_var.get()
            
            with open('file_collector_gui_config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def save_saved_filters(self):
        """Save filter presets"""
        try:
            with open('saved_filters.json', 'w') as f:
                json.dump(self.saved_filters, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save filters: {e}")
    
    def setup_styles(self):
        """Setup enhanced ttk styles"""
        style = ttk.Style()
        
        # Configure styles
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        style.configure('Warning.TLabel', foreground='#f39c12')
        
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self.new_session)
        file_menu.add_command(label="Load Mappings...", command=self.load_mappings)
        file_menu.add_command(label="Save Mappings...", command=self.save_mappings)
        file_menu.add_separator()
        file_menu.add_command(label="Export Report...", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select All", command=self.select_all)
        edit_menu.add_command(label="Deselect All", command=self.deselect_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Remove Selected", command=self.remove_selected)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Duplicate Finder", command=self.find_duplicates)
        tools_menu.add_command(label="Batch Rename", command=self.batch_rename)
        tools_menu.add_command(label="Size Calculator", command=self.calculate_total_size)
        tools_menu.add_separator()
        tools_menu.add_command(label="Preferences", command=self.show_preferences)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container with notebook for tabs
        self.notebook = ttk.Notebook(self.root, padding="5")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab
        main_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(main_tab, text="File Collection")
        
        # Advanced tab
        advanced_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_tab, text="Advanced Options")
        
        # Logs tab
        logs_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(logs_tab, text="Logs & Reports")
        
        # Create main tab content
        self.create_main_tab_content(main_tab)
        
        # Create advanced tab content
        self.create_advanced_tab_content(advanced_tab)
        
        # Create logs tab content
        self.create_logs_tab_content(logs_tab)
        
    def create_main_tab_content(self, parent):
        """Create main tab content"""
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(parent, text="File Collector Pro - Individual Destination Control", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Enhanced source section
        self.create_enhanced_source_section(parent)
        
        # File mappings table
        self.create_enhanced_mappings_table(parent)
        
        # Action buttons
        self.create_enhanced_action_buttons(parent)
        
        # Progress and status
        self.create_enhanced_status_section(parent)
        
    def create_enhanced_source_section(self, parent):
        """Create enhanced source file selection section"""
        source_frame = ttk.LabelFrame(parent, text="Source Files & Filters", padding="10")
        source_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        source_frame.columnconfigure(1, weight=1)
        
        # First row - file operations
        ttk.Button(source_frame, text="Add Files", 
                  command=self.add_files, style='Action.TButton').grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        ttk.Button(source_frame, text="Add Folder", 
                  command=self.add_folder, style='Action.TButton').grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Button(source_frame, text="Add with Pattern", 
                  command=self.add_with_pattern, style='Action.TButton').grid(row=0, column=2, padx=5, sticky=tk.W)
        ttk.Button(source_frame, text="Clear All", 
                  command=self.clear_all, style='Action.TButton').grid(row=0, column=3, padx=(5, 0), sticky=tk.W)
        
        # Second row - filter presets
        ttk.Label(source_frame, text="Filter Presets:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.filter_preset_var = tk.StringVar()
        filter_preset_combo = ttk.Combobox(source_frame, textvariable=self.filter_preset_var, width=15)
        filter_preset_combo['values'] = list(self.saved_filters.keys()) + ['Custom...']
        filter_preset_combo.set('Custom...')
        filter_preset_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0), padx=(10, 0))
        filter_preset_combo.bind('<<ComboboxSelected>>', self.apply_filter_preset)
        
        # Custom filter entry
        ttk.Label(source_frame, text="Custom Pattern:").grid(row=1, column=2, sticky=tk.W, pady=(10, 0), padx=(20, 5))
        self.custom_pattern_var = tk.StringVar()
        custom_pattern_entry = ttk.Entry(source_frame, textvariable=self.custom_pattern_var, width=20)
        custom_pattern_entry.grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        custom_pattern_entry.bind('<Return>', self.apply_custom_pattern)
        
        # Third row - quick actions
        ttk.Button(source_frame, text="Save Filter", 
                  command=self.save_current_filter).grid(row=2, column=0, pady=(10, 0), sticky=tk.W)
        ttk.Button(source_frame, text="Apply Filter", 
                  command=self.apply_custom_pattern).grid(row=2, column=1, pady=(10, 0), sticky=tk.W, padx=(10, 0))
        
        # File count label
        self.file_count_var = tk.StringVar(value="Files: 0")
        ttk.Label(source_frame, textvariable=self.file_count_var, 
                 style='Header.TLabel').grid(row=2, column=3, pady=(10, 0), sticky=tk.E)
        
    def create_enhanced_mappings_table(self, parent):
        """Create enhanced file mappings table"""
        mappings_frame = ttk.LabelFrame(parent, text="File Mappings", padding="10")
        mappings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        mappings_frame.columnconfigure(0, weight=1)
        mappings_frame.rowconfigure(0, weight=1)
        
        # Create enhanced treeview
        tree_frame = ttk.Frame(mappings_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Enhanced treeview with more columns
        columns = ('selected', 'source', 'size', 'type', 'destination', 'status', 'progress')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('selected', text='✓')
        self.tree.heading('source', text='Source File')
        self.tree.heading('size', text='Size')
        self.tree.heading('type', text='Type')
        self.tree.heading('destination', text='Destination')
        self.tree.heading('status', text='Status')
        self.tree.heading('progress', text='Progress')
        
        self.tree.column('selected', width=30, anchor='center')
        self.tree.column('source', width=250, anchor='w')
        self.tree.column('size', width=80, anchor='e')
        self.tree.column('type', width=60, anchor='center')
        self.tree.column('destination', width=250, anchor='w')
        self.tree.column('status', width=100, anchor='center')
        self.tree.column('progress', width=80, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Enhanced context menu
        self.create_enhanced_context_menu()
        
        # Enhanced table action buttons
        table_buttons_frame = ttk.Frame(mappings_frame)
        table_buttons_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(table_buttons_frame, text="Set Destination", 
                  command=self.set_destination).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(table_buttons_frame, text="Bulk Set Dest", 
                  command=self.bulk_set_destination).grid(row=0, column=1, padx=5)
        ttk.Button(table_buttons_frame, text="Toggle Selection", 
                  command=self.toggle_selection).grid(row=0, column=2, padx=5)
        ttk.Button(table_buttons_frame, text="Edit Path", 
                  command=self.edit_destination_path).grid(row=0, column=3, padx=5)
        ttk.Button(table_buttons_frame, text="Remove Selected", 
                  command=self.remove_selected).grid(row=0, column=4, padx=(5, 0))
        
    def create_enhanced_context_menu(self):
        """Create enhanced context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Set Destination", command=self.set_destination)
        self.context_menu.add_command(label="Edit Destination Path", command=self.edit_destination_path)
        self.context_menu.add_command(label="Set Default Destination", command=self.set_default_destination)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Selection", command=self.toggle_selection)
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_command(label="Deselect All", command=self.deselect_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Path", command=self.copy_path_to_clipboard)
        self.context_menu.add_command(label="Show Properties", command=self.show_file_properties)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove", command=self.remove_selected)
        self.context_menu.add_command(label="Open Source Folder", command=self.open_source_folder)
        self.context_menu.add_command(label="Open Destination Folder", command=self.open_destination_folder)
        
    def create_enhanced_action_buttons(self, parent):
        """Create enhanced action buttons"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(action_frame, text="Preview Operation", 
                  command=self.preview_operation, style='Action.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(action_frame, text="Start Collection", 
                  command=self.start_collection, style='Action.TButton').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(action_frame, text="Pause/Resume", 
                  command=self.toggle_pause, style='Action.TButton').grid(row=0, column=2, padx=(0, 10))
        ttk.Button(action_frame, text="Stop Operation", 
                  command=self.stop_operation, style='Action.TButton').grid(row=0, column=3, padx=(0, 10))
        
    def create_enhanced_status_section(self, parent):
        """Create enhanced progress and status section"""
        status_frame = ttk.LabelFrame(parent, text="Status & Progress", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Overall progress
        ttk.Label(status_frame, text="Overall Progress:").grid(row=0, column=0, sticky=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        # Progress label
        self.progress_label_var = tk.StringVar(value="0/0 files")
        ttk.Label(status_frame, textvariable=self.progress_label_var).grid(row=0, column=2, sticky=tk.E)
        
        # Current file progress
        ttk.Label(status_frame, text="Current File:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.current_file_var = tk.DoubleVar()
        self.current_file_bar = ttk.Progressbar(status_frame, variable=self.current_file_var, 
                                              maximum=100, mode='determinate')
        self.current_file_bar.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(5, 0))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=2, column=0, columnspan=3, 
                                                                  sticky=tk.W, pady=(5, 0))
        
    def create_advanced_tab_content(self, parent):
        """Create advanced options tab content"""
        parent.columnconfigure(0, weight=1)
        
        # Operation options
        options_frame = ttk.LabelFrame(parent, text="Operation Options", padding="10")
        options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Copy mode
        ttk.Label(options_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.copy_mode_var = tk.StringVar(value=self.config.get('copy_mode', 'copy'))
        mode_combo = ttk.Combobox(options_frame, textvariable=self.copy_mode_var, 
                                 values=('copy', 'move', 'hardlink', 'symlink'), state='readonly', width=10)
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Options checkboxes
        self.preserve_structure_var = tk.BooleanVar(value=self.config.get('preserve_structure', False))
        ttk.Checkbutton(options_frame, text="Preserve directory structure", 
                       variable=self.preserve_structure_var).grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Overwrite existing files", 
                       variable=self.overwrite_var).grid(row=0, column=3, sticky=tk.W)
        
        # More options
        self.verify_copy_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Verify copies", 
                       variable=self.verify_copy_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.skip_large_files_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Skip files larger than:", 
                       variable=self.skip_large_files_var).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        self.max_file_size_var = tk.StringVar(value="100")
        size_entry = ttk.Entry(options_frame, textvariable=self.max_file_size_var, width=10)
        size_entry.grid(row=1, column=2, sticky=tk.W, pady=(5, 0), padx=(5, 0))
        ttk.Label(options_frame, text="MB").grid(row=1, column=3, sticky=tk.W, pady=(5, 0), padx=(5, 0))
        
        # Destination options
        dest_frame = ttk.LabelFrame(parent, text="Destination Options", padding="10")
        dest_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dest_frame.columnconfigure(1, weight=1)
        
        # Default destination
        ttk.Label(dest_frame, text="Default Destination:").grid(row=0, column=0, sticky=tk.W)
        self.default_dest_var = tk.StringVar(value=self.config.get('default_destination', ''))
        dest_entry = ttk.Entry(dest_frame, textvariable=self.default_dest_var)
        dest_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        ttk.Button(dest_frame, text="Browse", 
                  command=self.browse_default_destination).grid(row=0, column=2)
        
        # Naming options
        naming_frame = ttk.LabelFrame(parent, text="File Naming Options", padding="10")
        naming_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.add_timestamp_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(naming_frame, text="Add timestamp to filenames", 
                       variable=self.add_timestamp_var).grid(row=0, column=0, sticky=tk.W)
        
        self.add_counter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(naming_frame, text="Add counter for duplicates", 
                       variable=self.add_counter_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Performance options
        perf_frame = ttk.LabelFrame(parent, text="Performance Options", padding="10")
        perf_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(perf_frame, text="Thread count:").grid(row=0, column=0, sticky=tk.W)
        self.thread_count_var = tk.StringVar(value="4")
        thread_spin = ttk.Spinbox(perf_frame, from_=1, to=16, textvariable=self.thread_count_var, width=10)
        thread_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(perf_frame, text="Buffer size:").grid(row=0, column=2, sticky=tk.W)
        self.buffer_size_var = tk.StringVar(value="64")
        buffer_combo = ttk.Combobox(perf_frame, textvariable=self.buffer_size_var, 
                                   values=('32', '64', '128', '256'), width=10)
        buffer_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        ttk.Label(perf_frame, text="KB").grid(row=0, column=4, sticky=tk.W, padx=(5, 0))
        
    def create_logs_tab_content(self, parent):
        """Create logs and reports tab content"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Log controls
        log_controls_frame = ttk.Frame(parent)
        log_controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(log_controls_frame, text="Refresh Logs", 
                  command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_controls_frame, text="Clear Logs", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_controls_frame, text="Export Logs", 
                  command=self.export_logs).pack(side=tk.LEFT, padx=(0, 10))
        
        # Log display
        log_frame = ttk.LabelFrame(parent, text="Operation Logs", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load existing logs
        self.refresh_logs()
        
    # File operation methods (implementing required functionality)
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
                ("Video files", "*.mp4 *.avi *.mkv *.mov"),
                ("Audio files", "*.mp3 *.wav *.flac"),
                ("Archive files", "*.zip *.rar *.7z *.tar"),
            ]
        )
        
        for file_path in files:
            self.add_file_mapping(file_path)
        
        self.update_file_count()
            
    def add_folder(self):
        """Add all files from a folder"""
        folder = filedialog.askdirectory(title="Select folder to collect files from")
        if folder:
            pattern = simpledialog.askstring(
                "File Pattern", 
                "Enter file pattern (e.g., *.txt, *.*, or leave empty for all files):",
                initialvalue="*.*"
            )
            if pattern is None:
                pattern = "*.*"
                
            self.add_files_from_folder(folder, pattern)
            
    def add_with_pattern(self):
        """Add files using advanced pattern matching"""
        folder = filedialog.askdirectory(title="Select folder to search in")
        if not folder:
            return
            
        # Show pattern dialog
        self.show_pattern_dialog(folder)
        
    def add_files_from_folder(self, folder, pattern):
        """Add files from folder matching pattern"""
        folder_path = Path(folder)
        
        try:
            if pattern == "*.*" or pattern == "":
                files = list(folder_path.rglob("*"))
            else:
                files = list(folder_path.rglob(pattern))
                
            for file_path in files:
                if file_path.is_file():
                    self.add_file_mapping(str(file_path))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan folder: {e}")
            
        self.update_file_count()
            
    def add_file_mapping(self, source_path):
        """Add a file mapping to the collection"""
        # Check if file already exists
        for mapping in self.file_mappings:
            if mapping['source'] == source_path:
                return
                
        # Get file info
        try:
            size = os.path.getsize(source_path)
            size_str = self.format_file_size(size)
            file_type = Path(source_path).suffix.upper()[1:] or "FILE"
        except:
            size_str = "Unknown"
            file_type = "Unknown"
            
        # Default destination
        filename = os.path.basename(source_path)
        default_dest = os.path.join(self.default_dest_var.get() or './collected_files', filename)
        
        # Create mapping
        mapping = {
            'source': source_path,
            'destination': default_dest,
            'selected': True,
            'size': size_str,
            'type': file_type,
            'status': 'Ready',
            'progress': '0%'
        }
        
        self.file_mappings.append(mapping)
        self.refresh_tree()
        
    # Additional implementation methods...
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
                mapping['type'],
                mapping['destination'],
                mapping['status'],
                mapping['progress']
            )
            self.tree.insert('', 'end', values=values, tags=(str(i),))
            
    def update_file_count(self):
        """Update file count display"""
        total = len(self.file_mappings)
        selected = sum(1 for m in self.file_mappings if m['selected'])
        self.file_count_var.set(f"Files: {total} (Selected: {selected})")
        
    # Menu and dialog methods
    def new_session(self):
        """Start a new session"""
        if messagebox.askyesno("New Session", "Clear current session and start new?"):
            self.file_mappings.clear()
            self.refresh_tree()
            self.update_file_count()
            
    def show_preferences(self):
        """Show preferences dialog"""
        prefs_window = tk.Toplevel(self.root)
        prefs_window.title("Preferences")
        prefs_window.geometry("500x400")
        prefs_window.transient(self.root)
        prefs_window.grab_set()
        
        # Preferences content would go here
        ttk.Label(prefs_window, text="Preferences", style='Title.TLabel').pack(pady=20)
        ttk.Label(prefs_window, text="Feature coming soon...").pack()
        
    def show_help(self):
        """Show help dialog"""
        help_text = """
File Collector Pro - Quick Guide

1. Add Files: Use 'Add Files' or 'Add Folder' to select source files
2. Set Destinations: Double-click files or use 'Set Destination' to specify where each file should go
3. Preview: Use 'Preview Operation' to see what will happen
4. Start: Click 'Start Collection' to begin the file operation
5. Monitor: Watch progress in the status section

Tips:
- Right-click for context menu with additional options
- Use filter presets for common file types
- Save/load mappings to reuse file selections
- Check the Advanced tab for more options
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Quick Guide")
        help_window.geometry("600x400")
        help_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
File Collector Pro v2.0

A comprehensive file collection and management tool
with individual destination control.

Features:
• Individual file destination mapping
• Multiple copy modes (copy, move, hardlink, symlink)
• Advanced filtering and pattern matching
• Progress tracking and logging
• Batch operations and automation
• Cross-platform compatibility

Created with Python and tkinter
        """
        messagebox.showinfo("About File Collector Pro", about_text)
        
    # Placeholder methods for additional functionality
    def apply_filter_preset(self, event=None):
        """Apply selected filter preset"""
        pass
        
    def apply_custom_pattern(self, event=None):
        """Apply custom pattern filter"""
        pass
        
    def save_current_filter(self):
        """Save current filter as preset"""
        pass
        
    def bulk_set_destination(self):
        """Set destination for multiple files"""
        pass
        
    def edit_destination_path(self):
        """Edit destination path directly"""
        pass
        
    def copy_path_to_clipboard(self):
        """Copy file path to clipboard"""
        pass
        
    def show_file_properties(self):
        """Show file properties dialog"""
        pass
        
    def toggle_pause(self):
        """Pause or resume operation"""
        pass
        
    def stop_operation(self):
        """Stop current operation"""
        pass
        
    def find_duplicates(self):
        """Find duplicate files"""
        pass
        
    def batch_rename(self):
        """Batch rename files"""
        pass
        
    def calculate_total_size(self):
        """Calculate total size of selected files"""
        pass
        
    def browse_default_destination(self):
        """Browse for default destination"""
        dest = filedialog.askdirectory(title="Select default destination")
        if dest:
            self.default_dest_var.set(dest)
            
    def refresh_logs(self):
        """Refresh log display"""
        try:
            if os.path.exists('file_collector_gui.log'):
                with open('file_collector_gui.log', 'r') as f:
                    self.log_text.delete(1.0, tk.END)
                    self.log_text.insert(tk.END, f.read())
                    self.log_text.see(tk.END)
        except:
            pass
            
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
        
    def export_logs(self):
        """Export logs to file"""
        filename = filedialog.asksaveasfilename(
            title="Export logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Logs exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {e}")
                
    def export_report(self):
        """Export operation report"""
        pass
        
    def show_pattern_dialog(self, folder):
        """Show advanced pattern dialog"""
        pass
        
    # Implement missing core methods from original GUI
    def clear_all(self):
        """Clear all file mappings"""
        if messagebox.askyesno("Confirm", "Remove all file mappings?"):
            self.file_mappings.clear()
            self.refresh_tree()
            self.update_file_count()
            
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
            
        default_dest = self.default_dest_var.get() or './collected_files'
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
        self.update_file_count()
        
    def select_all(self):
        """Select all files"""
        for mapping in self.file_mappings:
            mapping['selected'] = True
        self.refresh_tree()
        self.update_file_count()
        
    def deselect_all(self):
        """Deselect all files"""
        for mapping in self.file_mappings:
            mapping['selected'] = False
        self.refresh_tree()
        self.update_file_count()
        
    def remove_selected(self):
        """Remove selected items from tree"""
        indices = self.get_selected_indices()
        if not indices:
            messagebox.showinfo("Info", "Please select files to remove")
            return
            
        if messagebox.askyesno("Confirm", f"Remove {len(indices)} selected file(s)?"):
            for index in sorted(indices, reverse=True):
                if index < len(self.file_mappings):
                    del self.file_mappings[index]
            self.refresh_tree()
            self.update_file_count()
            
    def open_source_folder(self):
        """Open source folder in file explorer"""
        indices = self.get_selected_indices()
        if indices:
            source_path = self.file_mappings[indices[0]]['source']
            folder_path = os.path.dirname(source_path)
            try:
                if os.name == 'nt':
                    os.startfile(folder_path)
                elif os.name == 'posix':
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
                if os.name == 'nt':
                    os.startfile(folder_path)
                elif os.name == 'posix':
                    os.system(f'open "{folder_path}"' if sys.platform == 'darwin' else f'xdg-open "{folder_path}"')
            except:
                messagebox.showerror("Error", "Could not open folder")
                
    def preview_operation(self):
        """Preview the copy operation"""
        selected_mappings = [m for m in self.file_mappings if m['selected']]
        if not selected_mappings:
            messagebox.showinfo("Info", "No files selected for operation")
            return
            
        self.show_preview_window(selected_mappings)
        
    def show_preview_window(self, mappings):
        """Show preview window with operation details"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Operation Preview")
        preview_window.geometry("900x700")
        preview_window.transient(self.root)
        preview_window.grab_set()
        
        content_frame = ttk.Frame(preview_window, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        summary_text = f"""
Operation Summary:
- Mode: {self.copy_mode_var.get().upper()}
- Files to process: {len(mappings)}
- Preserve structure: {self.preserve_structure_var.get()}
- Overwrite existing: {self.overwrite_var.get()}
- Verify copies: {self.verify_copy_var.get()}

File Operations:
"""
        
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=25)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        text_widget.insert(tk.END, summary_text)
        
        for i, mapping in enumerate(mappings, 1):
            operation_text = f"{i}. {mapping['source']}\n   → {mapping['destination']}\n   Size: {mapping['size']}, Type: {mapping['type']}\n\n"
            text_widget.insert(tk.END, operation_text)
            
        text_widget.config(state=tk.DISABLED)
        
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
            
        mode = self.copy_mode_var.get()
        if not messagebox.askyesno("Confirm", f"Start {mode} operation for {len(selected_mappings)} files?"):
            return
            
        self.progress_var.set(0)
        self.current_file_var.set(0)
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
                filename = os.path.basename(mapping['source'])
                self.root.after(0, lambda: self.status_var.set(f"Processing: {filename}"))
                self.root.after(0, lambda p=i: self.progress_label_var.set(f"{p+1}/{total_files} files"))
                
                # Create destination directory
                dest_dir = os.path.dirname(mapping['destination'])
                os.makedirs(dest_dir, exist_ok=True)
                
                # Handle existing files
                if os.path.exists(mapping['destination']) and not overwrite:
                    base, ext = os.path.splitext(mapping['destination'])
                    counter = 1
                    while os.path.exists(mapping['destination']):
                        mapping['destination'] = f"{base}_{counter}{ext}"
                        counter += 1
                
                # Perform operation with progress
                if mode == 'copy':
                    self.copy_with_progress(mapping['source'], mapping['destination'], i, total_files)
                elif mode == 'move':
                    shutil.move(mapping['source'], mapping['destination'])
                elif mode == 'hardlink':
                    os.link(mapping['source'], mapping['destination'])
                elif mode == 'symlink':
                    os.symlink(mapping['source'], mapping['destination'])
                
                mapping['status'] = 'Completed'
                mapping['progress'] = '100%'
                successful += 1
                
            except Exception as e:
                mapping['status'] = f'Error: {str(e)}'
                mapping['progress'] = 'Failed'
                failed += 1
                self.logger.error(f"Failed to process {mapping['source']}: {e}")
                
            # Update progress
            progress = ((i + 1) / total_files) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, self.refresh_tree)
            
        final_status = f"Completed: {successful} successful, {failed} failed"
        self.root.after(0, lambda: self.status_var.set(final_status))
        self.root.after(0, lambda: messagebox.showinfo("Operation Complete", final_status))
        
    def copy_with_progress(self, src, dst, file_index, total_files):
        """Copy file with progress tracking"""
        buffer_size = int(self.buffer_size_var.get()) * 1024
        
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                file_size = os.path.getsize(src)
                copied = 0
                
                while True:
                    chunk = fsrc.read(buffer_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    copied += len(chunk)
                    
                    # Update current file progress
                    if file_size > 0:
                        file_progress = (copied / file_size) * 100
                        self.root.after(0, lambda p=file_progress: self.current_file_var.set(p))
        
        # Copy metadata
        shutil.copystat(src, dst)
        
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
                self.update_file_count()
                messagebox.showinfo("Success", "Mappings loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load mappings: {e}")
                
    def bind_events(self):
        """Bind event handlers"""
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_double_click(self, event):
        """Handle double click on tree item"""
        self.set_destination()
        
    def on_right_click(self, event):
        """Handle right click on tree item"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def on_closing(self):
        """Handle application closing"""
        self.save_config()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FileCollectorGUIExtended(root)
    root.mainloop()

if __name__ == "__main__":
    main()