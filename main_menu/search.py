import customtkinter as ctk
import pickle
import pandas as pd
import os
from datetime import datetime
from CTkMessagebox import CTkMessagebox
from tkcalendar import Calendar
import tkinter as tk

try: from read import read_recipe, format_number, read_font, read_code
except: from main_menu.read import read_recipe, format_number, read_font, read_code

def search():
    with open("config.pickle", "rb") as fr:
        config = pickle.load(fr)

    history_path = config["내역 경로"] + "/history"
    if not os.path.exists(history_path):
        os.makedirs(history_path)
    history_path += "history.csv"
    try: history = pd.read_csv(history_path)
    except: history = pd.DataFrame({"제조 일자":[],
                                "제조 완료 시각":[],
                                "작업자(지시자/칭량자/배합자)":[],
                                "배합 가마":[],
                                "제품명":[],
                                "작업량(g)":[],
                                "PH":[]})
    
    recipes = read_recipe(config["BOM 경로"])
    ingredient_dict = {}
    buyer_dict = {}
    code_dict = read_code(config["BOM 경로"])

    for name in recipes.keys():
        recipe = recipes[name]

        ingredients = [i[0] for i in recipe["칭량"]]
        for ingredient in ingredients:
            if ingredient in ingredient_dict.keys():ingredient_dict[ingredient].append(name)
            else: ingredient_dict[ingredient] = [name]

        buyer = recipe["기타 정보"][0].split(":")[1]
        if buyer in buyer_dict: buyer_dict[buyer].append(name)
        else: buyer_dict[buyer] = [name]

    window = ctk.CTk()
    window.title("내역 검색")
    window.geometry("750x1000+0+0")

    search_frame = ctk.CTkFrame(window, width = 730, height = 300)
    search_frame.grid(column = 0, row = 0, pady = 2, padx= 10)

    # =====================
    calendars_frame = ctk.CTkFrame(window, width = 730, height = 300)
    calendars_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    # =====================

    # 시작 날짜 달력
    calendar_frame_from = tk.Frame(calendars_frame, width = 345)
    calendar_frame_from.grid(column=0, row=0, padx=10)

    cal_from = Calendar(calendar_frame_from, selectmode='day', date_pattern='yyyy-mm-dd', locale='ko_KR')
    cal_from.pack()

    def get_date_from():
        selected_date = cal_from.get_date()
        date_label_from.configure(text=f"검색 시작 일자: {selected_date}")

    select_btn_from = ctk.CTkButton(window, text="시작 날짜 선택", command=get_date_from)
    select_btn_from.grid(column=0, row=1)

    date_label_from = ctk.CTkLabel(window, text="")
    date_label_from.grid(column=0, row=2)

    # 종료 날짜 달력
    calendar_frame_to = tk.Frame(calendars_frame, width = 345)
    calendar_frame_to.grid(column=1, row=0, padx=10)

    cal_to = Calendar(calendar_frame_to, selectmode='day', date_pattern='yyyy-mm-dd', locale='ko_KR')
    cal_to.pack()

    def get_date_to():
        selected_date = cal_to.get_date()  # 🔧 cal_to._to() → get_date()
        date_label_to.configure(text=f"검색 종료 일자: {selected_date}")

    select_btn_to = ctk.CTkButton(window, text="종료 날짜 선택", command=get_date_to)
    select_btn_to.grid(column=1, row=1)

    date_label_to = ctk.CTkLabel(window, text="")
    date_label_to.grid(column=1, row=2)

    window.mainloop()

if __name__ == "__main__":
    search()