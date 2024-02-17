import tkinter as tk
from tkinter import messagebox
import requests
from lxml import html
import psycopg2

# Database connection
def conn_Db():
    # Replace the empty strings with your actual PostgreSQL credentials
    try:
        conn = psycopg2.connect(
            host="your_host",
            database="your_database",
            port="your_port",
            user="your_username",
            password="your_password"
        )
        return conn
    except (Exception, psycopg2.Error) as Err:
        print(f"Error connecting to the Database: {Err}")
        return None

# Create the database and table
def create_database():
    try:
        connection = conn_Db()
        if connection:
            with connection.cursor() as cursor:
                # Create the 'news' table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS news (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255),
                        content TEXT,
                        source VARCHAR(255)
                    )
                """)
            connection.commit()
            print("Database and table created successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")

# Scraper backend for scraping
def scrape_and_store_news(url):
    try:
        # Make an HTTP request to the specified URL
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML content
            tree = html.fromstring(response.content)
            
            # Extract title using XPath
            title = tree.xpath('//title/text()')[0]

            # Extract paragraphs using XPath
            paragraphs = tree.xpath('//p/text()')

            # Connect to the database
            connection = conn_Db()
            if connection:
                # Insert the scraped data into the database
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO news (title, content, source) VALUES (%s, %s, %s)",
                                   (title, '\n'.join(paragraphs), url))
                connection.commit()
                print("Data successfully stored in the database.")
                return title, paragraphs
    except Exception as e:
        print(f"Error scraping and storing news: {e}")
        return None, None

# Frontend
class ScrapperNews:
    def __init__(self, master):
        self.master = master
        self.master.title("News Scraper App")

        # Create Tkinter widgets (labels, entry, button, etc.)
        self.label = tk.Label(master, text="Enter the News Website URL:")
        self.entry = tk.Entry(master, width=50)
        self.button = tk.Button(master, text="Scrape and Display the News", command=self.scrape_and_display)
        self.result_label = tk.Label(master, text="", justify="left", anchor="w", wraplength=500)

        # List to store scraped articles
        self.articles = []

        # Pack widgets
        self.label.pack()
        self.entry.pack()
        self.button.pack()
        self.result_label.pack()

        # Create the database and table on initialization
        create_database()

    def scrape_and_display(self):
        url = self.entry.get()
        title, paragraphs = scrape_and_store_news(url)

        if title and paragraphs:
            # Append the scraped data to the list of articles
            self.articles.append({"title": title, "content": '\n'.join(paragraphs), "source": url})

            # Display a summary of titles in the Tkinter interface
            titles_summary = "\n".join([f"- {article['title']}" for article in self.articles])
            self.result_label.config(text=f"Articles:\n{titles_summary}", font=("Arial", 12), justify="left", anchor="w", wraplength=500)
        else:
            # Display an error message using messagebox
            messagebox.showerror("Error", "Error scraping and storing news.")

def main():
    root = tk.Tk()
    app = ScrapperNews(root)
    root.mainloop()

if __name__ == "__main__":
    main()
