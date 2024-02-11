import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog
import os
import requests
from bs4 import BeautifulSoup

class WebsiteScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Website Scraper")
        master.geometry("600x400")

        self.label = tk.Label(master, text="Enter Website URL:", font=("Helvetica", 14))
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.url_entry = tk.Entry(master, width=40, font=("Helvetica", 12))
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_folder, font=("Helvetica", 12))
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.submit_button = tk.Button(master, text="Scrape Website", command=self.scrape_website, font=("Helvetica", 14))
        self.submit_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_scraping, font=("Helvetica", 14), state=tk.DISABLED)
        self.stop_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        self.output_text = scrolledtext.ScrolledText(master, width=60, height=10, font=("Helvetica", 12))
        self.output_text.grid(row=2, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.created_by_label = tk.Label(master, text="Created by Zoubaire", font=("Helvetica", 10), fg="gray")
        self.created_by_label.grid(row=3, columnspan=3, padx=10, pady=5, sticky="s")

        self.selected_folder = None
        self.is_scraping = False

        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)

    def browse_folder(self):
        self.selected_folder = filedialog.askdirectory()

    def scrape_website(self):
        self.is_scraping = True
        self.submit_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        url = self.url_entry.get()

        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            self.stop_scraping()
            return

        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a destination folder")
            self.stop_scraping()
            return

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch website: {e}")
            self.stop_scraping()
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find and save HTML code
        html_code = soup.prettify()

        # Find and save CSS code
        css_code = ''
        for css_link in soup.find_all('link', {'rel': 'stylesheet'}):
            css_url = css_link.get('href')
            if css_url.startswith('http'):
                css_response = requests.get(css_url)
                if css_response.status_code == 200:
                    css_code += css_response.text + '\n'

        # Find and save JavaScript code
        js_code = ''
        for script in soup.find_all('script'):
            if script.get('src'):
                js_url = script.get('src')
                if js_url.startswith('http'):
                    js_response = requests.get(js_url)
                    if js_response.status_code == 200:
                        js_code += js_response.text + '\n'
            else:
                js_code += script.get_text() + '\n'

        with open(os.path.join(self.selected_folder, 'index.html'), 'w') as html_file:
            html_file.write(html_code)
        with open(os.path.join(self.selected_folder, 'styles.css'), 'w') as css_file:
            css_file.write(css_code)
        with open(os.path.join(self.selected_folder, 'script.js'), 'w') as js_file:
            js_file.write(js_code)

        if self.is_scraping:
            self.output_text.insert(tk.END, "HTML, CSS, and JS files saved successfully!\n")
            messagebox.showinfo("Success", "Website scraped successfully! Files saved in the selected folder.")

        self.stop_scraping()

    def stop_scraping(self):
        self.is_scraping = False
        self.submit_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = WebsiteScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
