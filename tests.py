import re

bg_months = {
        "януари": "01",
        "февруари": "02",
        "март": "03",
        "април": "04",
        "май": "05",
        "юни": "06",
        "юли": "07",
        "август": "08",
        "септември": "09",
        "октомври": "10",
        "ноември": "11",
        "декември": "12",
    }

# article_datetime = "04 МАЙ 2023  17:38"
#
article_datetime = "13:14 ч. 04.05.2023 г."
print(article_datetime)
string_for_replace = []
new_datetime = None
for x in article_datetime.split(" "):
    if x.lower() in bg_months.keys():
        replacement = bg_months[x.lower()]
        new_datetime = article_datetime.replace(x, replacement)
        break

print(article_datetime.isascii())
print(article_datetime.isalnum())
# y = "04 май 2023  17:38"
# print(y.replace("май", "05"))

x = [ch for ch in article_datetime.lower() if re.search('[а-яА-Я]', ch)]

print(x)





