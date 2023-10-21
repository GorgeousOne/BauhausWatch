# request url and get all links to a protocol
import requests
import re
from bs4 import BeautifulSoup
import datetime
import locale
import os

# Set the locale to German
locale.setlocale(locale.LC_TIME, "de_DE.utf-8")

# download protocols
import urllib.request

import json

def read_json(path):
    with open(path) as f:
        return json.load(f)

processed_links = []

def embed_ocr_text(filepath):
    return

import PyPDF2
def get_protocol_date_from_pdf_file(filepath):
    pdfFileObj = open(filepath, "rb")
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    pageObj = pdfReader.pages[0]

    # only search in the first 300 characters
    text = pageObj.extract_text()[:300]

    print(text)

    if len(text) < 1:
        print("This protocoll needs OCR embedding")

    # search for date in the format 12. Oktober 2022
    match = re.search(r"\d{1,2}\s*\.\s*[\D]+\s*\d{4}", text)
    if match is not None:
        date = match.group(0).replace(" ", "").replace(".", "")
        if date[1] == ".":
            date = "0" + date
        # find it in the german format
        try:
            date = datetime.datetime.strptime(date, "%d%B%Y").date().strftime("%d.%m.%Y") 
        except ValueError:
            date = "Datum unbekannt"
        return date
    
    # search for date in the format 12.10.2022
    match = re.search(r"\d{1,2}\s*\.\s*\d{1,2}\s*\.\s*\d{4}", text)
    if match is not None:
        date = match.group(0).replace(" ", "").replace(".", "")
        if date[1] == ".":
            date = "0" + date
        if date[4] == ".":
            date = date[:3] + "0" + date[3:]
        try:
            date = datetime.datetime.strptime(date, "%d%m%Y").date().strftime("%d.%m.%Y")
        except ValueError:
            date = "Datum unbekannt"
        return date
    
    return "Datum unbekannt"


def name_to_directory_name(name):
    name = name.replace("/", "_")
    name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return name.lower().replace(" ", "_")

def get_protocols_from_url(url, committee, class_name):

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    protocols_added = 0

    links = []
    for link in soup.find_all("a"):
        links.append(link)

    # filter links to protocols
    protocols = []
    for link in links:
        if link is not None and link.get("href") is not None:
            href = "https://www.uni-weimar.de" + link.get("href")
            if ".pdf" in href and href not in processed_links:
                processed_links.append(href)
                protocol = {
                    "date": "Datum unbekannt",
                    "unixdate": 0,
                    "url": href,
                    "filename": href.split("/")[-1],
                    "link_title": link.text,
                    "committee": committee,
                    "class": class_name
                }

                filepath = "downloads/" + name_to_directory_name(protocol["committee"]) + "/" + protocol["filename"]
                
                # check if subdirectory exists
                if not os.path.exists("downloads/" + name_to_directory_name(protocol["committee"])):
                    os.makedirs("downloads/" + name_to_directory_name(protocol["committee"]))
                
                # check if file already exists
                if not os.path.exists(filepath):
                    urllib.request.urlretrieve(protocol["url"], filepath)
                    print("Downloaded " + protocol["url"])

                # get date from pdf file
                protocol["date"] = get_protocol_date_from_pdf_file(filepath)

                if protocol["date"] and protocol["date"] != "Datum unbekannt":
                    protocol["unixdate"] = datetime.datetime.strptime(protocol["date"], "%d.%m.%Y").timestamp()

                protocol["local_url"] = filepath

                pdfFileObj = open(filepath, "rb")
                pdfReader = PyPDF2.PdfReader(pdfFileObj)
                pageObj = pdfReader.pages[0]
                for page in range(len(pdfReader.pages)):
                    if not os.path.exists(filepath[:-4]):
                        os.makedirs(filepath[:-4])
                    txt_filename = filepath[:-4] + "/" + str(page) + ".txt"
                    # if there is no text file for the current page, create one
                    if not os.path.isfile(txt_filename):
                        pageObj = pdfReader.pages[page]
                        text = pageObj.extract_text()
                        with open(txt_filename, "w") as text_file:
                            text_file.write(text)

                print("Found new protocol ", protocol["filename"])

                protocols.append(protocol)

    return protocols

def update():
    global processed_links

    # check if download folder exists
    import os
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    previous_protocols = read_json("protocols.json")
    processed_links  = [proto["url"] for proto in previous_protocols]

    protocols = get_protocols_from_url("https://www.uni-weimar.de/de/kunst-und-gestaltung/struktur/gremien/fakultaetsrat/fakultaetsratsprotokolle/", "Fakultätsrat Kunst und Gestaltung", "art")
    protocols += get_protocols_from_url("https://www.uni-weimar.de/de/universitaet/struktur/gremien/senat/protokolle/", "Senat", "uni")
    protocols += get_protocols_from_url("https://www.uni-weimar.de/de/bauingenieurwesen/struktur/gremien/fakultaetsrat/", "Fakultätsrat Bauingenieurwesen", "engineering")
    protocols += get_protocols_from_url("https://www.uni-weimar.de/de/architektur-und-urbanistik/struktur/gremien/fakultaetsrat/", "Fakultätsrat Architektur & Urbanistik", "architecture")
    protocols += get_protocols_from_url("https://www.uni-weimar.de/de/medien/struktur/gremien/fakultaetsrat/fakultaetsratsprotokolle/", "Fakultätsrat Medien", "media")

    protocols += previous_protocols

    # sort protocols by date
    protocols = sorted(protocols, key=lambda k: k["unixdate"], reverse=True)

    return
    # save protocols to json file
    import json
    with open("protocols.json", "w") as f:
        json.dump(protocols, f, indent=4)


