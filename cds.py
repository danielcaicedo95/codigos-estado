import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd

def get_links(url):
    internal_links = []
    external_links = []

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('#'):
                internal_links.append(urljoin(url, href))
            elif urlparse(href).netloc == '':
                internal_links.append(urljoin(url, href))
            else:
                external_links.append(href)

    except requests.RequestException as e:
        print(f"Error al obtener la página: {e}")
        return None, None

    return internal_links, external_links


def get_link_data(links, link_type):
    data = {'Enlace': [], 'Anchor Text': [], 'Código de Estado': []}

    for link in links:
        try:
            response = requests.head(link)
            status_code = response.status_code
            anchor_text = link.text.strip() if hasattr(link, 'text') and link.text else "No tiene"
            data['Enlace'].append(link)
            data['Anchor Text'].append(anchor_text)
            data['Código de Estado'].append(status_code)

        except requests.RequestException as e:
            data['Enlace'].append(link)
            data['Anchor Text'].append("No tiene")
            data['Código de Estado'].append("Error")

    return pd.DataFrame(data)


if __name__ == "__main__":
    url = input("Introduce la URL: ")
    internal_links, external_links = get_links(url)

    if internal_links is not None and external_links is not None:
        internal_df = get_link_data(internal_links, "INTERNAL")
        external_df = get_link_data(external_links, "EXTERNAL")

        internal_df.to_csv('enlaces_internos.csv', index=False)
        external_df.to_csv('enlaces_externos.csv', index=False)

        print("Los resultados se han guardado en 'enlaces_internos.csv' y 'enlaces_externos.csv'.")
