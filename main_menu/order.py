import customtkinter as ctk
import pickle
import pandas as pd
import os
from datetime import datetime
from CTkMessagebox import CTkMessagebox

try: from read import read_recipe, format_number, read_font
except: from main_menu.read import read_recipe, format_number, read_font

def order_start(who):
    #---------------------------------------------------------------------------------------------------------
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
        orders = orders.sort_values(by="현재 단계").reset_index(drop=True)
        print(file_name)
    else:
        # test
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
    #---------------------------------------------------------------------------------------------------------
    window = ctk.CTk()
    window.title("작업 지시")
    window.attributes('-fullscreen', True)

    up_frame = ctk.CTkFrame(master=window, height=40, fg_color="#333333", corner_radius=0)
    up_frame.pack(side="top", fill="x",pady=[0,5])

    title_label = ctk.CTkLabel(
        window,
        font=read_font(size=14),
        text="작업 지시",
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
    #---------------------------------------------------------------------------------------------------------
    columns_frame = ctk.CTkFrame(master=window, height=40)
    columns_frame.pack(side="top", fill="x")

    column_titles = [
        "작업일", "지시자", "지시 시간", "제품명", "작업량(g)",
        "배합가마", "현재단계", "내역", "확정", "삭제"
    ]

    # column 수에 맞게 weight 지정 (동일한 비율로 배분)
    column_widths = [175, 175, 175, 300, 175, 175, 175, 175, 175, 175]

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
    #---------------------------------------------------------------------------------------------------------
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

    def save(orders, idx):
        orders.loc[idx, "현재 단계"] = "1:작업 전"
        orders.to_csv(file_name, index=False)
        refresh_window(orders)

    def delete(orders, idx):
        orders = orders.drop(index=idx).reset_index(drop=True)
        orders.to_csv(file_name, index=False)
        refresh_window(orders)

    def refresh_window(orders = False, refresh = False):
        if type(orders) != pd.DataFrame: orders = pd.read_csv(file_name)
        orders = orders.sort_values(by="현재 단계").reset_index(drop=True)
        for widget in inner_frame.winfo_children():
            widget.destroy()
        for i in range(len(orders)):
            order_frame = ctk.CTkFrame(master=inner_frame, height=45)
            order_frame.pack(side="top", fill="x", pady=1)

            for idx, title in enumerate(orders.columns):
                if title == "현재 단계":
                    label = ctk.CTkLabel(
                        master=order_frame,
                        text=orders.iloc[i][title].split("|")[0],
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
            if orders.iloc[i][title].split("|")[0][0] == "0":
                save_button = ctk.CTkButton(master=order_frame,
                        text = "저장",font=read_font(size=12),
                        width=column_widths[idx+2],
                        height=40,
                        anchor="center", 
                        fg_color="#BBBBBB",
                        text_color="black",
                        command=lambda i=i, orders=orders: save(orders, i), corner_radius=0
                        )
            else:
                save_button = ctk.CTkButton(master=order_frame,
                        text = "저장",font=read_font(size=12),
                        width=column_widths[idx+2],
                        height=40,
                        anchor="center", 
                        fg_color="#BBBBBB",
                        text_color="black",
                        command=None, corner_radius=0
                        )
            save_button.grid(row=0, column=idx+2, sticky="nsew", padx=1)

            delete_button = ctk.CTkButton(master=order_frame,
                    text = "삭제",font=read_font(size=12),
                    width=column_widths[idx+3],
                    height=40,
                    anchor="center", 
                    fg_color="#BBBBBB",
                    text_color="black",
                    command=lambda i=i, orders=orders: delete(orders, i), corner_radius=0)
            delete_button.grid(row=0, column=idx+3, sticky="nsew", padx=1)
        if refresh:
            window.after(30000, lambda refresh=refresh: refresh_window(refresh==True))

    refresh_window(refresh=True)
#---------------------------------------------------------------------------------------------------------
    def add_order():
        add_window = ctk.CTk()
        add_window.title("작업 지시 추가")
        add_window.geometry("775x400")  # 창 크기 3배로 조정

        gamas = config["배합 가마"]

        recipes = read_recipe(config["BOM 경로"])

        ctk.CTkLabel(add_window, text="지시자:", font=read_font(size=30)).grid(row=0, column=0, padx=30, pady=(50,10), sticky="e")
        worker_Label = ctk.CTkLabel(add_window, font=read_font(size=30), width=500, text=who)
        worker_Label.grid(row=0, column=1, padx=30, pady=(50,10))

        ctk.CTkLabel(add_window, text="제품명:", font=read_font(size=30)).grid(row=1, column=0, padx=30, pady=10, sticky="e")

        options = list(recipes.keys())
        product_combobox = ctk.CTkComboBox(add_window, values=options, font=read_font(size=30), width=500, dropdown_font=read_font(size=25))
        product_combobox.grid(row=1, column=1, padx=30, pady=10)

        ctk.CTkLabel(add_window, text="작업량(g):", font=read_font(size=30)).grid(row=2, column=0, padx=30, pady=10, sticky="e")
        amount_entry = ctk.CTkEntry(add_window, font=read_font(size=30), width=500)
        amount_entry.grid(row=2, column=1, padx=30, pady=10)

        ctk.CTkLabel(add_window, text="배합가마:", font=read_font(size=30)).grid(row=3, column=0, padx=30, pady=10, sticky="e")
        gama_combobox = ctk.CTkComboBox(add_window, font=read_font(size=30), width=500, values=gamas)
        gama_combobox.grid(row=3, column=1, padx=30, pady=10)

        def submit_order():
            orders = pd.read_csv(file_name)

            product = product_combobox.get()
            amount = amount_entry.get()
            gama = gama_combobox.get()

            if not product or not amount:
                CTkMessagebox(title="오류", message="모든 필드를 채워주세요.", icon="cancel")
                add_window.destroy()
            try:
                amount = int(amount)
            except ValueError:
                CTkMessagebox(title="오류", message="작업량은 숫자로 입력해야 합니다.", icon="cancel")
                add_window.destroy()
                return

            new_order = {
                "작업일": datetime.today().strftime("%Y-%m-%d"),
                "지시자": who,
                "지시 시간": datetime.now().strftime("%H:%M"),
                "제품명": product,
                "작업량(g)": amount,
                "배합 가마": gama,
                "현재 단계": "0: 확정 전"
            }
            orders = pd.concat([orders, pd.DataFrame(new_order, index=[0])], ignore_index=True)
            orders.to_csv(file_name, index=False)
            refresh_window()
            add_window.destroy()

        submit_button = ctk.CTkButton(add_window, text="작업 추가", font=read_font(size=40), command=submit_order, width = 750, height = 75)
        submit_button.grid(row=4, column=0, columnspan=2, pady=30)

        add_window.mainloop()

    def save_data():
        window.destroy()

    # 버튼 프레임 생성
    button_frame = ctk.CTkFrame(window)
    button_frame.pack(pady=10)

    # 버튼 생성 및 배치
    add_button = ctk.CTkButton(button_frame, text="작업 지시", font=read_font(size=40), command=add_order, height=100, width= 300)
    add_button.pack(side="left", padx=10)

    save_button = ctk.CTkButton(button_frame, text="종료하기", font=read_font(size=40), command=save_data, height=100, width= 300)
    save_button.pack(side="left", padx=10)

    window.mainloop()


if __name__ == "__main__":
    order_start("위성진")