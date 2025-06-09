import customtkinter as ctk
import pickle
import pandas as pd
import os
from datetime import datetime
import operator
from datetime import datetime

try: from measuring import measuring
except: from main_menu.measuring import measuring

try: from read import read_recipe, format_number, read_font
except: from main_menu.read import read_recipe, format_number, read_font

def measurement_start(who):
#-------------------------------------------------------------------------
    with open("config.pickle", "rb") as fr:
        config = pickle.load(fr)

    data_path = config["내역 경로"] + "/data"
    if not os.path.exists(data_path):
        try:os.makedirs(data_path)
        except:
            config["내역 경로"] = ""
            data_path = config["내역 경로"] + "/data"
            os.makedirs(data_path)
    today = datetime.today().strftime("%Y_%m_%d")
    file_name = data_path + "/" + today + "_작업지시.csv"

    if os.path.isfile(file_name):
        orders = pd.read_csv(file_name)
    else:
        data = {
            "작업일": [],
            "지시자": [],
            "지시 시간": [],
            "제품명": [],
            "작업량(g)": [],
            "배합 가마": [],
            "현재 단계": []
        }
        orders = pd.DataFrame(data)[["작업일", "지시자", "지시 시간", "제품명", "작업량(g)", "배합 가마", "현재 단계"]]
        orders.to_csv(file_name, index=False)
#-------------------------------------------------------------------------
    window = ctk.CTk()
    window.title("작업 지시")
    window.attributes('-fullscreen', True)

    up_frame = ctk.CTkFrame(master=window, height=40, fg_color="#333333", corner_radius=0)
    up_frame.pack(side="top", fill="x",pady=[0,5])

    title_label = ctk.CTkLabel(
        window,
        font=read_font(size=14),
        text="칭량 작업",
        text_color="#ffffff",       # 흰 글자
        bg_color="#333333"          # 배경 회색
    )
    title_label.place(relx=0.0, x=10, y=10, anchor="nw")

    time_label = ctk.CTkLabel(
        window,
        font=read_font(size=14),
        text_color="#ffffff",       # 흰 글자
        bg_color="#333333"          # 배경 회색
    )
    time_label.place(relx=1.0, x=-10, y=10, anchor="ne")

    def update_time():
        now = datetime.now()
        formatted_time = now.strftime("현재 시각: %Y/%m/%d - %H:%M:%S")
        time_label.configure(text=formatted_time)
        window.after(1000, update_time)

    update_time()
#-------------------------------------------------------------------------
    columns_frame = ctk.CTkFrame(master=window, height=40)
    columns_frame.pack(side="top", fill="x")

    column_titles = [
        "작업일", "지시자", "지시 시간", "제품명", "작업량(g)",
        "배합가마", "현재단계", "내역", "작업 시작"
    ]

    # column 수에 맞게 weight 지정 (동일한 비율로 배분)
    column_widths = [197, 197, 197, 300, 197, 197, 197, 197, 197]

    for idx, title in enumerate(column_titles):
        label = ctk.CTkLabel(
            master=columns_frame,
            text=title,
            font=read_font(size=14),
            width=column_widths[idx],
            height=40,
            anchor="center",  # 가운데 정렬
            fg_color="#52ADD4",  # 이전에 조정한 컬러
            text_color="black"
        )
        if idx == 0: label.grid(row=0, column=idx, sticky="nsew", padx=[7,1])
        else: label.grid(row=0, column=idx, sticky="nsew", padx=1)
