import csv 
import os 
from datetime import datetime


null_count = 0
date_count = 0
date_count1 = 0
folder_path = f"{str(os.curdir)}/data/incoming"
csv_list = list(os.listdir(folder_path))
for csv_file in csv_list:
    print(csv_file)
    with open(f"{folder_path}/{csv_file}", "r") as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            print(row)
            for column, value in row.items():
                if value is None or value.strip() == "":
                    null_count+=1
            for sana, val in row.items():
                if val is not None:
                    try:
                        datetime.strptime(val.strip(), "%d.%m.%Y")
                        date_count += 1
                    except ValueError:
                        pass
            for sana1, val1 in row.items():
                if val1 is not None:
                    try:
                        datetime.strptime(val1.strip(), "%Y-%m-%d")
                        date_count1 += 1
                    except ValueError:
                        pass
print(f"null lar soni: {null_count}")
print(f"%d.%m.%Y shunaqa formatlilar soni: {date_count}")
print(f"%Y-%m-%d shunaqa formatlilar soni: {date_count1}")

# folder = f"{str(os.curdir)}/data/incoming"
# csv_list = list(os.listdir(folder))
# for csv_file in csv_list:
#     print(csv_file)
#     with open(f"{folder}/{csv_file}",'r') as file:
#         reader = csv.DictReader(file,delimiter=';')
#         for row in reader:
#             print(row)

