The goal of this project was to create an application where i could ask for a manga, an anime or a moovie and it would open the right link.
It would open the right episode (the first one if it's the first time i am watching the anime/ or the next episode if I already watched some)

# Explanation of the project : 

To manage that I created files .csv that are the database of my project. 
- One for each type of things i can ask about (moovie, anime ...)
- One to be able to know when was the last update

To fetch the data i need, I scrapped a lot of different website. 


I used python for the scrapping with 2 differents library : 
- selenium
- BeautifulSoup

MoreOver, I used TkInter to create a little application to avoid asking what I am looking for in the terminal.

# Main Problem 
The website are changing (The URL or just the HTML) so the code is not working anymore. 
