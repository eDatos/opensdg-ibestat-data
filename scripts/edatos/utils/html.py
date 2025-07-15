from bs4 import BeautifulSoup

def remove_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    whitelist=['br']
    for tag in soup.find_all(True):
        if tag.name not in whitelist:
            tag.unwrap()
    return soup.decode_contents() 