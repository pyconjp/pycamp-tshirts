import time
from urllib import request

from bs4 import BeautifulSoup


def get_staff_list(url: str):
    """
    get pycamp staff and ta list from connpass page

    [("name1", "ta"), ("name2", "staff"), ...]
    """
    with request.urlopen(url + "participation") as f:
        html = f.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

    staff_list = []
    for div in soup.select("div.participation_table_area"):
        ptype = div.find("span", class_="label_ptype_name").text
        if "TA" in ptype or "現地スタッフ" in ptype:
            if "TA" in ptype:
                kind = "ta"
            else:
                kind = "staff"

            for user in div.select("p.display_name"):
                try:
                    name = user.a["href"].split("/")[-2]
                    staff_list.append((name, kind))
                except TypeError:
                    pass

    return staff_list


def get_event_list() -> list[tuple[str, str]]:
    """
    get pycamp event name and url list

    [("name1", "url1"), ("name2", "url2"), ...]
    """
    url = "https://www.pycon.jp/support/bootcamp.html"
    with request.urlopen(url) as f:
        html = f.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

    # get title
    a_tag = soup.find("a", string="開催実績", class_="toc-backref")
    section = a_tag.parent.parent

    event_list = []
    for atag in section.select("a.external"):
        link = atag["href"]
        # skip not connpass link
        if "connpass" not in link:
            continue
        # skip canceled event
        if "中止" in atag.parent.text:
            continue

        place = atag.text.removeprefix("Python Boot Camp in ")
        event_list.append((place, link))

    return event_list


def main():
    event_list = get_event_list()

    for name, url in event_list:
        staff_list = get_staff_list(url)
        for staff_name, kind in staff_list:
            print(f"{name}\t{url}\t{staff_name}\t{kind}")
        time.sleep(1)


if __name__ == '__main__':
    main()
