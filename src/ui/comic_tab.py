import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import threading
import os
from src.modules.comic_folder import converter

class ComicFolderTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # self.pack(fill='both', expand=True) # Let the notebook handle packing
        
        # Variables
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        
        # Layout
        self.create_widgets()
        
    def create_widgets(self):
        padding = {'padx': 10, 'pady': 5}
        
        # Input Directory
        input_frame = tk.Frame(self)
        input_frame.pack(fill='x', **padding)
        tk.Label(input_frame, text="Input Directory:").pack(anchor='w')
        tk.Entry(input_frame, textvariable=self.input_var).pack(side='left', fill='x', expand=True)
        tk.Button(input_frame, text="Browse...", command=self.select_input).pack(side='right', padx=(5, 0))
        
        # Output Directory
        output_frame = tk.Frame(self)
        output_frame.pack(fill='x', **padding)
        tk.Label(output_frame, text="Output Directory:").pack(anchor='w')
        tk.Entry(output_frame, textvariable=self.output_var).pack(side='left', fill='x', expand=True)
        tk.Button(output_frame, text="Browse...", command=self.select_output).pack(side='right', padx=(5, 0))
        
        # Start Button
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill='x', **padding)
        self.start_btn = tk.Button(btn_frame, text="Start Conversion", command=self.start_processing, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.start_btn.pack(fill='x')
        
        # Progress
        progress_frame = tk.Frame(self)
        progress_frame.pack(fill='x', **padding)
        self.status_label = tk.Label(progress_frame, text="Ready")
        self.status_label.pack(anchor='w')
        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill='x')
        
        # Log Area
        log_frame = tk.Frame(self)
        log_frame.pack(fill='both', expand=True, **padding)
        tk.Label(log_frame, text="Log:").pack(anchor='w')
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_area.pack(fill='both', expand=True)
        
    def select_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_var.set(path)
            # User Requirement: Output directory defaults to input directory
            if not self.output_var.get():
                self.output_var.set(path)
            
    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_var.set(path)
            
    def start_processing(self):
        input_dir = self.input_var.get()
        output_dir = self.output_var.get()
        
        if not input_dir:
            self.log("Please select an input directory.")
            return
            
        if not os.path.exists(input_dir):
            self.log(f"Error: Input directory '{input_dir}' does not exist.")
            return
            
        # Disable buttons
        self.start_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.log_area.delete(1.0, tk.END)
        self.log(f"Starting conversion...\nInput: {input_dir}\nOutput: {output_dir}\n")
        
        # Run in thread
        threading.Thread(target=self.run_conversion, args=(input_dir, output_dir), daemon=True).start()
        
    def run_conversion(self, input_dir, output_dir):
        try:
            target_output = output_dir if output_dir.strip() else None
            
            converter.process_directory(
                input_dir, 
                target_output, 
                progress_callback=self.update_progress,
                log_callback=self.log
            )
            self.log("Processing complete!")
        except Exception as e:
            self.log(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.after(0, lambda: self.start_btn.config(state='normal'))

    def update_progress(self, current, total, desc):
        # Update GUI from thread safely
        self.after(0, lambda: self._update_progress_gui(current, total, desc))
        
    def _update_progress_gui(self, current, total, desc):
        if total > 0:
            self.progress_bar['maximum'] = total
            self.progress_bar['value'] = current
        self.status_label.config(text=desc)

    def log(self, message):
        self.after(0, lambda: self._log_gui(message))
        
    def _log_gui(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
