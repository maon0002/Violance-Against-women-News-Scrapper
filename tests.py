# import re
#
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
#
# class BaseWebsite:
#     bg_months = {
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
# article_datetime_lst = ["""
#         10:35, 06.05.2023
#                     (обновена)
#             """,  # bnt
#                     "13:14 ч. 04.05.2023 г.",  # btv
#                     "04 май 2023  09:13"  # nova
#
#                     ]
#
# for article_datetime in article_datetime_lst:
#     if len([ch for ch in article_datetime.lower() if re.search('[а-яА-Я]', ch)]) > 2:
#
#         for x in article_datetime.split(" "):
#             if x.lower() in BaseWebsite.bg_months.keys():
#                 replacement = BaseWebsite.bg_months[x.lower()]
#                 article_datetime = article_datetime.replace(x, replacement)
#                 print(article_datetime, "<< with month")
#                 # article_datetime = article_datetime.replace(" ", ":", 2)
#                 article_datetime = article_datetime.replace("  ", "-")
#                 article_datetime = article_datetime.replace(" ", ":")
#                 article_datetime = article_datetime.replace("-", " ")
#                 print(article_datetime, "<< without month")
#
#     lst = [re.sub('[^\d]', " ", x).strip() for x in article_datetime.split(" ")]
#     new_dt = [x for x in lst if x]
#     print(new_dt)
#     final_article_datetime = []
#     for element in new_dt:
#         if len(element) == 5:
#             time = element.replace(" ", ":")
#             final_article_datetime.append(time)
#         else:
#             date = element.replace(" ", "-")
#             final_article_datetime.append(date)
#     if len(final_article_datetime[0]) < len(final_article_datetime[1]):
#         final_article_datetime[0], final_article_datetime[1] = final_article_datetime[1], final_article_datetime[0]
#
#     print(", ".join(x for x in final_article_datetime))
#
# def is_leap(year):
#     leap = False
#
#
#     # Write your logic here
#     if year % 4 == 0:
#         if year % 100 == 0:
#             if year % 400 == 0:
#                 leap = True
#         else:
#             leap = True
#     return leap
#
#
# # year = int(input())
# year = 2500
# print(is_leap(year))
# print(1900 % 4)
# print(1900 // 4)
# print(1900 / 4)
#
# print(1900 % 100)
# print(1900 // 100)
# print(1900 / 100)

# if __name__ == '__main__':
#     n = int(input())
#     for num in range(1, n + 1):
#         print(num, end='')
#
# def count_symetric_diff_subscriptionists(first_set: set, second_set: set) -> int:
#     new_set = first_set.symmetric_difference(second_set)
#     new_set_length = len(new_set)
#     return new_set_length
#
#
# english_newspaper_subscribers = int(input())
# english_newspaper_subscribers_numbers = input().split()
# french_newspaper_subscribers = int(input())
# french_newspaper_subscribers_numbers = input().split()
#
# number_of_unique_subscribers = count_symetric_diff_subscriptionists(set(english_newspaper_subscribers_numbers),
#                                                                     set(french_newspaper_subscribers_numbers))
# print(number_of_unique_subscribers)


# def set_mutation(operation: str):
#
#     if operation == "update":
#         new_input_set = set(input().split())
#         set_values.update(new_input_set)
#     elif operation == "intersection_update":
#         new_input_set = set(input().split())
#         set_values.intersection_update(new_input_set)
#     elif operation == "difference_update":
#         new_input_set = set(input().split())
#         set_values.difference_update(new_input_set)
#     elif operation == "symmetric_difference_update":
#         new_input_set = set(input().split())
#         set_values.symmetric_difference_update(new_input_set)
#
#
# set_length = int(input())
# set_values = set(input().split())
# number_of_operations = int(input())
#
# for op in range(number_of_operations):
#     command, value = input().split()
#     set_mutation(command)
#
# new_set_length = len(set_values)
# print(sum([int(x) for x in set_values]))

#
# def set_mutation(operation: str):
#     if operation == "update":
#         new_input_set = set(input().split())
#         set_values.update(new_input_set)
#     elif operation == "intersection_update":
#         new_input_set = set(input().split())
#         set_values.intersection_update(new_input_set)
#     elif operation == "difference_update":
#         new_input_set = set(input().split())
#         set_values.difference_update(new_input_set)
#     elif operation == "symmetric_difference_update":
#         new_input_set = set(input().split())
#         set_values.symmetric_difference_update(new_input_set)
#
#
# set_length = int(input())
# set_values = set(input().split())
# number_of_operations = int(input())
#
# for op in range(number_of_operations):
#     operation, value = input().split()
#     if operation == "update":
#         new_input_set = set(input().split())
#         set_values.update(new_input_set)
#     elif operation == "intersection_update":
#         new_input_set = set(input().split())
#         set_values.intersection_update(new_input_set)
#     elif operation == "difference_update":
#         new_input_set = set(input().split())
#         set_values.difference_update(new_input_set)
#     elif operation == "symmetric_difference_update":
#         new_input_set = set(input().split())
#         set_values.symmetric_difference_update(new_input_set)
#
# new_set_length = len(set_values)
# print(sum([int(x) for x in set_values]))


group_size = int(input())
rooms_list = list(map(int, input().split()))

rooms_set = set(rooms_list)
rooms_sum = sum(rooms_list)
room_set_sum = sum(rooms_set) * group_size
captain = (room_set_sum - rooms_sum) // (group_size - 1)
print(captain)
print("rooms_set :", rooms_set)
print("rooms_sum :", rooms_sum)
print("room_set_sum :", room_set_sum)
# for room in elements_set:
#     if elements_list.count(room) != group_size:
#         print(room)
# print(sorted(elements_list, key=lambda x: elements_list.count(x)))
# print(sorted(elements_list, key=lambda x: elements_list.count(x))[0])
#
# [print(room) for room in set(elements_list) if elements_list.count(room) != group_size]