#-------------------------------------------------------------------------
    inner_frame = ctk.CTkScrollableFrame(master=window, height=900)
    inner_frame.pack(side="top", fill="x")

    def check(orders, idx):
        recipe = read_recipe(config["BOM 경로"])[orders.iloc[idx]["제품명"]]
        how = orders.iloc[idx]["작업량(g)"]

        window = ctk.CTk()
        window.title(f"{orders.iloc[idx]['제품명']} 정보")
        window.geometry("800x600")

        tabview = ctk.CTkTabview(master=window)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # -------------------- 칭량 탭 --------------------
        tab1 = tabview.add("칭량")
        scrollable_frame = ctk.CTkScrollableFrame(tab1)
        scrollable_frame.pack(fill="both", expand=True)

        columns1 = ["원료명", "함량(%)", "편차(%)", "벌크(Y/N)", "목표량(g)"]
        widths = [250,100,100,100,100]
        for i, col in enumerate(columns1):
            label = ctk.CTkLabel(scrollable_frame, text=col, font=read_font(size=13), width = widths[i], fg_color="grey")
            label.grid(row=0, column=i,padx=1, pady=1)

        for r, row in enumerate(recipe["칭량"], start=1):
            for c, val in enumerate(row):
                label = ctk.CTkLabel(scrollable_frame, text=val if type(val) == str else format_number(val), font=read_font(size=12), width = widths[c], fg_color="darkgrey")
                label.grid(row=r, column=c,padx=1, pady=1, sticky="w")
            # 목표량 계산 칸
            goal = round(row[1] * how / 100, 3)  # kg → g
            label = ctk.CTkLabel(scrollable_frame, text=format_number(goal), font=read_font(size=12),width = widths[c+1], fg_color="darkgrey")
            label.grid(row=r, column=len(row),padx=1, pady=1, sticky="w")

        # -------------------- 배합 탭 --------------------
        tab2 = tabview.add("배합")
        scrollable_frame2 = ctk.CTkScrollableFrame(tab2)
        scrollable_frame2.pack(fill="both", expand=True)

        columns2 = ["원료명", "작업 순번", "대기시간 (분)"]
        widths = [250,100,100]
        for i, col in enumerate(columns2):
            label = ctk.CTkLabel(scrollable_frame2, text=col, font=read_font(size=13), width = widths[i], fg_color="grey")
            label.grid(row=0, column=i,padx=1, pady=1)

        for r, row in enumerate(recipe["배합"], start=1):
            for c, val in enumerate(row):
                label = ctk.CTkLabel(scrollable_frame2, text=str(val), font=read_font(size=12), width = widths[c], fg_color="darkgrey")
                label.grid(row=r, column=c,padx=1, pady=1, sticky="w")

        # -------------------- 기타 정보 탭 --------------------
        tab3 = tabview.add("기타")
        info_text = "\n".join(recipe["기타 정보"])
        info_label = ctk.CTkLabel(tab3, text=info_text, anchor="w", justify="left", font=read_font(size=12))
        info_label.pack(anchor="w", padx=20, pady=20)

        window.mainloop()

    def refresh_window(orders = False, refresh = False):
        if type(orders) != pd.DataFrame: orders = pd.read_csv(file_name)
        orders = orders.sort_values(by="현재 단계").reset_index(drop=True)
        orders = orders[orders["현재 단계"] == "1:작업 전"]
        for widget in inner_frame.winfo_children():
            widget.destroy()
        for i in range(len(orders)):
            order_frame = ctk.CTkFrame(master=inner_frame, height=45)
            order_frame.pack(side="top", fill="x", pady=1)

            for idx, title in enumerate(orders.columns):
                label = ctk.CTkLabel(
                    master=order_frame,
                    text=orders.iloc[i][title],
                    font=read_font(size=12),
                    width=column_widths[idx],
                    height=40,
                    anchor="center", 
                    fg_color="#BBBBBB",
                    text_color="black", corner_radius=0
                )
                label.grid(row=0, column=idx, sticky="nsew", padx=1)
            check_button = ctk.CTkButton(master=order_frame,
                    text = "확인",font=read_font(size=12),
                    width=column_widths[idx+1],
                    height=40,
                    anchor="center", 
                    fg_color="#BBBBBB",
                    text_color="black",
                    command=lambda i=i, orders=orders: check(orders, i), corner_radius=0
                    )
            check_button.grid(row=0, column=idx+1, sticky="nsew", padx=1)

            save_button = ctk.CTkButton(master=order_frame,
                    text = "작업 시작",font=read_font(size=12),
                    width=column_widths[idx+2],
                    height=40,
                    anchor="center", 
                    fg_color="#BBBBBB",
                    text_color="black",
                    command=lambda i=i, orders=orders: work(orders.iloc[i], who), corner_radius=0
                    )
            save_button.grid(row=0, column=idx+2, sticky="nsew", padx=1)

        if refresh:
            window.after(30000, lambda refresh=refresh: refresh_window(refresh==True))

    refresh_window(refresh=True)
