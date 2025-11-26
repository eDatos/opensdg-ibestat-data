from bs4 import BeautifulSoup
import html

def remove_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    whitelist=['br']
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.unwrap()
    # https://stackoverflow.com/questions/79268152/why-does-beautifulsoup-output-self-closing-tags-in-html
    return html.unescape(soup.decode_contents(None, 'utf-8', 'html5'))