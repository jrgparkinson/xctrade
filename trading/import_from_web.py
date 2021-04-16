"""
Utilites for scraping data from the web
"""
import re
import logging
import urllib.request
from datetime import timedelta
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)


def lookup_po10(name, _):

    names = name.split(" ")
    if not names:
        return ""

    firstname = names[0]
    lastname = names[1]

    results = []

    po10url = (
        "https://thepowerof10.info/athletes/athleteslookup.aspx?surname="
        + lastname
        + "&firstname="
        + firstname
    )

    try:

        with urllib.request.urlopen(po10url) as response:
            html = response.read()

        # page = urllib2.urlopen(po10url)
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", attrs={"id": "cphBody_dgAthletes"})

        if table:
            rows = table.find_all("tr")

            for row in rows:
                cols = row.find_all("td")
                for col in cols:
                    if col.text.strip() == "Show":
                        a = col.find("a", href=True)
                        url = a["href"]

                        if "runbritain" in url:
                            continue

                        results.append({"url": url})
                        # LOGGER.debug(url)

    except Exception as error:
        LOGGER.debug("An exception was thrown accessing " + po10url + "!")
        LOGGER.debug(str(error))
        return ""

    LOGGER.debug(results)
    if len(results) == 1:
        return "https://www.thepowerof10.info/athletes/" + results[0]["url"]

    return ""


class ParsedResult:
    pos: int
    name: str
    time: timedelta

    def __init__(self, pos, name, time):
        self.pos = pos
        self.name = name
        self.time = time

    def __str__(self):
        return "{}|{}|{}".format(self.pos, self.name, self.time)

    def __repr__(self):
        return "<ParsedResult: {}|{}|{}>".format(self.pos, self.name, self.time)

    @staticmethod
    def str_to_timedelta(string):

        hours = 0
        millis = 0
        minutes = 0
        seconds = 0

        # Match mm:ss
        m = re.match(r"^(\d+):(\d+)$", string)

        if m:
            minutes = int(m.groups()[0])
            seconds = int(m.groups()[1])
        else:
            # match mm:ss.tenths
            m = re.match(r"^(\d+):(\d+)\.(\d+)$", string)

            if m:
                minutes = int(m.groups()[0])
                seconds = int(m.groups()[1])
                millis = int(m.groups()[2]) * 100
            else:
                # match hh:mm:ss.
                m = re.match(r"^(\d+):(\d+):(\d+)$", string)
                if m:
                    hours = int(m.groups()[0])
                    minutes = int(m.groups()[1])
                    seconds = int(m.groups()[2])

        # LOGGER.debug("{}, {}, {}, {}".format(hours, minutes, seconds, millis))
        td = timedelta(
            hours=hours, minutes=minutes, seconds=seconds, milliseconds=millis
        )

        return td


def load_opentrack_results(_):
    pass


def load_po10_results_page(url):
    results = []
    with urllib.request.urlopen(url) as response:
        html = response.read()

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", attrs={"id": "cphBody_dgP"})

        if table:
            rows = table.find_all("tr")

            for row in rows:
                bg_color = ""

                try:

                    style = row.get("style")
                    bgcol = row.get("bgcolor")

                    if style:
                        LOGGER.debug("Get bg color from {}".format(row["style"]))
                        m = re.match(r"background-color:([a-zA-Z]+)", row["style"])
                        bg_color = m.groups()[0]

                    elif bgcol:
                        LOGGER.debug("Get bg color from {}".format(row["bgcolor"]))
                        bg_color = row["bgcolor"]

                except Exception as error:
                    LOGGER.debug("error parsing row: " + str(row))
                    LOGGER.debug(error)
                    continue

                if not ("WhiteSmoke" in bg_color or "Gainsboro" in bg_color):
                    continue

                cols = row.find_all("td")

                # LOGGER.debug(cols)

                pos = cols[0].text.strip()
                time = cols[2].text.strip()
                name = cols[3].text.strip()

                res = ParsedResult(
                    pos=pos, name=name, time=ParsedResult.str_to_timedelta(time)
                )
                results.append(res)

    # LOGGER.debug(results)
    return results


def load_po10_results(url):
    results = []
    with urllib.request.urlopen(url) as response:
        html = response.read()

        soup = BeautifulSoup(html, "html.parser")

        # table = soup.find('table', attrs={'id': 'cphBody_dgP'})
        pages = soup.find("span", attrs={"id": "cphBody_lblTopPageLinks"})
        links = pages.find_all("a")

        # Load first page
        results.extend(load_po10_results_page(url))

        for link in links:
            # LOGGER.debug(link)
            page_url = "https://www.thepowerof10.info" + link["href"]
            page_url = page_url.replace(" ", "%20")
            LOGGER.debug(page_url)
            results.extend(load_po10_results_page(page_url))

    LOGGER.debug(results)
    return results
