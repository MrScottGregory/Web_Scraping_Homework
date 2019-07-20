from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
import os




def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

    # define all values w/ reference to functions below
    mars_title, mars_p = mars_news(browser)

    featured_url = mars_image(browser)

    weather = mars_weather(browser)

    facts = mars_facts(browser)

    image_urls = mars_hemispheres(browser)

    # create dictionary to hold all mars_data
    mars_data = {
                "mars_title": mars_title,
                "mars_p": mars_p,
                "featured_url": featured_url,
                "weather": weather,
                "facts": facts,
                "image_urls": image_urls
                }

    # close the browser after scraping
    browser.quit()

    # return results
    return mars_data

def mars_news(news_browser):
    # visit URL of page to be scraped for articles
    article_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    news_browser.visit(article_url)

    # scrape page into Soup
    html = news_browser.html
    soup = bs(html, 'html.parser')

    # find first article title 
    news_title = soup.find(class_ ='content_title').text

    # find first article description 
    news_p = soup.find(class_='article_teaser_body').text

    # Return results
    return news_title, news_p

def mars_image(image_browser):
    # visit URL of page to be scraped for featured image
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    image_browser.visit(image_url)

    # scrape page into Soup
    html = image_browser.html
    soup = bs(html, 'html.parser')

    # find and build url
    article = soup.find('article')
    style = article['style']
    parsed_string = style.split("'")
    base_url = parsed_string[1]
    url = ('https://www.jpl.nasa.gov' + base_url)

    return url

def mars_weather(weather_browser):
    # visit URL of page to be scraped for tweet
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    weather_browser.visit(weather_url)

    # scrape page into Soup
    html = weather_browser.html
    soup = bs(html, 'html.parser')

    # find most recent weathertweet
    tweet= soup.find(string=re.compile("InSight sol"))
    return tweet

def mars_facts(facts_browser):
    # visit URL of page to be scraped for facts
    facts_url = 'https://space-facts.com/mars'
    facts_browser.visit(facts_url)

    # scrape page into Soup
    html = facts_browser.html
    soup = bs(html, 'html.parser')

    # scrape to find fact chart 
    facts_tables = pd.read_html(facts_url)
    facts_tables
    mars_df = facts_tables[1]

    # rename columns
    mars_df.columns = ["Description","Values"]
    
    # reset index
    mars_df = mars_df.iloc[1:]
    mars_df.set_index('Description', inplace=True)

    # convert to HTML string
    mars_table = mars_df.to_html()

    return mars_table

def mars_hemispheres(hemispheres_browser):
    # visit URL of page to be scraped for hemispheres info
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemispheres_browser.visit(hemispheres_url)

    # scrape page into Soup
    html = hemispheres_browser.html
    soup = bs(html, 'html.parser')

    # create lists to hold hemisphere URLs and hemisphere titles
    hem_url_list = []
    hem_title_list = []

    # inspect site, locate the instances in the HTML with a 'div' with a 'description' class
    image_div = soup.find_all("div", class_="description")

    # loop through each of those instances, identifying the base image URL, and append to list
    for div in image_div:
        hem_url_list.append(div.a["href"])
        
    # while looping, also identify the title, and append to that list
        hem_title_list.append(div.h3.text)

    # create list to hold image urls
    image_list = []

    # create a new loop to iterate through each URL 
    for url in hem_url_list:
        
    # concatenate the base url to each hem url to create the url paths we'll need
        url_path = ('https://astrogeology.usgs.gov' + url)

    # use spliter to read and parse html
        url_browser = Browser("chrome", headless=False)
        url_browser.visit(url_path)
        html = url_browser.html
        soup = bs(html, 'html.parser')
        
    # drill down to find image URL
        image_div = soup.find("div", id="wide-image")
        image_line = image_div.find("img", class_="wide-image")
        image = image_line["src"]
        image_url = ('https://astrogeology.usgs.gov' + image)
        
    # append to image list
        image_list.append(image_url)

    # create list to hold dictionaries
    hemisphere_image_urls =[]

    # loop through title_list and image_list and add values to dictionaries
    for title, image in zip(hem_title_list, image_list):
        dict={}
        dict['title'] = title
        dict['img_url'] = image
        
    # append dictionaries to list
        hemisphere_image_urls.append(dict)

    return hemisphere_image_urls

# for testing purposes only
# print(scrape())
