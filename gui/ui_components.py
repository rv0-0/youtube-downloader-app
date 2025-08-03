"""
UI Components for the YouTube Downloader GUI
Handles the creation and setup of all UI elements
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .constants import (
    QUALITY_OPTIONS, DEFAULT_CUSTOM_FORMAT, FORMAT_HELP_TEXT,
    TITLE_FONT, NORMAL_FONT, BOLD_FONT, CODE_FONT, URL_FONT,
    PROGRESS_COLUMNS, PADDING_STANDARD, PADDING_SMALL
)


class UIComponents:
    """Manages all UI component creation and setup"""
    
    def __init__(self, parent, progress_tracker):
        self.parent = parent
        self.progress_tracker = progress_tracker
        
        # UI Variables
        self.path_var = None
        self.quality_var = None
        self.custom_format_var = None
        self.download_subtitles_var = None
        self.embed_subtitles_var = None
        
        # UI Elements
        self.urls_text = None
        self.log_text = None
        self.download_button = None
        self.stop_button = None
        self.custom_format_frame = None
        
        # Setup main container
        self.main_container = ttk.Frame(parent)
        self.main_container.pack(fill="both", expand=True, padx=PADDING_STANDARD, pady=PADDING_STANDARD)
        
        # Configure grid weights for responsive design
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(6, weight=1)  # Video progress area
        self.main_container.rowconfigure(7, weight=1)  # Log area
    
    def setup_ui(self, download_path, browse_callback, clear_callback, quality_change_callback):
        """Setup all UI components"""
        self._setup_title()
        self._setup_settings_panel(download_path, browse_callback)
        self._setup_options_panel(quality_change_callback)
        self._setup_custom_format_panel()
        self._setup_urls_panel()
        self._setup_buttons_panel(clear_callback)
        self._setup_progress_panel()
        self._setup_log_panel()
    
    def _setup_title(self):
        """Setup the title label"""
        title_label = ttk.Label(self.main_container, text="🎬 YouTube Downloader", 
                               font=TITLE_FONT)
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, PADDING_STANDARD))
    
    def _setup_settings_panel(self, download_path, browse_callback):
        """Setup the download path settings panel"""
        settings_panel = ttk.Frame(self.main_container)
        settings_panel.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, PADDING_STANDARD))
        settings_panel.columnconfigure(1, weight=1)
        
        # Download path - more compact
        ttk.Label(settings_panel, text="📁 Path:").grid(row=0, column=0, sticky=tk.W)
        self.path_var = tk.StringVar(value=download_path)
        path_entry = ttk.Entry(settings_panel, textvariable=self.path_var, state="readonly", width=40)
        path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        browse_button = ttk.Button(settings_panel, text="Browse", command=browse_callback, width=8)
        browse_button.grid(row=0, column=2, sticky=tk.W)
    
    def _setup_options_panel(self, quality_change_callback):
        """Setup quality and subtitle options panel"""
        options_panel = ttk.Frame(self.main_container)
        options_panel.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, PADDING_STANDARD))
        options_panel.columnconfigure(1, weight=1)
        
        # Quality selection - compact
        ttk.Label(options_panel, text="🎥 Quality:").grid(row=0, column=0, sticky=tk.W)
        self.quality_var = tk.StringVar(value="Best Quality (4K/1440p/1080p)")
        quality_combo = ttk.Combobox(options_panel, textvariable=self.quality_var, 
                                   values=list(QUALITY_OPTIONS.keys()), 
                                   state="readonly", width=25)
        quality_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 15))
        quality_combo.bind('<<ComboboxSelected>>', quality_change_callback)
        
        # Subtitle options - compact checkboxes
        self.download_subtitles_var = tk.BooleanVar(value=True)
        subtitle_check = ttk.Checkbutton(options_panel, text="📝 Subtitles", 
                                        variable=self.download_subtitles_var)
        subtitle_check.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.embed_subtitles_var = tk.BooleanVar(value=False)
        embed_check = ttk.Checkbutton(options_panel, text="📎 Embed", 
                                     variable=self.embed_subtitles_var)
        embed_check.grid(row=0, column=3, sticky=tk.W)
    
    def _setup_custom_format_panel(self):
        """Setup custom format entry panel (initially hidden)"""
        self.custom_format_frame = ttk.Frame(self.main_container)
        self.custom_format_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, PADDING_STANDARD))
        self.custom_format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.custom_format_frame, text="⚙️ Custom:").grid(row=0, column=0, sticky=tk.W)
        self.custom_format_var = tk.StringVar(value=DEFAULT_CUSTOM_FORMAT)
        self.custom_format_entry = ttk.Entry(self.custom_format_frame, textvariable=self.custom_format_var)
        self.custom_format_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        help_button = ttk.Button(self.custom_format_frame, text="?", width=3, 
                               command=self._show_format_help)
        help_button.grid(row=0, column=2, sticky=tk.W)
        
        # Hide custom format initially
        self.custom_format_frame.grid_remove()
    
    def _setup_urls_panel(self):
        """Setup URLs input panel"""
        urls_panel = ttk.LabelFrame(self.main_container, text="🔗 YouTube URLs", padding=PADDING_STANDARD)
        urls_panel.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, PADDING_STANDARD))
        urls_panel.columnconfigure(0, weight=1)
        urls_panel.rowconfigure(0, weight=1)
        
        self.urls_text = scrolledtext.ScrolledText(urls_panel, height=4, width=50, font=URL_FONT)
        self.urls_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _setup_buttons_panel(self, clear_callback):
        """Setup action buttons panel"""
        buttons_panel = ttk.Frame(self.main_container)
        buttons_panel.grid(row=5, column=0, pady=(0, PADDING_STANDARD))
        
        self.download_button = ttk.Button(buttons_panel, text="🚀 Start Download", width=15)
        self.download_button.pack(side=tk.LEFT, padx=(0, PADDING_STANDARD))
        
        self.stop_button = ttk.Button(buttons_panel, text="⏹️ Stop", state="disabled", width=10)
        self.stop_button.pack(side=tk.LEFT, padx=(0, PADDING_STANDARD))
        
        clear_button = ttk.Button(buttons_panel, text="🗑️ Clear", 
                                 command=clear_callback, width=10)
        clear_button.pack(side=tk.LEFT)
    
    def _setup_progress_panel(self):
        """Setup progress tracking panel"""
        progress_panel = ttk.LabelFrame(self.main_container, text="📊 Progress", padding=PADDING_STANDARD)
        progress_panel.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, PADDING_STANDARD))
        progress_panel.columnconfigure(0, weight=1)
        progress_panel.rowconfigure(2, weight=1)
        
        # Create progress bars with correct parent
        overall_progress_bar = ttk.Progressbar(progress_panel, mode='determinate', length=400)
        current_progress_bar = ttk.Progressbar(progress_panel, mode='determinate', length=400)
        
        # Update progress tracker with the new progress bars
        self.progress_tracker.overall_progress_bar = overall_progress_bar
        self.progress_tracker.current_progress_bar = current_progress_bar
        
        # Overall progress - compact
        overall_frame = ttk.Frame(progress_panel)
        overall_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, PADDING_SMALL))
        overall_frame.columnconfigure(1, weight=1)
        
        ttk.Label(overall_frame, text="Overall:", font=BOLD_FONT).grid(row=0, column=0, sticky=tk.W)
        overall_label = ttk.Label(overall_frame, textvariable=self.progress_tracker.overall_progress_var, 
                                 font=NORMAL_FONT)
        overall_label.grid(row=0, column=1, sticky=tk.W, padx=(PADDING_STANDARD, 0))
        
        overall_progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), 
                                 pady=(0, PADDING_STANDARD))
        
        # Video progress treeview - more compact
        videos_tree = ttk.Treeview(progress_panel, columns=PROGRESS_COLUMNS, 
                                  show="headings", height=6)
        
        # Set the tree in progress tracker
        self.progress_tracker.videos_tree = videos_tree
        
        # Configure tree in progress tracker
        self.progress_tracker._setup_tree_columns()
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(progress_panel)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        videos_tree.grid(row=0, column=0, in_=tree_frame, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", 
                                      command=videos_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        videos_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Current progress display
        current_frame = ttk.Frame(progress_panel)
        current_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(PADDING_SMALL, 0))
        current_frame.columnconfigure(1, weight=1)
        
        ttk.Label(current_frame, text="Current:", font=BOLD_FONT).grid(row=0, column=0, sticky=tk.W)
        current_label = ttk.Label(current_frame, textvariable=self.progress_tracker.current_progress_var, 
                                 font=NORMAL_FONT)
        current_label.grid(row=0, column=1, sticky=tk.W, padx=(PADDING_STANDARD, 0))
        
        current_progress_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), 
                                 pady=(2, 0))
    
    def _setup_log_panel(self):
        """Setup download log panel"""
        log_panel = ttk.LabelFrame(self.main_container, text="📝 Download Log", padding=PADDING_STANDARD)
        log_panel.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_panel.columnconfigure(0, weight=1)
        log_panel.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_panel, height=6, width=50, 
                                                 font=CODE_FONT, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _show_format_help(self):
        """Show help dialog for custom format"""
        messagebox.showinfo("Format Help", FORMAT_HELP_TEXT)
    
    def on_quality_change(self, event=None):
        """Handle quality selection change"""
        if self.quality_var.get() == "Custom Format":
            self.custom_format_frame.grid()
        else:
            self.custom_format_frame.grid_remove()
    
    def get_selected_format(self):
        """Get the currently selected video format"""
        quality_name = self.quality_var.get()
        if quality_name == "Custom Format":
            return self.custom_format_var.get()
        else:
            return QUALITY_OPTIONS.get(quality_name, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best")
    
    def clear_urls(self):
        """Clear the URLs text area"""
        self.urls_text.delete(1.0, tk.END)
    
    def get_urls_text(self):
        """Get text from URLs input"""
        return self.urls_text.get(1.0, tk.END).strip()
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def set_download_buttons_state(self, download_enabled, stop_enabled):
        """Set the state of download and stop buttons"""
        self.download_button.config(state="normal" if download_enabled else "disabled")
        self.stop_button.config(state="normal" if stop_enabled else "disabled")
    
    def get_download_settings(self):
        """Get current download settings"""
        return {
            'path': self.path_var.get(),
            'format': self.get_selected_format(),
            'download_subtitles': self.download_subtitles_var.get(),
            'embed_subtitles': self.embed_subtitles_var.get()
        }
