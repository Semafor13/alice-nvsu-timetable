from bs4 import BeautifulSoup
import requests
import datetime

base_url = 'http://timetable.nvsu.ru/tm/index.php/timetable/show_timetable/'
group_number = "8277"
subgroup = "0"


def get_current_date():
    day = datetime.datetime.now().day
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    return f"{day}_{month}_{year}"


def get_tomorrow_date():
    day = datetime.datetime.now().day + 1
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    return f"{day}_{month}_{year}"


date = "22_04_2024"

r = requests.get(f"{base_url}group/{group_number}//{subgroup}/?date={date}")
soup = BeautifulSoup(r.text, "html.parser")
timetable: BeautifulSoup = soup.find(id="timetable")


# Очищает текст от символов \t, \r, \n и пробелов
def clear_text(text: str) -> str:
    cleared_text = text.replace("\t", "")
    cleared_text = cleared_text.replace("\r", "")
    cleared_text = cleared_text.replace("\n", " ")
    cleared_text = cleared_text.strip()

    return cleared_text


def get_day(tt: BeautifulSoup, d: int) -> list[BeautifulSoup]:
    heads: list[BeautifulSoup] = tt.findAll("thead")

    dates = [int(clear_text(h.find("div").get_text()).split(" ")[1]) for h in heads]

    if d in dates:
        index_of_day_tr = dates.index(d)

        return tt.findAll("tbody")[index_of_day_tr].find_all("tr")


# Получает все данные из одной строчки расписания (с одной пары)
def get_data_from_tr(tr: BeautifulSoup):
    tds: list[BeautifulSoup] = tr.find_all("td")

    pg_indexer = 0

    if len(tds) == 7:
        pg_indexer = 1

    number_of_exercise = tds[1].find("small").get_text()

    subject_data = clear_text(tds[2 + pg_indexer].get_text()).split("-")

    subject_type = subject_data[0].strip()
    subject_name = subject_data[1].strip()

    teacher = clear_text(tds[3 + pg_indexer].find(class_="teacher").get_text()).split("(")[0].strip()

    groups = clear_text(tds[4 + pg_indexer].find("div").get_text()).split(", ")

    auditory = clear_text(tds[5 + pg_indexer].find("a").get_text())

    return number_of_exercise, subject_type, subject_name, teacher, groups, auditory


def get_all_classes(tt: BeautifulSoup, d: int) -> list:
    classes = []

    for tr in get_day(tt, d):
        classes.append(get_data_from_tr(tr))

    return classes


print(get_all_classes(timetable, int(date.split("_")[0])))
