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
        "    <style>",
        "        :root {",
        "            --bg-color: #f8fafc;",
        "            --card-bg: #ffffff;",
        "            --text-primary: #1e293b;",
        "            --text-secondary: #475569;",
        "            --text-muted: #64748b;",
        "            --link-color: #2563eb;",
        "            --link-hover: #1d4ed8;",
        "            --border-color: #e2e8f0;",
        "            --shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1);",
        "            --font-family: -apple-system, BlinkMacSystemFont, "
        '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;',
        "        }",
        "        @media (prefers-color-scheme: dark) {",
        "            :root {",
        "                --bg-color: #0f172a;",
        "                --card-bg: #1e293b;",
        "                --text-primary: #f8fafc;",
        "                --text-secondary: #cbd5e1;",
        "                --text-muted: #94a3b8;",
        "                --link-color: #38bdf8;",
        "                --link-hover: #7dd3fc;",
        "                --border-color: #334155;",
        "                --shadow: 0 1px 3px rgba(0,0,0,0.2);",
        "            }",
        "        }",
        "        * {",
        "            box-sizing: border-box;",
        "        }",
        "        html {",
        "            scroll-behavior: smooth;",
        "            scroll-padding-top: 180px;",
        "        }",
        "        body {",
        "            font-family: var(--font-family);",
        "            line-height: 1.6;",
        "            color: var(--text-secondary);",
        "            background-color: var(--bg-color);",
        "            margin: 0;",
        "            padding: 2rem 1rem;",
        "        }",
        "        .container {",
        "            max-width: 900px;",
        "            margin: 0 auto;",
        "        }",
        "        header {",
        "            margin-bottom: 2rem;",
        "            border-bottom: 1px solid var(--border-color);",
        "            padding-bottom: 1rem;",
        "        }",
        "        h1 {",
        "            color: var(--text-primary);",
        "            font-size: 2.25rem;",
        "            margin: 0 0 0.5rem 0;",
        "            font-weight: 800;",
        "            letter-spacing: -0.025em;",
        "        }",
        "        .subtitle {",
        "            color: var(--text-muted);",
        "            font-size: 1.125rem;",
        "            margin: 0;",
        "        }",
        "        .sticky-bar {",
        "            position: sticky;",
        "            top: 0;",
        "            background-color: rgba(248, 250, 252, 0.9);",
        "            backdrop-filter: blur(8px);",
        "            -webkit-backdrop-filter: blur(8px);",
        "            padding: 1rem 0;",
        "            z-index: 100;",
        "            margin-bottom: 2rem;",
        "        }",
        "        @media (prefers-color-scheme: dark) {",
        "            .sticky-bar {",
        "                background-color: rgba(15, 23, 42, 0.9);",
        "            }",
        "        }",
        "        .search-container {",
        "            margin-bottom: 1rem;",
        "        }",
        "        #search-input {",
        "            width: 100%;",
        "            padding: 0.75rem 1rem;",
        "            font-size: 1rem;",
        "            border: 1px solid var(--border-color);",
        "            border-radius: 8px;",
        "            background-color: var(--card-bg);",
        "            color: var(--text-primary);",
        "            outline: none;",
        "            transition: border-color 0.2s, box-shadow 0.2s;",
        "        }",
        "        #search-input:focus {",
        "            border-color: var(--link-color);",
        "            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);",
        "        }",
        "        @media (prefers-color-scheme: dark) {",
        "            #search-input:focus {",
        "                box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);",
        "            }",
        "        }",
        "        .nav-bar {",
        "            display: flex;",
        "            flex-wrap: wrap;",
        "            gap: 0.5rem;",
        "        }",
        "        .nav-link {",
        "            display: inline-flex;",
        "            align-items: center;",
        "            padding: 0.35rem 0.75rem;",
        "            font-size: 0.875rem;",
        "            border-radius: 6px;",
        "            background: var(--card-bg);",
        "            border: 1px solid var(--border-color);",
        "            color: var(--text-secondary);",
        "            text-decoration: none;",
        "            transition: all 0.2s;",
        "        }",
        "        .nav-link:hover {",
        "            background: var(--link-color);",
        "            color: #ffffff;",
        "            border-color: var(--link-color);",
        "            text-decoration: none;",
        "        }",
        "        .nav-count {",
        "            font-size: 0.75rem;",
        "            background-color: var(--bg-color);",
        "            color: var(--text-muted);",
        "            padding: 0.1rem 0.4rem;",
        "            border-radius: 999px;",
        "            margin-left: 0.375rem;",
        "            display: inline-block;",
        "            transition: all 0.2s;",
        "        }",
        "        .nav-link:hover .nav-count {",
        "            background-color: rgba(255, 255, 255, 0.25);",
        "            color: #ffffff;",
        "        }",
        "        .interface-section {",
        "            background: var(--card-bg);",
        "            border: 1px solid var(--border-color);",
        "            border-radius: 12px;",
        "            padding: 2rem;",
        "            margin-bottom: 2rem;",
        "            box-shadow: var(--shadow);",
        "            transition: padding-bottom 0.2s;",
        "        }",
        "        .interface-section.collapsed {",
        "            padding-bottom: 1.5rem;",
        "        }",
        "        .interface-section.collapsed .interface-header {",
        "            margin-bottom: 0;",
        "        }",
        "        .interface-header {",
        "            margin-top: 0;",
        "            margin-bottom: 1rem;",
        "            display: flex;",
        "            align-items: center;",
        "            justify-content: space-between;",
        "            flex-wrap: wrap;",
        "            gap: 0.5rem;",
        "            cursor: pointer;",
        "            user-select: none;",
        "        }",
        "        .interface-title {",
        "            font-size: 1.5rem;",
        "            font-weight: 700;",
        "            margin: 0;",
        "        }",
        "        .interface-title a {",
        "            color: var(--text-primary);",
        "            text-decoration: none;",
        "        }",
        "        .interface-title a:hover {",
        "            color: var(--link-color);",
        "        }",
        "        .interface-header-actions {",
        "            display: flex;",
        "            align-items: center;",
        "            gap: 0.75rem;",
        "        }",
        "        .title-count {",
        "            font-size: 0.8125rem;",
        "            font-weight: 500;",
        "            color: var(--text-muted);",
        "            background-color: var(--bg-color);",
        "            padding: 0.25rem 0.625rem;",
        "            border-radius: 999px;",
        "            border: 1px solid var(--border-color);",
        "        }",
        "        .toggle-btn {",
        "            background: none;",
        "            border: 1px solid var(--border-color);",
        "            border-radius: 6px;",
        "            color: var(--text-secondary);",
        "            cursor: pointer;",
        "            padding: 0.25rem;",
        "            display: inline-flex;",
        "            align-items: center;",
        "            justify-content: center;",
        "            transition: all 0.2s;",
        "        }",
        "        .toggle-btn:hover {",
        "            background-color: var(--border-color);",
        "            color: var(--text-primary);",
        "        }",
        "        .chevron {",
        "            transition: transform 0.2s;",
        "            transform: rotate(0deg);",
        "        }",
        "        .interface-section.collapsed .chevron {",
        "            transform: rotate(-90deg);",
        "        }",
        "        .interface-content {",
        "            transition: max-height 0.3s ease-out, opacity 0.3s ease-out;",
        "            max-height: 10000px;",
        "            opacity: 1;",
        "            overflow: hidden;",
        "        }",
        "        .interface-section.collapsed .interface-content {",
        "            max-height: 0;",
        "            opacity: 0;",
        "            pointer-events: none;",
        "        }",
        "        .interface-desc {",
        "            color: var(--text-secondary);",
        "            font-size: 1rem;",
        "            margin-bottom: 1.5rem;",
        "        }",
        "        .api-list {",
        "            list-style: none;",
        "            padding: 0;",
        "            margin: 0;",
        "            display: grid;",
        "            gap: 1.25rem;",
        "        }",
        "        .api-item {",
        "            border-top: 1px solid var(--border-color);",
        "            padding-top: 1.25rem;",
        "        }",
        "        .api-item:first-child {",
        "            border-top: none;",
        "            padding-top: 0;",
        "        }",
        "        .api-name {",
        "            font-weight: 600;",
        "            color: var(--text-primary);",
        "            margin-bottom: 0.25rem;",
        "            font-size: 1.05rem;",
        "        }",
        "        .api-name a {",
        "            color: var(--link-color);",
        "            text-decoration: none;",
        "        }",
        "        .api-name a:hover {",
        "            text-decoration: underline;",
        "        }",
        "        .api-desc {",
        "            font-size: 0.95rem;",
        "            color: var(--text-secondary);",
        "            margin: 0;",
        "        }",
        "        footer {",
        "            text-align: center;",
        "            margin-top: 4rem;",
        "            padding-top: 2rem;",
        "            border-top: 1px solid var(--border-color);",
        "            color: var(--text-muted);",
        "            font-size: 0.875rem;",
        "        }",
        "    </style>",
        "</head>",
        "<body>",
        "    <div class='container'>",
        "        <header>",
        "            <h1>Epic Open API Specifications</h1>",
        "            <p class='subtitle'>Scraped interface list and specifications from https://open.epic.com/Interface/</p>",
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
    html_parts.append("            <p>Generated automatically by Epic Open API Scraper</p>")
    html_parts.append("        </footer>")
    html_parts.append("    </div>")

    html_parts.append("    <script>")
    html_parts.append("        document.addEventListener('DOMContentLoaded', () => {")
    html_parts.append("            const searchInput = document.getElementById('search-input');")
    html_parts.append("            const sections = document.querySelectorAll('.interface-section');")
    html_parts.append("")
    html_parts.append("            // Toggle collapse/expand on header click")
    html_parts.append("            document.querySelectorAll('.interface-header').forEach(header => {")
    html_parts.append("                header.addEventListener('click', (e) => {")
    html_parts.append("                    if (e.target.closest('a')) return;")
    html_parts.append("                    const section = header.closest('.interface-section');")
    html_parts.append("                    section.classList.toggle('collapsed');")
    html_parts.append("                });")
    html_parts.append("            });")
    html_parts.append("")
    html_parts.append("            // Real-time search filter")
    html_parts.append("            searchInput.addEventListener('input', (e) => {")
    html_parts.append("                const query = e.target.value.toLowerCase().trim();")
    html_parts.append("")
    html_parts.append("                sections.forEach(section => {")
    html_parts.append("                    let visibleCount = 0;")
    html_parts.append("                    const items = section.querySelectorAll('.api-item');")
    html_parts.append("")
    html_parts.append("                    items.forEach(item => {")
    html_parts.append("                        const name = item.querySelector('.api-name').textContent.toLowerCase();")
    html_parts.append("                        const desc = item.querySelector('.api-desc').textContent.toLowerCase();")
    html_parts.append("")
    html_parts.append("                        if (name.includes(query) || desc.includes(query)) {")
    html_parts.append("                            item.style.display = '';")
    html_parts.append("                            visibleCount++;")
    html_parts.append("                        } else {")
    html_parts.append("                            item.style.display = 'none';")
    html_parts.append("                        }")
    html_parts.append("                    });")
    html_parts.append("")
    html_parts.append("                    if (visibleCount > 0 || query === '') {")
    html_parts.append("                        section.style.display = '';")
    html_parts.append("                        if (query !== '') {")
    html_parts.append("                            section.classList.remove('collapsed');")
    html_parts.append("                        }")
    html_parts.append("                    } else {")
    html_parts.append("                        section.style.display = 'none';")
    html_parts.append("                    }")
    html_parts.append("                });")
    html_parts.append("            });")
    html_parts.append("        });")
    html_parts.append("    </script>")
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
