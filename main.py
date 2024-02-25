import tkinter as tk
from tkinter import messagebox
import requests
from lxml import html
import psycopg2

# Database connection
def conn_Db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="scrapper",
            port="5000",
            user="postgres",
            password="admin"
        )
        return conn
    except (Exception, psycopg2.Error) as Err:
        print(f"Error connecting to the Database: {Err}")
        return None

def table_exists(table_name):
    connection = conn_Db()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table_name,))
            return cursor.fetchone()[0]

def create_users_table():
    try:
        if not table_exists('users'):
            connection = conn_Db()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(255) NOT NULL,
                            password VARCHAR(255) NOT NULL
                        )
                    """)

                    cursor.execute("SELECT * FROM users WHERE username = %s", ('admin',))
                    admin_exists = cursor.fetchone()

                    if not admin_exists:
                        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', 'admin'))

                connection.commit()
                print("Users table created successfully.")
    except Exception as e:
        print(f"Error creating users table: {e}")

def login():
    login_window = tk.Toplevel()
    login_window.title("Login")
    login_window.geometry("800x800")  # Set width and height

    login_label = tk.Label(login_window, text="LOGIN", font=("Arial", 20, "bold"), fg="purple")
    login_label.pack(pady=10)

    username_label = tk.Label(login_window, text="Username:")
    username_entry = tk.Entry(login_window)
    username_label.pack()
    username_entry.pack()

    password_label = tk.Label(login_window, text="Password:")
    password_entry = tk.Entry(login_window, show="*")
    password_label.pack()
    password_entry.pack()

    login_button = tk.Button(login_window, text="Login", command=lambda: validate_login(username_entry.get(), password_entry.get(), login_window))
    login_button.pack()

    # Center the content in the window
    for widget in login_window.winfo_children():
        widget.pack_configure(anchor='center')

def validate_login(username, password, login_window):
    connection = conn_Db()
    if connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user:
                messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                login_window.destroy()
                open_main_app()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

def open_main_app():
    root.deiconify()
    app = ScrapperNews(root)

def create_database():
    try:
        connection = conn_Db()
        if connection:
            with connection.cursor() as cursor:
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

def scrape_and_store_news(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            tree = html.fromstring(response.content)
            title = tree.xpath('//title/text()')[0]
            paragraphs = tree.xpath('//p/text()')

            connection = conn_Db()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO news (title, content, source) VALUES (%s, %s, %s)",
                                   (title, '\n'.join(paragraphs), url))
                connection.commit()
                print("Data successfully stored in the database.")
                return title, '\n'.join(paragraphs)  # Return both title and content
    except Exception as e:
        print(f"Error scraping and storing news: {e}")
        return None, None

class ScrapperNews:
    def __init__(self, master):
        self.master = master
        self.master.title("News Scraper App")
        self.master.geometry("900x900")  # Set width and height

        self.label = tk.Label(master, text="Enter the News Website URL:")
        self.entry = tk.Entry(master, width=50)
        self.button = tk.Button(master, text="Scrape and Display the News", command=self.scrape_and_display)
        self.result_label = tk.Label(master, text="", justify="left", anchor="w", wraplength=700)

        self.articles = []

        self.label.pack()
        self.entry.pack()
        self.button.pack()
        self.result_label.pack()

        create_database()

    def scrape_and_display(self):
        url = self.entry.get()
        title, content = scrape_and_store_news(url)

        if title and content:
            self.articles.append({"title": title, "content": content, "source": url})
            titles_summary = "\n".join([f"- {article['title']}\n{article['content']}\n" for article in self.articles])
            self.result_label.config(text=f"Articles:\n{titles_summary}", font=("Arial", 12, "bold"), justify="left", anchor="w", wraplength=700)
        else:
            messagebox.showerror("Error", "Error scraping and storing news.")

def main():
    create_users_table()
    global root
    root = tk.Tk()
    root.withdraw()
    login()
    root.mainloop()

if __name__ == "__main__":
    main()
