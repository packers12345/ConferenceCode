import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from requirements import example_system_requirements
from system_designs import example_system_designs
from verification_requirements import example_verification_requirements
import api_integration

class SystemModelApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("System Model Analysis Interface")
        self.root.geometry("800x600")

        # Variables
        self.api_key = tk.StringVar()
        self.system_requirements = tk.StringVar()
        self.results = ""
        self.selected_table = tk.StringVar()  # For dropdown selection

        self.create_layout()
        self.populate_table_dropdown()  # Populate the dropdown on startup

    def create_layout(self):
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill='both', expand=True)

        # API Configuration Section
        api_section = ttk.LabelFrame(main_container, text="API Configuration", padding="5")
        api_section.pack(fill='x', pady=(0, 10))

        ttk.Label(api_section, text="Gemini API Key:").pack(pady=2)
        ttk.Entry(api_section, textvariable=self.api_key, width=50).pack(pady=2)
        ttk.Button(api_section, text="Initialize API", command=self.initialize_api).pack(pady=2)

        # System Requirements Section
        requirements_section = ttk.LabelFrame(main_container, text="System Requirements", padding="5")
        requirements_section.pack(fill='x', pady=(0, 10))

        ttk.Label(requirements_section, text="Enter System Requirements:").pack(pady=2)
        self.requirements_text = tk.Text(requirements_section, height=10, width=60)
        self.requirements_text.pack(pady=2)
        ttk.Button(requirements_section, text="Submit Requirements", command=self.submit_requirements).pack(pady=2)

        # Table Selection Section
        table_section = ttk.LabelFrame(main_container, text="Select Table for Reference", padding="5")
        table_section.pack(fill='x', pady=(0, 10))

        ttk.Label(table_section, text="Select a table:").pack(pady=2)
        self.table_dropdown = ttk.Combobox(table_section, textvariable=self.selected_table, state="readonly")
        self.table_dropdown.pack(pady=2)
        # A refresh button in case tables change:
        ttk.Button(table_section, text="Refresh Table List", command=self.populate_table_dropdown).pack(pady=2)

        # Run Analysis Button
        ttk.Button(main_container, text="Run Analysis", command=self.run_analysis).pack(pady=10)

        # Check Out Results Button
        ttk.Button(main_container, text="Check Out Results", command=self.show_results).pack(pady=5)

        # Download Results Button
        ttk.Button(main_container, text="Download Results", command=self.download_results).pack(pady=5)

    def populate_table_dropdown(self):
        """Fetch the table list from the database and populate the dropdown."""
        tables = api_integration.list_all_tables()
        if tables:
            self.table_dropdown['values'] = tables
            # Optionally, set the first table as the default selection:
            self.selected_table.set(tables[0])
        else:
            self.table_dropdown['values'] = []
            self.selected_table.set("")

    def initialize_api(self):
        if api_integration.initialize_api(self.api_key.get()):
            messagebox.showinfo("Success", "API initialized successfully")
        else:
            messagebox.showerror("Error", "Failed to initialize API")

    def submit_requirements(self):
        self.system_requirements = self.requirements_text.get("1.0", tk.END).strip()
        messagebox.showinfo("Info", "System requirements submitted successfully")

    def run_analysis(self):
        try:
            # Retrieve the selected table from the dropdown.
            table_name = self.selected_table.get().strip()
            # Optionally, if a table is selected, append a reference into the system requirements text.
            # This ensures that your backend detect_table_name() finds it.
            user_reqs = self.system_requirements
            if table_name and f"table {table_name}" not in user_reqs.lower():
                user_reqs += f"\nPlease reference table {table_name} for proof."
            
            result = api_integration.generate_system_designs(
                user_reqs, 
                example_system_requirements, 
                example_system_designs
            )
            self.results = result
            messagebox.showinfo("Success", "Analysis completed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")

    def show_results(self):
        # Create a new window to display the results
        results_window = tk.Toplevel(self.root)
        results_window.title("Analysis Results")
        results_window.geometry("800x600")

        results_text = tk.Text(results_window, width=100, height=30)
        results_text.pack(pady=10, fill='both', expand=True)
        results_text.insert(tk.END, self.results)
        results_text.config(state='disabled')

    def download_results(self):
        # Open a file dialog to save the results
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.results)
            messagebox.showinfo("Success", "Results downloaded successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemModelApp(root)
    root.mainloop()
