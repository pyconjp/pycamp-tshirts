"""
Python Boot Campに2回以上貢献したスタッフの一覧表を出力する
"""

import time
from collections import Counter
from urllib import request

import requests
from bs4 import BeautifulSoup


def get_event_urls(contributor, pycamp_contributors):
    event_urls = []
    for url, staff_list in pycamp_contributors.items():
        if contributor in staff_list:
            event_urls.append(url)
    return event_urls


def create_contributor_list(twice_contributors, pycamp_contributors, pycamp_events):
    """create contributor list table"""
    event_dict = {e["url"]: e["title"] for e in pycamp_events}

    print(".. list-table::")
    print("   :header-rows: 1")
    print("")
    print("   - * 名前")
    print("     * 回数")
    print("     * 参加イベント")

    for contributor, count in twice_contributors:
        if count == 1:
            break

        name, url = contributor
        print(f"   - * `{name} <{url}>`__")
        print(f"     * {count}")

        event_urls = get_event_urls(contributor, pycamp_contributors)
        event_links = " 、 ".join(f"`{event_dict[url]} <{url}>`__" for url in event_urls)
        print(f"     * {event_links}")


def get_twice_contributors(contributors: dict[str, list]):
    """
    get two or more contributors
    """

    counter = Counter()
    for staff_list in contributors.values():
        print(staff_list)
        counter.update(staff_list)
    return counter.most_common()


def get_pycamp_contributors(pycamp_events: list[dict[str, str]]) -> dict[str, list]:
    """
    get contributors for all pycamp events

    {
      'https://pyconjp.connpass.com/event/33014/': [
        ('tanishiking', 'https://connpass.com/user/tanishiking/'),
        ('ymyzk', 'https://connpass.com/user/litesystems/')
      ],
      'https://pyconjp.connpass.com/event/34564/': [
        ('ynaruc', 'https://connpass.com/user/ynaruc/'),
        ('YoshitakeKageura', 'https://connpass.com/user/YoshitakeKageura/'),
        ('kazweda', 'https://connpass.com/user/npmyj/')
      ],
      ...
    }
    """
    pycamp_contributors = {}
    print("get pycamp contributors: ", end="", flush=True)

    for event in pycamp_events:
        print(event["title"], end=" ", flush=True)

        contributors = get_staff_list(event["url"])
        pycamp_contributors[event["url"]] = contributors
        time.sleep(1)

    return pycamp_contributors


def get_staff_list(url: str):
    """
    get pycamp staff and ta list from connpass page

    [("name1", "url1"), ("name2", "url2"), ...]
    """
    headers = {
        "User-Agent": "pycamp tshirts agens",
        "From": "https://github.com/pyconjp/pycamp-tshirts/",
    }
    r = requests.get(url + "participation", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    staff_list = []
    for div in soup.select("div.participation_table_area"):
        ptype = div.find("span", class_="label_ptype_name").text
        if "TA" in ptype or "現地スタッフ" in ptype:
            for user in div.select("p.display_name"):
                try:
                    name = user.a.text
                    url = user.a["href"]
                    staff_list.append((name, url))
                except AttributeError:
                    pass
                except TypeError:
                    pass

    return staff_list


def add_event_date(pycamp_events: list[dict[str, str]]) -> list[dict[str, str]]:
    """add pycamp date to pycamp_events"""
    print("get event date: ", end="", flush=True)
    # add event date
    for event in pycamp_events:
        print(event["title"], end=" ", flush=True)
        event_id = event["url"].split("/")[-2]
        # https://connpass.com/about/api/
        r = requests.get(f"https://connpass.com/api/v1/event/?event_id={event_id}")
        data = r.json()
        started_at = data["events"][0]["started_at"]
        start_date, _ = started_at.split("T")
        event["date"] = start_date
        time.sleep(1)
    print("")

    return pycamp_events


def get_pycamp_events() -> list[dict[str, str]]:
    """
    get list of pycamp event name and url from web page(https://www.pycon.jp/support/bootcamp.html)

    [
      {"title": "京都", "url": "https://pyconjp.connpass.com/event/33014/"},
      {"title": "愛媛", "url": "https://pyconjp.connpass.com/event/34564/"},
      ...
    ]
    """
    bootcamp_url = "https://www.pycon.jp/support/bootcamp.html"
    with request.urlopen(bootcamp_url) as f:
        html = f.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

    # get title
    a_tag = soup.find("a", string="開催実績", class_="toc-backref")
    section = a_tag.parent.parent

    pycamp_events = []
    for atag in section.select("a.external"):
        url = atag["href"]
        # skip not connpass link
        if "connpass" not in url:
            continue
        # skip canceled event
        if "中止" in atag.parent.text:
            continue

        title = atag.text.removeprefix("Python Boot Camp in ")
        pycamp_events.append({"title": title, "url": url})

    return pycamp_events


def main():
    # get list of pycamp event title and url from web page
    # pycamp_events = [
    #   {"title": "京都", "url": "https://pyconjp.connpass.com/event/33014/"},
    #   {"title": "愛媛", "url": "https://pyconjp.connpass.com/event/34564/"},
    #   ...
    # ]
    pycamp_events = get_pycamp_events()
    # print(pycamp_events)

    # pycamp_events = [
    #   {"title": "京都", "url": "https://pyconjp.connpass.com/event/33014/"},
    #   {"title": "愛媛", "url": "https://pyconjp.connpass.com/event/34564/"},
    #   ...
    # ]
    # pycamp_events = add_event_date(pycamp_events)
    # print(pycamp_events)

    # get list of pycamp contributos
    # {
    #   'https://pyconjp.connpass.com/event/33014/': [
    #     ('tanishiking', 'https://connpass.com/user/tanishiking/'),
    #     ('ymyzk', 'https://connpass.com/user/litesystems/')
    #   ],
    #   'https://pyconjp.connpass.com/event/34564/': [
    #     ('ynaruc', 'https://connpass.com/user/ynaruc/'),
    #     ('YoshitakeKageura', 'https://connpass.com/user/YoshitakeKageura/'),
    #     ('kazweda', 'https://connpass.com/user/npmyj/')
    #   ],
    #   ...
    # }
    pycamp_contributors = get_pycamp_contributors(pycamp_events)

    # get two or more contributors
    twice_contributors = get_twice_contributors(pycamp_contributors)

    # create contributor list
    create_contributor_list(twice_contributors, pycamp_contributors, pycamp_events)


if __name__ == "__main__":
    main()
