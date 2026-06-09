from urllib.parse import urljoin, urlparse, urlunparse

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
    url = urljoin(getBaseURL(), f"/Interface/{interfaceType}")
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
                if specRelativeLink and specRelativeLink != "#":
                    # Join base URL and relative link safely
                    specLink = urljoin(getBaseURL(), specRelativeLink)
                    # Clean double slashes in path (except protocol separator)
                    parsed = urlparse(specLink)
                    path = parsed.path
                    while "//" in path:
                        path = path.replace("//", "/")
                    specLink = urlunparse(parsed._replace(path=path))
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

    sections_info = []
    for item in savedData:
        heading = item["interfaceHeading"]
        count = len(item["list"])
        sec_id = "".join(c for c in heading if c.isalnum() or c in ("-", "_")).lower()
        sections_info.append({"heading": heading, "count": count, "id": sec_id, "item": item})

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "    <meta charset='utf-8'>",
        "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "    <title>Epic Open API Specifications</title>",
        "    <link rel='stylesheet' href='style.css'>",
        "</head>",
        "<body>",
        "    <div class='container'>",
        "        <header>",
        "            <h1>Epic Open API Specifications</h1>",
        "            <p class='subtitle'>Scraped interface list and specifications from <a href='https://open.epic.com/Interface/'>https://open.epic.com/Interface/</a>.</p>",
        "        </header>",
    ]

    html_parts.append("        <div class='sticky-bar'>")
    html_parts.append("            <div class='search-container'>")
    html_parts.append(
        "                <input type='text' id='search-input' "
        "placeholder='Search APIs by name or description...' "
        "autofocus autocomplete='off'>"
    )
    html_parts.append("            </div>")
    html_parts.append("            <nav class='nav-bar'>")
    for info in sections_info:
        sec_id = info["id"]
        heading = info["heading"]
        count = info["count"]
        html_parts.append(
            f"                <a href='#{sec_id}' class='nav-link'>{heading}<span class='nav-count'>{count}</span></a>"
        )
    html_parts.append("            </nav>")
    html_parts.append("        </div>")

    html_parts.append("        <main>")

    for info in sections_info:
        item = info["item"]
        sec_id = info["id"]
        interface_heading = item["interfaceHeading"]
        interface_description = item["interfaceDescription"]
        interface_link = item["interfaceLink"]
        count = info["count"]

        html_parts.append(f"            <section class='interface-section' id='{sec_id}'>")
        html_parts.append("                <div class='interface-header'>")
        html_parts.append(
            "                    <h2 class='interface-title'>"
            f"<a href='{interface_link}' target='_blank' "
            f"rel='noopener noreferrer'>{interface_heading}</a>"
            "                    </h2>"
        )
        html_parts.append("                    <div class='interface-header-actions'>")
        html_parts.append(f"                        <span class='title-count'>{count} APIs</span>")
        html_parts.append("                        <button class='toggle-btn' aria-label='Toggle Section'>")
        html_parts.append(
            "                            <svg class='chevron' viewBox='0 0 24 24' width='16' height='16'>"
            "<path d='M7 10l5 5 5-5H7z' fill='currentColor'/></svg>"
        )
        html_parts.append("                        </button>")
        html_parts.append("                    </div>")
        html_parts.append("                </div>")
        html_parts.append("                <div class='interface-content'>")
        html_parts.append(f"                    <p class='interface-desc'>{interface_description}</p>")
        html_parts.append("                    <ul class='api-list'>")

        for sub_item in item["list"]:
            sub_heading = sub_item["heading"]
            sub_description = sub_item["description"]
            spec_link = sub_item["specLink"]

            html_parts.append("                    <li class='api-item'>")
            if spec_link == "#":
                html_parts.append(f"                        <div class='api-name'>{sub_heading}</div>")
            else:
                html_parts.append(
                    "                        <div class='api-name'>"
                    f"<a href='{spec_link}' target='_blank' "
                    f"rel='noopener noreferrer'>{sub_heading}</a></div>"
                )
            html_parts.append(f"                        <p class='api-desc'>{sub_description}</p>")
            html_parts.append("                    </li>")

        html_parts.append("                    </ul>")
        html_parts.append("                </div>")
        html_parts.append("            </section>")

    html_parts.append("        </main>")
    html_parts.append("        <footer>")
    html_parts.append(
        "            <p>Generated by "
        "<a href='https://github.com/zbhavyai/epic-open-api-scraper'>Epic Open API Scraper</a></p>"
    )
    html_parts.append("        </footer>")
    html_parts.append("    </div>")

    html_parts.append("    <script src='script.js'></script>")
    html_parts.append("</body>")
    html_parts.append("</html>")

    html = "\n".join(html_parts)

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
