import requests
import csv
import re
from typing import List, Dict, Optional
from pydantic import BaseModel
from tqdm import tqdm

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

class Paper(BaseModel):
    pubmed_id: str
    title: str
    pub_date: str
    non_academic_authors: List[str]
    company_affiliations: List[str]
    corresponding_email: Optional[str]

def fetch_pubmed_ids(query: str) -> List[str]:
    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 100
    })
    response.raise_for_status()
    return response.json()["esearchresult"]["idlist"]

def fetch_pubmed_details(pubmed_ids: List[str]) -> List[Paper]:
    papers: List[Paper] = []

    for pubmed_id in tqdm(pubmed_ids, desc="Fetching papers"):
        resp = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params={
            "db": "pubmed",
            "id": pubmed_id,
            "retmode": "xml"
        })
        if not resp.ok:
            continue

        xml = resp.text
        title = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", xml)
        pub_date = re.search(r"<PubDate>.*?<Year>(\d+)</Year>", xml)
        affiliations = re.findall(r"<Affiliation>(.*?)</Affiliation>", xml)
        authors = re.findall(r"<LastName>(.*?)</LastName>", xml)
        emails = EMAIL_PATTERN.findall(xml)

        non_acad_authors = []
        companies = []

        for aff in affiliations:
            if not re.search(r"(univ|college|school|institute|dept|department|lab)", aff, re.I):
                companies.append(aff)
                non_acad_authors.extend(authors)

        paper = Paper(
            pubmed_id=pubmed_id,
            title=title.group(1) if title else "N/A",
            pub_date=pub_date.group(1) if pub_date else "N/A",
            non_academic_authors=list(set(non_acad_authors)),
            company_affiliations=list(set(companies)),
            corresponding_email=emails[0] if emails else None
        )
        papers.append(paper)
    return papers

def save_to_csv(papers: List[Paper], filename: str):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "PubmedID", "Title", "Publication Date",
            "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"
        ])
        for paper in papers:
            writer.writerow([
                paper.pubmed_id,
                paper.title,
                paper.pub_date,
                "; ".join(paper.non_academic_authors),
                "; ".join(paper.company_affiliations),
                paper.corresponding_email or ""
            ])