#------------------------------------------------------------------------------------------------
    def save_data():
        window.destroy()

    # 버튼 프레임 생성
    button_frame = ctk.CTkFrame(window)
    button_frame.pack(pady=10)

    save_button = ctk.CTkButton(button_frame, text="종료하기", font=read_font(size=40), command=save_data, height=100, width= 300)
    save_button.pack(side="left", padx=1)

    window.mainloop()
#------------------------------------------------------------------------------------------------
def work(order, who):
    with open("config.pickle", "rb") as fr:
        config = pickle.load(fr)

    window = ctk.CTk()
    window.title("작업 지시")
    window.attributes('-fullscreen', True)

    up_frame = ctk.CTkFrame(master=window, height=40, fg_color="#333333", corner_radius=0)
    up_frame.pack(side="top", fill="x",pady=[0,5])

    title_label = ctk.CTkLabel(
        window,
        font=read_font(size=14),
        text="칭량 작업",
        text_color="#ffffff",       # 흰 글자
        bg_color="#333333"          # 배경 회색
    )
    title_label.place(relx=0.0, x=10, y=10, anchor="nw")

    time_label = ctk.CTkLabel(
        window,
        font=read_font(size=14),
        text_color="#ffffff",       # 흰 글자
        bg_color="#333333"          # 배경 회색
    )
    time_label.place(relx=1.0, x=-10, y=10, anchor="ne")

    def update_time():
        now = datetime.now()
        formatted_time = now.strftime("현재 시각: %Y/%m/%d - %H:%M:%S")
        time_label.configure(text=formatted_time)
        window.after(1000, update_time)

    update_time()
#------------------------------------------------------------------------------------------------
    info_frame = ctk.CTkFrame(window, height = 400, fg_color="#BBBBBB", corner_radius=0, width=1500)
    info_frame.pack(side="top",pady=[30,30], fill=None)

    width = [300,300,300,500,300]
    headers = ["작업일", "지시 시간", "제품명", "작업량(g)"]
    for i, text in enumerate(headers):
        label = ctk.CTkLabel(info_frame, text=text, font=read_font(size=20), fg_color="#AAAAAA", text_color="black", corner_radius=0, width=width[i], height=75)
        label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

    data = [order["작업일"], order["지시 시간"], order["제품명"], order["작업량(g)"]]
    for i, text in enumerate(data):
        label = ctk.CTkLabel(info_frame, text=text, font=(read_font(size=18)), fg_color="#AAAAAA", text_color="black", corner_radius=0, width=width[i], height=75)
        label.grid(row=1, column=i, sticky="nsew", padx=1, pady=1)

    recipe = read_recipe(config["BOM 경로"])[order["제품명"]]["칭량"]

    columns_frame = ctk.CTkFrame(master=window, height=40)
    columns_frame.pack(side="top", fill="x")
    column_titles = [
        "원료명", "기준량(g)", "칭량값(g)", "칭량"
    ]
    column_widths = [900,250,250,500]
    for idx, title in enumerate(column_titles):
        label = ctk.CTkLabel(
            master=columns_frame,
            text=title,
            font=read_font(size=14),
            width=column_widths[idx],
            height=80,
            anchor="center",  # 가운데 정렬
            fg_color="#52ADD4",  # 이전에 조정한 컬러
            text_color="black"
        )
        if idx == 0: label.grid(row=0, column=idx, sticky="nsew", padx=[7,1])
        else: label.grid(row=0, column=idx, sticky="nsew", padx=1)

    for i in range(len(recipe)):
        recipe[i][1] = (recipe[i][1]/100)*order["작업량(g)"]
        recipe[i][2] = round(recipe[i][1]*recipe[i][2]*10,3)
