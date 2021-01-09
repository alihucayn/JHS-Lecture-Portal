import string
import random

# gnerating list of choices
# def generateChoicesList(of, model, campus=None, grade=None):
#     list=[]
#     if of=="campus":
#         for entry in model.query:
#             if entry.campus not in list:
#                 list.append((entry.value, entry.value))
#         return list
#     elif of=="class":
#         for entry in model.query.filter_by(campus=campus):
#             value=getattr(entry, of)
#             if value not in list:
#                 list.append((value, value))
#         return list
#     elif of=="section":
#         for entry in model.query.filter(_or,campus=campus, grade=grade):
#             value=getattr(entry, of)
#             if value not in list:
#                 list.append((value, value))
#         return list

def generateChoicesList(of, model, empty_insert=True):
    list=[]
    for entry in model.query:
        value=getattr(entry, of)
        if (value, value) not in list:
            list.append((value, value))
    if empty_insert:
        list.insert(0,("",of.capitalize()))
    return list


def username_generator(form):
    return form.name.data.replace(" ", "-").lower()+"-"+form.grade.data.lower()


def private_id_generator(length=12):
    return ''.join( random.choice(string.ascii_letters) for i in range(length) )
