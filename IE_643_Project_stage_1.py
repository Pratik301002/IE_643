import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Define your scraping functions
def nips_papers(year):
  paper = []
  links = []
  pdf = []
  url = f"https://papers.nips.cc/paper_files/paper/{year}"
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  titles = soup.find_all('a',href=True)

  for title in titles:
    href = title.get('href')
    links.append('https://papers.nips.cc/'+href)
    paper.append(title.text.strip())
    href = href.replace('/hash','/file')
    pdf_link = href.replace('Abstract.html', 'Paper.pdf')
    pdf.append('https://papers.nips.cc'+pdf_link)
  df = pd.DataFrame({'title':paper,'link':links, 'pdf link':pdf})
  df = df[4:-2]
  df.reset_index(drop=True,inplace=True)
  return df

def acl_papers(years):
  url = f"https://aclanthology.org/events/acl-{years}/"
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  strong = soup.find_all('strong')
  u = []
  abs = []
  pdf = []
  for i in strong :
    if "https://github.com/baidu" not in i.find_next('a').text:
      if "pdf\n" not in i.find_next('a').text:
        u.append(i.find_next('a').text)
        abs.append("https://aclanthology.org/"+i.find_next('a').get('href'))


  pdf_link = soup.find_all('span',class_="d-block mr-2 text-nowrap list-button-row")
  for text in pdf_link:
    if "https://aclanthology.org/" not in text.find('a').get('href'):
      pdf.append("https://aclanthology.org/"+text.find('a').get('href'))
    else:
      link = text.find('a').get('href')
      link = link.replace('.bib','')
      pdf.append(link)
  df = pd.DataFrame({'title':u,'link':abs})
  return df

def eccv_papers(year):
    paper = []
    links = []
    pdf = []
    url = "https://www.ecva.net/papers.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.find_all('div', class_='accordion-content')

    for title in titles:
        anchors = title.find_all('a')

        for anchor in anchors:
            href = anchor.get('href')
            if href:
                if href.endswith('.php') and f'eccv_{year}' in href:
                    paper_title = anchor.text.strip()
                    if paper_title:
                        paper.append(paper_title)
                        full_url = f'https://www.ecva.net/{href}'
                        links.append(full_url)

                if href.endswith('.pdf') and f'eccv_{year}' in href and not href.endswith('-supp.pdf'):
                    pdf_link = f'https://www.ecva.net/{href}'
                    pdf.append(pdf_link)

    df = pd.DataFrame({'title': paper, 'link': links, 'pdf link': pdf})
    df.reset_index(drop=True, inplace=True)
    return df

def iclr_papers(year):
    text = []
    link = []
    url = f"https://iclr.cc/virtual/{year}/papers.html?filter=titles"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find('ul', class_="nav nav-pills")
    titles = title.find_next('ul').find_all('a')

    for head in titles:
        text.append(head.text)
        link.append("https://iclr.cc/" + head.get('href'))

    df = pd.DataFrame({'title': text, 'link': link})
    return df

def icml_papers(year):
    icml_volumes = {
    2016: 48,
    2017: 70,
    2018: 80,
    2019: 97,
    2020: 119,
    2021: 139,
    2022: 162,
    2023: 202,
    2024: 250  # Hypothetical for 2024, update when available
}
    year = int(year)
    paper_titles = []
    paper_links = []
    pdf_links = []
    paper_years = []

    # Get the volume number for the year
    volume = icml_volumes.get(year)
    if volume is None:
        print(f"Volume for ICML {year} is not available.")
        return None

    # URL of the ICML page for a specific year
    url = f"https://proceedings.mlr.press/v{volume}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all paper listings
    papers = soup.find_all('div', class_='paper')

    # Check if papers were found
    if not papers:
        print(f"No papers found for ICML {year} at {url}")
        return None

    # Loop over all papers
    for paper_div in papers:
        # Get the title from 'p' tag with class 'title'
        title = paper_div.find('p', class_='title').text.strip()
        # Get the paper link from 'a' tag (if available)
        paper_link = paper_div.find('a').get('href')
        if not paper_link.startswith('http'):
            paper_link = f"https://proceedings.mlr.press{paper_link}"

        # Get the PDF link (from 'a' tag with text 'Download PDF')
        pdf_link = paper_div.find('a', text="Download PDF")
        if pdf_link:
            pdf_link = pdf_link.get('href')
            if not pdf_link.startswith('http'):
                pdf_link = f"https://proceedings.mlr.press{pdf_link}"
        else:
            pdf_link = 'No PDF link available'

        # Append the title, link, PDF, and year
        paper_titles.append(title)
        paper_links.append(paper_link)
        pdf_links.append(pdf_link)
        paper_years.append(year)

    # Create DataFrame with scraped data
    df = pd.DataFrame({
        'title': paper_titles,
        'paper link': paper_links,
        'pdf link': pdf_links,
    })

    return df

