#!/usr/bin/env python3

"""
Author: Bhavyai Gupta
Description: Scrapes the website "https://open.epic.com/" for all set of APIs
"""

import argparse
import json

import requests
from bs4 import BeautifulSoup


def getBaseURL() -> str:
    return "https://open.epic.com"


def getHTMLContent(url: str) -> str:
    """Returns the page content for the given URL."""
    response = requests.get(url)
    return response.text


def readDataJSON(filename: str) -> list[dict]:
    """Reads the data from a JSON file."""
    with open(filename, "r") as infile:
        return json.load(infile)


def storeDataJSON(allResults: list[dict], filename: str) -> None:
    """Stores the data in a JSON file."""
    with open(filename, "w") as outfile:
        json.dump(allResults, outfile, indent=2)


def getAllInterfaceTypes() -> list[str]:
    return [
        "HL7v2",
        "HL7v3",
        "IHE",
        "FHIR",
        "WebServices",
        "DICOM",
        "NCPDP",
        "X12",
        "Other",
    ]


def parseAPISection(interfaceType: str) -> dict:
    url = f"{getBaseURL()}/Interface/{interfaceType}"
    content = getHTMLContent(url)
    soup = BeautifulSoup(content, "html.parser")

    pageResults = []
    interfaceHeading = ""
    interfaceDescription = ""

    # get the list of interfaces
    interfaceList = soup.find("div", class_="interface-list interface-list-content")

    interfaceHeading = interfaceList.find("h2").text.strip()
    interfaceDescription = (
        interfaceList.find("div", class_="mainSection").get_text(separator=" ").strip()
    )

    for h3, div in zip(
        interfaceList.find_all("h3", class_="interface-title"),
        interfaceList.find_all("div", class_="subSection"),
    ):

        try:
            # get the API document link first
            specLinkText = ""
            specLink = "#"
            anchor = h3.find("a")
            if anchor:
                specRelativeLink = anchor.get("href")
                specLink = f"{getBaseURL()}/{specRelativeLink}"
                specLinkText = anchor.text.strip()

            # prepare the heading
            heading = h3.text.replace(specLinkText, "").strip()

            # get the description
            description = (
                div.find("div", class_="html-description")
                .get_text(separator=" ")
                .strip()
            )

            newData = {
                "heading": heading,
                "description": description,
                "specLink": specLink,
            }

            pageResults.append(newData)

        except Exception as e:
            print("eror: parsing API interface: ", h3.text.strip())
            print(e)
            continue

    return {
        "interfaceHeading": interfaceHeading,
        "interfaceDescription": interfaceDescription,
        "interfaceLink": url,
        "list": pageResults,
    }


def generateSingleHTML() -> None:
    savedData = readDataJSON("scrape_results.json")

    html = "<html><body>"

    for item in savedData:
        interface_heading = item["interfaceHeading"]
        interface_description = item["interfaceDescription"]
        interface_link = item["interfaceLink"]

        html += f"<h2><a href='{interface_link}'>{interface_heading}</a></h2>"
        html += f"<p>{interface_description}</p>"

        html += "<ul>"

        for sub_item in item["list"]:
            sub_heading = sub_item["heading"]
            sub_description = sub_item["description"]
            spec_link = sub_item["specLink"]

            if spec_link == "#":
                html += f"<li><strong>{sub_heading}</strong>: {sub_description}</li>"

            else:
                html += f"<li><strong><a href='{spec_link}'>{sub_heading}</a></strong>: {sub_description}</li>"

        html += "</ul>"

    html += "</body></html>"

    with open("scrape_results.html", "w") as f:
        f.write(html)


def beginParse() -> None:
    allResults = []

    for interfaceType in getAllInterfaceTypes():
        print("info: parsing data for interface type", interfaceType)
        allResults.append(parseAPISection(interfaceType))

    print("info: writing data as JSON")
    storeDataJSON(allResults, "scrape_results.json")


if __name__ == "__main__":
    """Driver code"""
    parser = argparse.ArgumentParser(
        description="Scrape https://open.epic.com/ for all set of APIs"
    )
    parser.add_argument(
        "-p", "--parse", action="store_true", help="Parse the data from the website"
    )
    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Generate HTML from the parsed data",
    )
    args = parser.parse_args()

    if args.parse:
        print("info: begin parsing")
        beginParse()

    elif args.generate:
        print("info: generating HTML")
        generateSingleHTML()

    else:
        print("eror: no action specified")
