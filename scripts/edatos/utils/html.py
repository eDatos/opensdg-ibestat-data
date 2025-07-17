from bs4 import BeautifulSoup
import html

def remove_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    whitelist=['br']
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.unwrap()
    return html.unescape(soup.decode_contents())