from bs4 import BeautifulSoup

from utils import (
    HTML_OUTPUT_PATH,
    JSON_OUTPUT_PATH,
    getBaseURL,
    getHTMLContent,
    logger,
    readDataJSON,
    storeDataJSON,
)


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
    if interfaceList is None:
        raise ValueError(f"Could not find interface-list container for {interfaceType}")

    h2_tag = interfaceList.find("h2")
    if h2_tag is None:
        raise ValueError("Could not find h2 heading under interface list")
    interfaceHeading = h2_tag.text.strip()

    main_section = interfaceList.find("div", class_="mainSection")
    if main_section is None:
        raise ValueError("Could not find mainSection under interface list")
    interfaceDescription = main_section.get_text(separator=" ").strip()

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
            desc_tag = div.find("div", class_="html-description")
            description = desc_tag.get_text(separator=" ").strip() if desc_tag else ""

            newData = {
                "heading": heading,
                "description": description,
                "specLink": specLink,
            }

            pageResults.append(newData)

        except Exception as e:
            logger.error(f"Failed parsing API interface {h3.text.strip()}: {e}")
            continue

    return {
        "interfaceHeading": interfaceHeading,
        "interfaceDescription": interfaceDescription,
        "interfaceLink": url,
        "list": pageResults,
    }


def generateHTML() -> None:
    logger.info(f"Reading parsed data from {JSON_OUTPUT_PATH}")
    savedData = readDataJSON(JSON_OUTPUT_PATH)

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

    logger.info(f"Generating HTML report at {HTML_OUTPUT_PATH}")
    HTML_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HTML_OUTPUT_PATH.open("w") as f:
        f.write(html)


def beginParse() -> None:
    allResults = []
    interfaceTypes = getAllInterfaceTypes()

    logger.info("Begin parsing Epic API sections")
    for interfaceType in interfaceTypes:
        logger.info(f"Parsing data for interface type: {interfaceType}")
        try:
            allResults.append(parseAPISection(interfaceType))
        except Exception as e:
            logger.error(f"Error parsing interface type {interfaceType}: {e}")

    logger.info(f"Writing parsed results as JSON to {JSON_OUTPUT_PATH}")
    storeDataJSON(allResults, JSON_OUTPUT_PATH)
