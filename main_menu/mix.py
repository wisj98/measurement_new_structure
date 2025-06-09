import customtkinter as ctk
import pickle
import pandas as pd
import os
from datetime import datetime

try: from read import read_recipe, format_number, read_font
except: from main_menu.read import read_recipe, format_number, read_font

def mix_start(who):
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
        font=read_font(),
        text="칭량 작업",
        text_color="#ffffff",       # 흰 글자
        bg_color="#333333"          # 배경 회색
    )
    title_label.place(relx=0.0, x=10, y=10, anchor="nw")

    time_label = ctk.CTkLabel(
        window,
        font=read_font(),
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
            font=read_font(),
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
                label = ctk.CTkLabel(scrollable_frame, text=val if type(val) == str else format_number(val), font=read_font(size=12, bold= False), width = widths[c], fg_color="darkgrey")
                label.grid(row=r, column=c,padx=1, pady=1, sticky="w")
            # 목표량 계산 칸
            goal = round(row[1] * how /100, 3)  # kg → g
            label = ctk.CTkLabel(scrollable_frame, text=format_number(goal), font=read_font(size=12, bold= False),width = widths[c+1], fg_color="darkgrey")
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
                label = ctk.CTkLabel(scrollable_frame2, text=str(val), font=read_font(size=12, bold= False), width = widths[c], fg_color="darkgrey")
                label.grid(row=r, column=c,padx=1, pady=1, sticky="w")

        # -------------------- 기타 정보 탭 --------------------
        tab3 = tabview.add("기타")
        info_text = "\n".join(recipe["기타 정보"])
        info_label = ctk.CTkLabel(tab3, text=info_text, anchor="w", justify="left", font=read_font(size=12, bold= False))
        info_label.pack(anchor="w", padx=20, pady=20)

        window.mainloop()

    def refresh_window(orders = False, refresh = False):
        if type(orders) != pd.DataFrame: orders = pd.read_csv(file_name)
        orders = orders.sort_values(by="현재 단계").reset_index(drop=True)
        orders = orders[orders["현재 단계"].str.startswith("2")]
        for widget in inner_frame.winfo_children():
            widget.destroy()
        for i in range(len(orders)):
            order_frame = ctk.CTkFrame(master=inner_frame, height=45)
            order_frame.pack(side="top", fill="x", pady=1)

            for idx, title in enumerate(orders.columns):
                if title == "현재 단계":
                    label = ctk.CTkLabel(
                        master=order_frame,
                        text="2:칭량 완료",
                        font=read_font(size=12),
                        width=column_widths[idx],
                        height=40,
                        anchor="center", 
                        fg_color="#BBBBBB",
                        text_color="black", corner_radius=0
                    )
                    label.grid(row=0, column=idx, sticky="nsew", padx=1)
                else:
                    label = ctk.CTkLabel(
                        master=order_frame,
                        text=orders.iloc[i][title],
                        font=read_font(size=13),
                        width=column_widths[idx],
                        height=40,
                        anchor="center", 
                        fg_color="#BBBBBB",
                        text_color="black", corner_radius=0
                    )
                    label.grid(row=0, column=idx, sticky="nsew", padx=1)
            check_button = ctk.CTkButton(master=order_frame,
                    text = "확인",font=read_font(size=13),
                    width=column_widths[idx+1],
                    height=40,
                    anchor="center", 
                    fg_color="#BBBBBB",
                    text_color="black",
                    command=lambda i=i, orders=orders: check(orders, i), corner_radius=0
                    )
            check_button.grid(row=0, column=idx+1, sticky="nsew", padx=1)

            save_button = ctk.CTkButton(master=order_frame,
                    text = "작업 시작",font=read_font(size=13),
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

    save_button = ctk.CTkButton(button_frame, text="종료하기", font=(read_font(size=40)), command=save_data, height=100, width= 300)
    save_button.pack(side="left", padx=1)

    window.mainloop()
#------------------------------------------------------------------------------------------------
def work(order, who):
    with open("config.pickle", "rb") as fr:
        config = pickle.load(fr)

    window = ctk.CTk()
    window.title("배합 작업")
    window.geometry("1020x900+0+0")

    up_frame = ctk.CTkFrame(master=window, height=40, fg_color="#333333", corner_radius=0)
    up_frame.pack(side="top", fill="x",pady=[0,5])

    title_label = ctk.CTkLabel(
        window,
        font=read_font(),
        text=f"작업자: {who}",
        text_color="#ffffff",       # 흰 글자
        bg_color="#333333"          # 배경 회색
    )
    title_label.place(relx=0.0, x=10, y=10, anchor="nw")

    time_label = ctk.CTkLabel(
        window,
        font=read_font(),
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
    recipe = read_recipe(config["BOM 경로"])[order["제품명"]]["배합"]


    columns_frame = ctk.CTkFrame(master=window, height=40)
    columns_frame.pack(side="top", fill="x")
    column_titles = [
        "원료명", "작업 순서", "대기 시간", "작업단계"
    ]
    column_widths = [500,165,165,165]
    for idx, title in enumerate(column_titles):
        label = ctk.CTkLabel(
            master=columns_frame,
            text=title,
            font=read_font(),
            width=column_widths[idx],
            height=80,
            anchor="center",  # 가운데 정렬
            fg_color="#52ADD4",  # 이전에 조정한 컬러
            text_color="black"
        )
        if idx == 0: label.grid(row=0, column=idx, sticky="nsew", padx=[7,1])
        else: label.grid(row=0, column=idx, sticky="nsew", padx=1)

#------------------------------------------------------------------------------------------------
    now_labels = {}
    ingredients_frame = ctk.CTkScrollableFrame(master=window, height=650, fg_color="#BBBBBB")
    ingredients_frame.pack(side="top",pady=[0,5], fill="x")

    waitings = []
    mix_buttons = [] 
    def toggle(wait, row):
        wait = round(wait)
        if wait != 0:
            waitings[row].configure(text=f"{wait//60}:{(wait%60)}", fg_color="lightyellow")
            mix_buttons[row].configure(fg_color="lightyellow", command = None)
            window.after(1000, lambda: toggle(wait-1, row))
        else:
            waitings[row].configure(text=f"{wait//60}:{(wait%60)}", fg_color="lightgreen")
            mix_buttons[row].configure(text="배합 완료", fg_color="lightgreen")

    for row, ingredient in enumerate(recipe):
        ingredient_name = ingredient[0]  # 재료 이름
        orders = ingredient[1]
        wait_time = ingredient[2]

        ingredient_frame = ctk.CTkFrame(master=ingredients_frame, height=50)
        ingredient_frame.pack(side="top",pady=[0,5], fill="x")

        ctk.CTkLabel(ingredient_frame, text=f"{ingredient_name}", font=read_font(size=13), width = column_widths[0], height=50, justify="left", anchor="w", fg_color="#AAAAAA",corner_radius=0).pack(side="left", padx=1, pady=[0,1])
        ctk.CTkLabel(ingredient_frame, text=orders, font=read_font(size=13), width = column_widths[1], height=50, justify="left", fg_color="#AAAAAA",corner_radius=0).pack(side="left", padx=1, pady=[0,1])
        waitings.append(ctk.CTkLabel(ingredient_frame, text=f"{wait_time//1}:{(wait_time%1)*60}", font=read_font(size=13), width = column_widths[2], height=50, justify="left", fg_color="#AAAAAA",corner_radius=0))
        waitings[row].pack(side="left", padx=1, pady=[0,1])
        mix_buttons.append(ctk.CTkButton(ingredient_frame, text="배합 전", font=read_font(size=13), width = column_widths[3],height=50, command = lambda wait = wait_time, row = row:toggle((wait//1)*60 + (wait%1)*60, row), fg_color="lightgrey",corner_radius=0, text_color="black", hover_color="#AAAAAA"))
        mix_buttons[row].pack(side="right", padx=1, pady=[0,1])
        
#------------------------------------------------------------------------------------------------
    def history(order, recipe_0, worker, recipe_1):
        recipe = recipe_0
        for idx, i in enumerate(recipe):
            for j in recipe_1:
                if i[0] == j[0]:
                    recipe[idx] += j[1:]
            for j in [ingre.split(":") for ingre in order["현재 단계"].split("|")[-1].split("=")]:
                if i[0] == j[0]:
                    recipe[idx] += j[1:]

        print(recipe)
        date = [order["현재 단계"].split("|")[2], "", "원료명"] + [r[0] for r in recipe]
        who_0 = [worker, "", "지시량(g)"] + [round(r[3] * order["작업량(g)"] / 100, 3) for r in recipe]
        who_1 = ["","","칭량량(g)"] + [round(float(r[-1]), 3) for r in recipe]
        weight_0 = [order["작업량(g)"], "","작업순서"] + [r[1] for r in recipe]
        weight_1 = ["", "", "대기 시간"] + [r[2] for r in recipe]
        gama = [order["배합 가마"],"", "배합자(서명)"] + ["" for _ in recipe] + ["", "PH", ""]

        # 가장 긴 열의 길이
        max_len = len(gama)

        # 모든 열을 동일한 길이로 패딩
        def pad_column(col):
            return col + [""] * (max_len - len(col))

        df = pd.DataFrame({
            "칭량 일시": pad_column(date),
            "칭량자": pad_column(who_0),
            "": pad_column(who_1),
            "작업량(g)": pad_column(weight_0),
            " ": pad_column(weight_1),
            "배합 가마": pad_column(gama),
        })

        df.to_csv("check.csv", index=False, encoding='cp949')

        os.startfile("check.csv")
#------------------------------------------------------------------------------------------------
    def save(order, PH, who):  # window 인자를 받도록 수정
        try:
            PH = float(PH)
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

            file.loc[mask, "현재 단계"] = "3:배합 완료"
            file.to_csv(file_name, index=False)

            history_path = config["내역 경로"] + "/history/history.csv"
            try: history = pd.read_csv(history_path)
            except: history = pd.DataFrame({"제조 일자":[],
                                        "제조 완료 시각":[],
                                        "작업자(지시자/칭량자/배합자)":[],
                                        "배합 가마":[],
                                        "제품명":[],
                                        "작업량(g)":[],
                                        "PH":[]})
            history.loc[len(history)] = [order["작업일"],
                                         datetime.now().strftime("%H:%M"),
                                         f"{order["지시자"]}/{order["현재 단계"].split("|")[1]}/{who}",
                                         order["배합 가마"],
                                         order["제품명"],
                                         order["작업량(g)"],
                                         PH]
            history.to_csv(history_path, index=False)

            # 팝업창 띄우기
            def on_confirm():
                popup.destroy()
                window.destroy()

            popup = ctk.CTkToplevel(window)
            popup.title("알림")
            popup.geometry("300x150")
            
            label = ctk.CTkLabel(popup, text="저장 완료", font=read_font(size=16))
            label.pack(pady=20)

            button = ctk.CTkButton(popup, text="확인", command=on_confirm)
            button.pack(pady=10)

            popup.grab_set()
        except:
            def on_confirm():
                popup.destroy()

            popup = ctk.CTkToplevel(window)
            popup.title("알림")
            popup.geometry("300x150")
            
            label = ctk.CTkLabel(popup, text="정상적인 PH값이 아니거나,\nPH값이 입력되지 않았습니다.", font=read_font(size=16))
            label.pack(pady=20)

            button = ctk.CTkButton(popup, text="확인", command=on_confirm)
            button.pack(pady=10)

            popup.grab_set()
#------------------------------------------------------------------------------------------------
    buttons_frame = ctk.CTkFrame(master=window, height=100)
    buttons_frame.pack(side="top",pady=[5,5], fill="x")
    PH = ctk.CTkLabel(master=buttons_frame, text=f"PH값 입력", height=100, width=225, font=read_font(size=20))
    PH.pack(side="left",padx=0,fill="x")
    PH_input = ctk.CTkEntry(master=buttons_frame, placeholder_text="0", height=100, width=225, font=read_font(size=20))
    PH_input.pack(side="left",padx=0,fill="x")
    save_button = ctk.CTkButton(master=buttons_frame, height=100, width=190, text="입력 완료", font=read_font(size=20), command=lambda:save(order, PH_input.get(), who), corner_radius=0)
    save_button.pack(side="left",padx=2,fill="x")
    cancel_button = ctk.CTkButton(master=buttons_frame, height=100, width=190, text="배합 취소", font=read_font(size=20), command=window.destroy, corner_radius=0)
    cancel_button.pack(side="left",padx=(0,2),fill="x")
    history_button = ctk.CTkButton(master=buttons_frame, height=100, width=190, text="배합 작업 출력", font=read_font(size=20), command=lambda:history(order, recipe, who, read_recipe(config["BOM 경로"])[order["제품명"]]["칭량"]), corner_radius=0)
    history_button.pack(side="left",padx=(0,2),fill="x")

    window.mainloop()

if __name__ == "__main__":
    mix_start("위성진")