#------------------------------------------------------------------------------------------------
    now_labels = {}

    def measurement(data):
        target, standard, error = data[0], data[1], data[2]
        popup_window = ctk.CTkToplevel(window)
        popup_window.geometry("511x301")
        popup_window.wm_attributes("-topmost", 1)
        popup_window.title(f"{target} 칭량 중...")
        popup_window.focus_force()
        popup_window.lift()

        top_frame = ctk.CTkLabel(master=popup_window, height=100, width = 500, text=f"{target}", font=read_font(size=30), fg_color="grey")
        top_frame.grid(row=0,column=0,sticky="new")

        middle_frame = ctk.CTkLabel(master=popup_window,height=100, width =500, text=f"기준량: {format_number(standard)} g", font=read_font(size=30), fg_color="lightgrey")
        middle_frame.grid(row=1,column=0,sticky="new")

        bottom_frame = ctk.CTkFrame(master=popup_window, height=100, width =500)
        bottom_frame.grid(row=2, column = 0, sticky="nsew")
        count = 0
        def update_value():
            nonlocal now_labels, count
            _ = round(measuring(),3)
            # _ = 90

            if _ != 0 or _ >= 100 or (count >= 3 and _ == 0): 
                now_labels[target][1] = _
                count = 0
            else: count += 1
            if target != 0:
                if round(now_labels[target][1],3) < round(standard-error,3) or round(now_labels[target][1],3) > round(standard+error,3):
                    popup_container_3_now.configure(fg_color="yellow", text_color="black")
                    now_labels[target][-1].configure(fg_color = "lightyellow")
                else:
                    popup_container_3_now.configure(fg_color="green", text_color="black")
                    now_labels[target][-1].configure(fg_color = "lightgreen")
                now_labels[target][0].configure(text = now_labels[target][1])
            popup_container_3_now.configure(text=format_number(now_labels[target][1])+"g")
            popup_container_3_now.after(500, update_value)

        popup_container_3_now = ctk.CTkLabel(master=bottom_frame, text=f"{round(now_labels[target][1],3)}g", font=read_font(size=50), width = 350, height=100)
        popup_container_3_now.grid(row=0, column = 0, sticky="nsew")

        def update_value_():
            popup_window.destroy()

        popup_container_3_done = ctk.CTkButton(master=bottom_frame, text="측정 종료", font=read_font(size=30), command = lambda: update_value_(), width = 150, height=100, corner_radius=0)
        popup_container_3_done.grid(row=0, column=1, sticky="nsew",padx=(10,0))

        update_value()
        popup_window.mainloop()
#------------------------------------------------------------------------------------------------
    ingredients_frame = ctk.CTkScrollableFrame(master=window, height=650, fg_color="#BBBBBB")
    ingredients_frame.pack(side="top",pady=[0,5], fill="x")
    column_widths = [900,250,250,250,250]
    for row, ingredient in enumerate(recipe):
        ingredient_name = ingredient[0]  # 재료 이름
        standard_value = ingredient[1]
        error_value = ingredient[2]
        bulk = ingredient[3]

        ingredient_frame = ctk.CTkFrame(master=ingredients_frame, height=50)
        ingredient_frame.pack(side="top",pady=[0,5], fill="x")

        ctk.CTkLabel(ingredient_frame, text=f"{ingredient_name}", font=read_font(size=12), width = 900, height=50, justify="left", anchor="w", fg_color="#AAAAAA",corner_radius=0).pack(side="left", padx=1, pady=[0,1])
        ctk.CTkLabel(ingredient_frame, text=format_number(standard_value), font=read_font(size=12), width = 250, height=50, justify="left", fg_color="#AAAAAA",corner_radius=0).pack(side="left", padx=1, pady=[0,1])
        now_labels[ingredient_name] = [ctk.CTkLabel(ingredient_frame, text=f"0", font=read_font(size=12), width = 250, height=50, justify="left", fg_color="#AAAAAA",corner_radius=0), 0, ingredient_frame]
        now_labels[ingredient_name][0].pack(side="left", padx=1, pady=[0,1])

        if bulk == "Y":
            ctk.CTkButton(ingredient_frame, text="칭량 완료", font=read_font(size=12), width = 250,height=50, command = lambda ingre = ingredient_name, stan = standard_value : (now_labels[ingre][0].configure(text=f"{format_number(stan)}"), operator.setitem(now_labels[ingre], 1, stan)), fg_color="lightgreen",corner_radius=0, text_color="black").pack(side="right", padx=1, pady=[0,1])
        else:
            now_labels[ingredient_name].append(ctk.CTkLabel(ingredient_frame, text="칭량 완료", font=read_font(size=12), width = 250,height=50, fg_color="#AAAAAA",corner_radius=0))
            now_labels[ingredient_name][-1].pack(side="right", padx=1, pady=[0,1])
        ctk.CTkButton(ingredient_frame, text="칭량 시작", font=read_font(size=12), width = 250,height=50, command = lambda data = [ingredient_name, standard_value, error_value]: measurement(data), fg_color="#AAAAAA",corner_radius=0, text_color="black").pack(side="left", padx=1, pady=[0,1])
