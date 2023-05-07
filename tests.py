import re

#
# bg_months = {
#         "януари": "01",
#         "февруари": "02",
#         "март": "03",
#         "април": "04",
#         "май": "05",
#         "юни": "06",
#         "юли": "07",
#         "август": "08",
#         "септември": "09",
#         "октомври": "10",
#         "ноември": "11",
#         "декември": "12",
#     }
#
# # article_datetime = "04 МАЙ 2023  17:38"
# #
# article_datetime = "13:14 ч. 04.05.2023 г."
# print(article_datetime)
# string_for_replace = []
# new_datetime = None
# for x in article_datetime.split(" "):
#     if x.lower() in bg_months.keys():
#         replacement = bg_months[x.lower()]
#         new_datetime = article_datetime.replace(x, replacement)
#         break
#
# print(article_datetime.isascii())
# print(article_datetime.isalnum())
# # y = "04 май 2023  17:38"
# # print(y.replace("май", "05"))
#
# x = [ch for ch in article_datetime.lower() if re.search('[а-яА-Я]', ch)]
#
# print(x)
#

class BaseWebsite:
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

article_datetime_lst = ["""
        10:35, 06.05.2023
                    (обновена)
            """,  # bnt
                    "13:14 ч. 04.05.2023 г.",  # btv
                    "04 май 2023  09:13"  # nova

                    ]

for article_datetime in article_datetime_lst:
    if len([ch for ch in article_datetime.lower() if re.search('[а-яА-Я]', ch)]) > 2:

        for x in article_datetime.split(" "):
            if x.lower() in BaseWebsite.bg_months.keys():
                replacement = BaseWebsite.bg_months[x.lower()]
                article_datetime = article_datetime.replace(x, replacement)
                print(article_datetime, "<< with month")
                # article_datetime = article_datetime.replace(" ", ":", 2)
                article_datetime = article_datetime.replace("  ", "-")
                article_datetime = article_datetime.replace(" ", ":")
                article_datetime = article_datetime.replace("-", " ")
                print(article_datetime, "<< without month")

    lst = [re.sub('[^\d]', " ", x).strip() for x in article_datetime.split(" ")]
    new_dt = [x for x in lst if x]
    print(new_dt)
    final_article_datetime = []
    for element in new_dt:
        if len(element) == 5:
            time = element.replace(" ", ":")
            final_article_datetime.append(time)
        else:
            date = element.replace(" ", "-")
            final_article_datetime.append(date)
    if len(final_article_datetime[0]) < len(final_article_datetime[1]):
        final_article_datetime[0], final_article_datetime[1] = final_article_datetime[1], final_article_datetime[0]

    print(", ".join(x for x in final_article_datetime))

