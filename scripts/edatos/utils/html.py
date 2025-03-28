from bs4 import BeautifulSoup

def remove_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text() 