class ConferenceScraper:
    def __init__(self, conf, year):
        self.conf = conf
        self.year = year
        self.base_url = f"https://openaccess.thecvf.com/{self.conf}{self.year}"
        self.data = pd.DataFrame()
        self.paper_names = []
        self.links = []
        self.pdf = []

    def get_all_papers(self):
        url = f"{self.base_url}?day=all"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        paper_titles = soup.find_all('dt', class_='ptitle')

        for title in paper_titles:
            paper_title = title.find('a').text.strip()
            self.paper_names.append(paper_title)
            # Extract links to papers
            a_tag = title.find('a')
            if a_tag:
                paper_link = a_tag.get('href')
                self.links.append(f"http://openaccess.thecvf.com/{paper_link}")

        paper_titles = soup.find_all('dd')
        for paper in paper_titles:
            pdf_link = paper.find('a').get('href')
            if pdf_link and pdf_link.endswith('.pdf'):
                self.pdf.append("http://openaccess.thecvf.com/" + pdf_link)

        # Create a DataFrame with the titles and links
        self.data = pd.DataFrame({
            "title": self.paper_names,
            "link": self.links,
            "pdf link": self.pdf
        })
        return self.data

    def get_papers_by_day(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        dates = soup.find_all('a', href=True)

        # Iterate over the dates and scrape papers for each day
        for date in dates:
            if 'Day' in date.text:
                date_only = date.text.split(':')[-1].strip()
                day_url = f"{self.base_url}?day={date_only}"
                day_response = requests.get(day_url)
                day_soup = BeautifulSoup(day_response.text, "html.parser")

                paper_titles = day_soup.find_all('dt', class_='ptitle')
                for title in paper_titles:
                    paper_title = title.find('a').text.strip()
                    self.paper_names.append(paper_title)
                    a_tag = title.find('a')
                    if a_tag:
                        paper_link = a_tag.get('href')
                        self.links.append(f"http://openaccess.thecvf.com/{paper_link}")

                paper_titles = day_soup.find_all('dd')
                for paper in paper_titles:
                    pdf_link = paper.find('a').get('href')
                    if pdf_link and pdf_link.endswith('.pdf'):
                        self.pdf.append("http://openaccess.thecvf.com/" + pdf_link)

        # Create a DataFrame with the titles and links
        self.data = pd.DataFrame({
            "title": self.paper_names,
            "link": self.links,
            "pdf link": self.pdf
        })
        return self.data

    def fetch_conference_papers(self):
        self.data = self.get_all_papers()

        if self.data.empty:
            print(f"No papers found for {self.conf} {self.year} in 'all days'. Fetching by individual days...")
            self.data = self.get_papers_by_day()
            if self.data.empty:
                return print(f"No papers found for {self.conf} {self.year}.")
        return self.data

# Streamlit app
st.title("Conference Paper Scraper")

# Dropdown for conference selection
conferences = {
    "CVPR": "cvpr",
    "ICCV": "iccv",
    "NIPS": nips_papers,
    "ACL": acl_papers,
    "ECCV": eccv_papers,
    "ICML": icml_papers,
    "ICLR": iclr_papers,

}

Years = [
  "2016","2017","2018","2019","2020","2021","2022","2023","2024"
]

Years_eccv = ["2018","2020","2022"]

# User input for conference selection
conference_name = st.selectbox("Select Conference", options=list(conferences.keys()))

if conference_name == "ECCV":
  year = st.selectbox("Select Year",options=Years_eccv)
else:
  year = st.selectbox("Select Year",options=Years)

# Button to fetch papers
if st.button("Fetch Papers"):
    if conference_name in ["CVPR", "ICCV"]:
        scraper = ConferenceScraper(conf=conferences[conference_name].upper(), year=year)
        fetched_data = scraper.fetch_conference_papers()
    else:
        scraper_function = conferences[conference_name]
        fetched_data = scraper_function(year)

    if fetched_data is not None and not fetched_data.empty:
        st.success(f"Fetched {len(fetched_data)} papers for {conference_name} {year}.")
        st.dataframe(fetched_data)

        # Button to download CSV
        csv = fetched_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{conference_name}_{year}_papers.csv",
            mime='text/csv'
        )
    else:
        st.error(f"No papers found for {conference_name} {year}.")