#------------------------------------------------------------------------------------------------
    def history(order, now_labels, worker):
        app = ctk.CTk()
        app.geometry("950x900+0+0")
        app.title("청정작업 기록서")

        # 제품 정보 프레임
        info_frame = ctk.CTkFrame(app, height = 400, fg_color="#BBBBBB", corner_radius=0, width=750)
        info_frame.pack(side="top",pady=[0,5], fill=None)

        width = [150,150,150,250,150]
        headers = ["제품명", "제조번호(Lot No.)", "칭량일", "칭량자", "제조 지시량(g)"]
        for i, text in enumerate(headers):
            label = ctk.CTkLabel(info_frame, text=text, font=read_font(size=14), fg_color="#AAAAAA", text_color="black", corner_radius=0, width=width[i], height=75)
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        data = [order["제품명"], datetime.now().strftime("%Y%m%d%H%M%S"), datetime.now().strftime("%Y-%m-%d_%H:%M:%S"), worker, order["작업량(g)"]]
        for i, text in enumerate(data):
            label = ctk.CTkLabel(info_frame, text=text, font=read_font(size=12), fg_color="#AAAAAA", text_color="black", corner_radius=0, width=width[i], height=75)
            label.grid(row=1, column=i, sticky="nsew", padx=1, pady=1)

        # 점검사항 프레임
        check_frame = ctk.CTkFrame(app)
        check_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(check_frame, text="    작업 전 점검사항", anchor="w", fg_color="#BBBBBB", font=read_font(size=14)).pack(fill="x", expand=True, padx=0, pady=0)
        check_texts = config["작업 전 점검사항"]

        for i, text in enumerate(check_texts):
            ctk.CTkLabel(check_frame, text=text, anchor="w", font=("pretendard medium", 12)).pack(anchor="w", padx=10, pady=2)

        # 원료 리스트 프레임
        list_frame = ctk.CTkScrollableFrame(app)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        headers = ["번호", "원료코드", "원료명", "함량(%)", "기준량(g)", "청량값(g)"]
        width = [131,131,250,131,131,131]
        for i, text in enumerate(headers):
            label = ctk.CTkLabel(list_frame, text=text, font=read_font(size=14), fg_color="#AAAAAA", text_color="black", corner_radius=0, width=width[i], height=30)
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        #수정 해야 함
        recipe_ = read_recipe(config["BOM 경로"])[order["제품명"]]['칭량']

        rows = []

        for i, key in enumerate(now_labels.keys()):
            rows.append([i+1, "",key, format_number(recipe_[i][1]), format_number((recipe_[i][1]/100)*order["작업량(g)"]), format_number(now_labels[key][1])])

        for i, row in enumerate(rows, start=1):
            for j, val in enumerate(row):
                ctk.CTkLabel(list_frame, text=val, width=120).grid(row=i, column=j)

        product_col = [data[0], headers[0]] + [rows[i][0] for i in range(len(rows))]
        lot_col = [data[1], headers[1]] + [rows[i][1] for i in range(len(rows))]
        date_col = [data[2], headers[2]] + [rows[i][2] for i in range(len(rows))]
        worker_col = [data[3], headers[3]] + [rows[i][3] for i in range(len(rows))]
        amount_col = [data[4], headers[4]] + [rows[i][4] for i in range(len(rows))]
        final_col = ["", headers[5]] + [rows[i][5] for i in range(len(rows))]

        checklist_col = config["작업 전 점검사항"]

        # 가장 긴 열의 길이
        max_len = max(len(product_col), len(checklist_col))

        # 모든 열을 동일한 길이로 패딩
        def pad_column(col):
            return col + [""] * (max_len - len(col))

        df = pd.DataFrame({
            "제품명": pad_column(product_col),
            "제조번호(Lot No.)": pad_column(lot_col),
            "칭량일": pad_column(date_col),
            "칭량자": pad_column(worker_col),
            "제조 지시량(g)": pad_column(amount_col),
            "  ": pad_column(final_col),
            " ": pad_column([]),
            "    작업 전 점검사항": pad_column(checklist_col),
        })

        df.to_csv("check.csv", index=False, encoding='cp949')

        # 출력 버튼
        print_button = ctk.CTkButton(app, text="엑셀 출력", width=200, command=lambda :os.startfile("check.csv"))
        print_button.pack(pady=20)

        app.mainloop()
