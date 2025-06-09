import customtkinter as ctk
import pickle
import pandas as pd
import os
from datetime import datetime
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import ttk

try: from read import read_recipe, format_number, read_font, read_code
except: from main_menu.read import read_recipe, format_number, read_font, read_code

def search():
    with open("config.pickle", "rb") as fr:
        config = pickle.load(fr)

    history_path = config["내역 경로"] + "history"
    if not os.path.exists(history_path):
        try:os.makedirs(history_path)
        except:
            config["내역 경로"] = ""
            history_path = config["내역 경로"] + "/history"
            os.makedirs(history_path)
    history_path += "/history.csv"
    try: history = pd.read_csv(history_path)
    except: history = pd.DataFrame({"제조 일자":[],
                                "제조 완료 시각":[],
                                "작업자(지시자/칭량자/배합자)":[],
                                "배합 가마":[],
                                "제품명":[],
                                "작업량(g)":[],
                                "PH":[]})
    history["제조 일자"] = history["제조 일자"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))

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
    window.title("내역조회")
    window.geometry("750x600+0+0")

    # ---------------- 제목 ----------------
    title_label = ctk.CTkLabel(window, text="내역조회", font=read_font(size=20))
    title_label.pack(pady=10)
    #------------------필요 함수----------------
    def on_search(as_excel=False):
        start = datetime.strptime(start_date.get(), "%Y-%m-%d")
        end = datetime.strptime(end_date.get(), "%Y-%m-%d")
        mode = search_mode.get()
        selected = division_var.get()
        if start > end:
            messagebox.showerror("오류", "시작 날짜는 종료 날짜보다 앞서야 합니다.")
        else:
            new_df = history[(history["제조 일자"] >= start) & (history["제조 일자"] <= end)]
            print(history)
            print(new_df)
            if mode == "code":
                new_df = history[(new_df["배합 가마"] == code_dict[code_combobox.get()]) | 
                                 (new_df["제품명"] == code_dict[code_combobox.get()]) |
                                 (new_df["제품명"].isin(ingredient_dict[code_dict[code_combobox.get()]])) |
                                 (new_df["제품명"].isin(buyer_dict[code_dict[code_combobox.get()]]))]
            else:
                if selected == "배합가마":new_df = new_df[new_df["배합 가마"] == name_combobox.get()]
                elif selected == "원료명":new_df = new_df[new_df["제품명"].isin(ingredient_dict[name_combobox.get()])]
                elif selected == "제품명":new_df = new_df[new_df["제품명"] == name_combobox.get()]
                elif selected == "거래처":new_df= new_df[new_df["제품명"].isin(buyer_dict[name_combobox.get()])]

            def find_buyer(x):
                for key in buyer_dict.keys():
                    if x in buyer_dict[key]: return key
            new_df["거래처명"] = new_df["제품명"].apply(lambda x: find_buyer(x))
            if selected == "배합가마":
                new_df = new_df[["배합 가마", "제조 일자", "제조 완료 시각","거래처명", "제품명", "작업량(g)"]]
            elif selected == "원료명":
                new_df["원료명"] = [name_combobox.get() for _ in range(len(new_df))]
                new_df = new_df[["원료명", "제조 일자", "제조 완료 시각","거래처명","제품명", "작업량(g)"]]
            elif selected == "제품명":
                new_df = new_df[["제품명", "제조 일자", "제조 완료 시각","배합 가마", "작업량(g)"]]
            elif selected == "거래처":
                new_df = new_df[["거래처명", "제조 일자", "제조 완료 시각","거래처명","제품명", "작업량(g)"]]

            new_df = pd.DataFrame(new_df)
            new_df_show = pd.concat([new_df.iloc[:3], new_df.iloc[-3:]]).drop_duplicates()
            
            # ✅ Treeview 내용 초기화
            tree.delete(*tree.get_children())
            tree["columns"] = list(new_df_show.columns)
            tree["show"] = "headings"

            for col in new_df_show.columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=100)

            # ✅ 새로운 데이터 삽입
            for _, row in new_df_show.iterrows():
                tree.insert("", "end", values=list(row))

            if as_excel==True:
                new_df.to_csv("result.csv", index = False, encoding='cp949')
                os.startfile("result.csv")

    # ---------------- 구분 (라디오 버튼) ----------------
    def update_combobox(*args):
        selected = division_var.get()
        if selected == "배합가마":
            code_combobox.configure(values=list(code_dict.keys()))
            name_combobox.configure(values=config["배합 가마"])
        elif selected == "원료명":
            code_combobox.configure(values=list(code_dict.keys()))
            name_combobox.configure(values=list(ingredient_dict.keys()))
        elif selected == "제품명":
            code_combobox.configure(values=list(code_dict.keys()))
            name_combobox.configure(values=list(recipes.keys()))
        elif selected == "거래처":
            code_combobox.configure(values=list(code_dict.keys()))
            name_combobox.configure(values=list(buyer_dict.keys()))
        code_combobox.set("")
        name_combobox.set("")

    division_var = ctk.StringVar()
    division_var.trace_add("write", update_combobox)  # 라디오 버튼 값이 바뀔 때 호출

    division_frame = ctk.CTkFrame(window)
    division_frame.pack(pady=10)

    division_label = ctk.CTkLabel(division_frame, text="구분", width=60)
    division_label.grid(row=0, column=0, padx=10)
    options = ["배합가마", "원료명", "제품명", "거래처"]
    for i, opt in enumerate(options):
        btn = ctk.CTkRadioButton(division_frame, text=opt, variable=division_var, value=opt)
        btn.grid(row=0, column=i+1, padx=5)

    # ---------------- 코드 / 명칭 ----------------
    search_mode = ctk.StringVar(value="name")  # 기본값: 코드

    code_frame = ctk.CTkFrame(window, width = 500)
    code_frame.pack(pady=10)

    code_label = ctk.CTkLabel(code_frame, text="코드")
    code_label.grid(row=0, column=0, padx=(10,0))

    code_combobox = ctk.CTkComboBox(code_frame, width=150, values=list(code_dict.keys()), command=on_search)
    code_combobox.grid(row=0, column=1, padx=5)

    code_radio = ctk.CTkRadioButton(code_frame, text="", variable=search_mode, value="code", width =70)
    code_radio.grid(row=0, column=2, padx=0)

    name_label = ctk.CTkLabel(code_frame, text="명칭")
    name_label.grid(row=0, column=3, padx=0)

    name_combobox = ctk.CTkComboBox(code_frame, width=150, values=list(buyer_dict.keys()), command=on_search)
    name_combobox.grid(row=0, column=4, padx=5)

    name_radio = ctk.CTkRadioButton(code_frame, text="", variable=search_mode, value="name", width =70)
    name_radio.grid(row=0, column=5, padx=0)

    # ---------------- 기준일자 선택 ----------------
    date_frame = ctk.CTkFrame(window)
    date_frame.pack(pady=20)

    standard_label = ctk.CTkLabel(date_frame, text="기준일자")
    standard_label.grid(row=0, column=0, padx=(10, 5))

    start_date = DateEntry(date_frame, width=12, background='darkblue',
                        foreground='white', date_pattern='yyyy-mm-dd')
    start_date.grid(row=0, column=1, padx=5)
    start_date.bind("<<DateEntrySelected>>", on_search)

    ctk.CTkLabel(date_frame, text="~").grid(row=0, column=2)

    end_date = DateEntry(date_frame, width=12, background='darkblue',
                        foreground='white', date_pattern='yyyy-mm-dd')
    end_date.grid(row=0, column=3, padx=5)
    start_date.bind("<<DateEntrySelected>>", on_search)

    # ---------------- 날짜 비교 및 조회 ----------------
    search_btn = ctk.CTkButton(window, text="조회", command=lambda:on_search(True), width=150, height=40)
    search_btn.pack(pady=30)
    # ---------------- DataFrame 표시 ----------------
    table_frame = ctk.CTkFrame(window)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree_scroll = ttk.Scrollbar(table_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(table_frame, yscrollcommand=tree_scroll.set)

    tree_scroll.config(command=tree.yview)

    # 컬럼 설정
    tree["columns"] = list(history.columns)
    tree["show"] = "headings"

    for col in history.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    # 데이터 삽입
    for _, row in history.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(fill="both", expand=True)

    # ---------------- 실행 ----------------
    window.mainloop()

if __name__ == "__main__":
    search()