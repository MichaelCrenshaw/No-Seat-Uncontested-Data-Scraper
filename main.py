import bs4
import requests

import pandas as pd

from csv import DictReader, DictWriter

pages_df_header = ["Chamber", "URN", "Majority party", "IMG"]
final_df_header = ["Democratic", "Republican", "Other", "Chamber"]


def main():
    pages_df = gather_pages()
    pages = pages_df['URN']
    chambers = pages_df['Chamber']

    dataframes = []
    for page, chambers in zip(pages, chambers):
        try:
            page_data = scrape_page(urn=page, chamber=chambers)
            dataframes.append(page_data)
        except AttributeError as e:
            print(e)

    df = pd.concat(dataframes)
    df.to_csv("final_df.csv")


def scrape_page(chamber: str, urn: str) -> pd.DataFrame:
    url = "https://ballotpedia.org" + urn
    print(url)
    html = requests.get(url)

    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    # print(soup)
    table = soup.find("table", class_="wikitable sortable collapsible candidateListTablePartisan")\
                .find('tbody')\
                .find_all('tr')[2:]

    data = []
    for elm in table:
        row = []
        # gather valid data of each row
        for value in elm:
            try:
                if value.get_text() == "\n":
                    continue
                row.append(value.get_text())

            except Exception as e:
                print(e)
                continue

        data.append(row)

    df = pd.DataFrame(data)
    df["Chamber"] = [chamber for i in range(len(df))]

    df = df.replace(r'\n', '', regex=True)
    df = df.replace(r'\s+', ' ', regex=True)
    df.to_csv(f'./output/{chamber}_data')

    return df


# gather table data for each chamber with election data
def gather_pages() -> pd.DataFrame:
    html = requests.get('https://ballotpedia.org/State_legislative_elections,_2022')

    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    table = soup.find_all('table')[2].find('tbody').find_all('tr')[2:]

    data = []
    for elm in table:
        row = []
        # gather valid data of each row
        for value in elm:
            try:
                if value.get_text() == "\n":
                    continue
                if value.find('a') is None:
                    continue
                row.append(value.get_text())
                row.append(value.find('a')['href'])

            except Exception as e:
                print(e)
                continue

        data.append(row)

    df = pd.DataFrame(data, columns=pages_df_header)

    df = df.replace(r'\n', '', regex=True)
    df.to_csv('./pages.csv')

    return df


if __name__ == '__main__':
    main()
