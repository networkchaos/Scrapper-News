import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import psycopg2


#Database connection
def conn_Db():
    #connection to postgres structure database 
    pass


#Scrapper backend for scarping
def scrape_and_store_news(url):
    #scrapping logic
    pass













#frontend
class ScrapperNews:
    def __init__(self, master):
        self.master = master
        self.master.title("News Scrapper App")


        #create Tkinter widgets (labels, entry, button, etc.)
        self.label = tk.Label(master, text="Enter the News Website URL:")
        self.entry = tk.Entry(master, width = 50)
        self.button = tk.Button(master, text="Scrape and Display the News ,",command=self.scrape_and_display)



        #pack widget
        self.label.pack()
        self.entry.pack()
        self.button.pack()



    def scrape_and_display(self):
        url = self.entry.get()
        scrapped_data = scrape_and_store_news(url)

def main():
    root = tk.Tk()
    app = ScrapperNews(root)
    root.mainloop()
if __name__=="__main__":
    main()