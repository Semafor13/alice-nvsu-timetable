from bs4 import BeautifulSoup
import requests
import datetime

base_url = 'http://timetable.nvsu.ru/tm/index.php/timetable/show_timetable/'
group_number = "8277"
subgroup = "0"


def get_timetable(date):
    r = requests.get(f"{base_url}group/{group_number}//{subgroup}/?date={date}")
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.find(id="timetable")


# Очищает текст от символов \t, \r, \n и пробелов
def clear_text(text: str) -> str:
    cleared_text = text.replace("\t", "")
    cleared_text = cleared_text.replace("\r", "")
    cleared_text = cleared_text.replace("\n", " ")
    cleared_text = cleared_text.strip()

    return cleared_text


def get_day(tt: BeautifulSoup, d: int) -> list[BeautifulSoup]:
    heads: list[BeautifulSoup] = tt.findAll("thead")

    dates = []

    for h in heads:

        if h.find(class_="empty-day"):
            continue

        day_in_week = int(clear_text(h.find_all("div")[-1].get_text()).split(" ")[1])

        dates.append(day_in_week)

    if d in dates:
        index_of_day_tr = dates.index(d)

        return tt.findAll("tbody")[index_of_day_tr].find_all("tr")


# Получает все данные из одной строчки расписания (с одной пары)
def get_data_from_tr(tr: BeautifulSoup):
    tds: list[BeautifulSoup] = tr.find_all("td")

    indexer = 0

    class_subgroup = None

    if len(tds) == 7:
        indexer = 1

        if tds[2].get_text():
            class_subgroup = clear_text(tds[2].get_text())

    time_of_class = tds[1].find("div").get_text()
    number_of_class = tds[1].find("small").get_text()

    subject_data = clear_text(tds[2 + indexer].get_text()).split("-")

    subject_type = subject_data[0].strip()
    subject_name = subject_data[1].strip()

    teacher = clear_text(tds[3 + indexer].find(class_="teacher").get_text()).split("(")[0].strip()

    groups = clear_text(tds[4 + indexer].find("div").get_text()).split(", ")

    auditory = clear_text(tds[5 + indexer].find("a").get_text())

    return time_of_class, number_of_class, class_subgroup, subject_type, subject_name, teacher, groups, auditory


def get_all_classes(tt: BeautifulSoup, d: int) -> list | None:
    day = get_day(tt, d)

    if day is None:
        return None

    classes = []

    for tr in day:
        classes.append(get_data_from_tr(tr))

    return classes


def get_today_classes():
    day = datetime.datetime.now().day
    month = datetime.datetime.now()
    year = datetime.datetime.now().year

    timetable: BeautifulSoup = get_timetable(f"{day}_{month}_{year}")
    return get_all_classes(timetable, day)


def get_tomorrow_classes():
    day = datetime.datetime.now().day + 1
    month = datetime.datetime.now()
    year = datetime.datetime.now().year

    timetable: BeautifulSoup = get_timetable(f"{day}_{month}_{year}")
    return get_all_classes(timetable, day)


def get_yesterday_classes():
    day = datetime.datetime.now().day - 1
    month = datetime.datetime.now()
    year = datetime.datetime.now().year

    timetable: BeautifulSoup = get_timetable(f"{day}_{month}_{year}")

    data = get_all_classes(timetable, day)

    print(data)


def get_my_date_classes(
        day=str(datetime.datetime.now().day),
        month=str(datetime.datetime.now().month),
        year=str(datetime.datetime.now().year)
):
    timetable: BeautifulSoup = get_timetable(f"{day}_{month}_{year}")
    return get_all_classes(timetable, datetime.datetime.now().day)


def beautify(info):
    if info is None:
        return "На этот день у вас нет пар"

    all_strs = []
    for i in info:
        all_strs.append(f"С {i[0].split(" ")[0]} по {i[0].split(" ")[1]} пара {i[4]} У {i[5]}")

    full_string = "\n".join(all_strs)

    return full_string


a = beautify(get_today_classes())

print(a)