#------------------------------------------------------------------------------------------------
    def save(order, who, now_labels):  # window 인자를 받도록 수정
        print(now_labels)
        with open("config.pickle", "rb") as fr:
            config = pickle.load(fr)

        data_path = config["내역 경로"] + "/data"
        if not os.path.exists(data_path):
            try:os.makedirs(data_path)
            except:
                config["내역 경로"] = ""
                data_path = config["내역 경로"] + "/data"
                os.makedirs(data_path)

        today = datetime.today().strftime("%Y_%m_%d")
        file_name = data_path + "/" + today + "_작업지시.csv"
        file = pd.read_csv(file_name)

        mask = (
            (file["지시자"] == order["지시자"]) &
            (file["지시 시간"] == order["지시 시간"]) &
            (file["제품명"] == order["제품명"])
        )

        weights = [f"{key}:{now_labels[key][1]}" for key in now_labels.keys()]
        file.loc[mask, "현재 단계"] = f"2:칭량 완료|{who}|{datetime.today().strftime("%Y/%m/%d, %h:%m")}|{"=".join(weights)}"
        file.to_csv(file_name, index=False)

        # 팝업창 띄우기
        def on_confirm():
            popup.destroy()
            window.destroy()

        popup = ctk.CTkToplevel(window)
        popup.title("알림")
        popup.geometry("300x150")
        
        label = ctk.CTkLabel(popup, text="저장 완료", font=read_font(size=16, bold=False))
        label.pack(pady=20)

        button = ctk.CTkButton(popup, text="확인", command=on_confirm)
        button.pack(pady=10)

        popup.grab_set()
#------------------------------------------------------------------------------------------------
    buttons_frame = ctk.CTkFrame(master=window, height=100)
    buttons_frame.pack(side="top",pady=[5,5], fill="x")
    worker = ctk.CTkLabel(master=buttons_frame, text=f"작업자: {who}", height=100, width=450, font=read_font(size=40))
    worker.pack(side="left",padx=15,fill="x")
    save_button = ctk.CTkButton(master=buttons_frame, height=100, width=450, text="전체 칭량 완료", font=read_font(size=40), command=lambda:save(order, who, now_labels))
    save_button.pack(side="left",padx=15,fill="x")
    cancel_button = ctk.CTkButton(master=buttons_frame, height=100, width=450, text="칭량 취소", font=read_font(size=40), command=window.destroy)
    cancel_button.pack(side="left",padx=15,fill="x")
    history_button = ctk.CTkButton(master=buttons_frame, height=100, width=450, text="칭량작업 기록서", font=read_font(size=40), command=lambda:history(order, now_labels, who))
    history_button.pack(side="left",padx=15,fill="x")

    window.mainloop()

if __name__ == "__main__":
    measurement_start("위성진")