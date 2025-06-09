import customtkinter as ctk
import tkinter.messagebox as msgbox

from main_menu.order import order_start
try: 
    from main_menu.measurement import measurement_start
    check_measure = True
except:
    check_measure = False
from main_menu.mix import mix_start
from main_menu.search import search

from main_menu.config import config, check_web, check_pickle
import os
import sys
from PIL import Image
from main_menu.read import read_font

BASE_DIR = os.path.dirname(sys.executable)

def login():
    username = username_entry.get()
    password = password_entry.get()
    token = check_web(username, password)
    if token == True:
        result_label.configure(text="로그인 성공!")
        app.destroy()
        main_menu()
    else:
        popup = ctk.CTkToplevel()
        popup.title("로그인 실패")
        popup.geometry("600x300")
        
        label = ctk.CTkLabel(popup, text=f"로그인 실패!\n\n\n{token}", font=read_font(size=20))
        label.pack(expand=True, padx=20, pady=20)
        
        button = ctk.CTkButton(popup, text="확인", command=popup.destroy)
        button.pack(pady=10)

def worker_login(which):
    config_ = check_pickle()

    workers = {}
    for i in config_[which] + config_["관리자"]:
        workers[i[0]] = i[1]

    def login_action():
        username = entry_username.get()
        password = entry_password.get()

        if username in workers and workers[username] == password:
            msgbox.showinfo("로그인 성공", f"{username}님 환영합니다.")
            next_action = {
            "관리자": config,
            "작업 지시자": lambda: order_start(username),
            "칭량 작업자": lambda: measurement_start(username),
            "배합 작업자": lambda: mix_start(username)
        }
            login_window.destroy()
            next_action[which]()
        else:
            msgbox.showerror("로그인 실패", "아이디 또는 비밀번호가 잘못되었습니다.")

    # 창 생성
    login_window = ctk.CTk()
    login_window.title("작업자 로그인")
    login_window.geometry("300x200")

    if len(workers) == 0 and which == "관리자":
        login_window.destroy()
        config()

    label_title = ctk.CTkLabel(login_window, text=f"{which} 로그인", font=read_font(size=20))
    label_title.pack(pady=10)

    entry_username = ctk.CTkEntry(login_window, placeholder_text="아이디")
    entry_username.pack(pady=5)

    entry_password = ctk.CTkEntry(login_window, placeholder_text="비밀번호", show="*")
    entry_password.pack(pady=5)

    login_button = ctk.CTkButton(login_window, text="로그인", command=login_action)
    login_button.pack(pady=10)

    login_window.mainloop()

def main_menu():
    mainmenu = ctk.CTk()
    mainmenu.title("메인 메뉴")
    mainmenu.geometry("600x700")

    bg_image = ctk.CTkImage(dark_image=Image.open("pictures/background.jpg"), size=(mainmenu.winfo_screenwidth(), mainmenu.winfo_screenheight()))

    # 배경 레이블 생성 (이미지를 Label 위에 띄우기)
    bg_label = ctk.CTkLabel(mainmenu, image=bg_image, text="")
    bg_label.place(relwidth=1, relheight=1)

    # 버튼 생성
    gear_image = ctk.CTkImage(light_image=Image.open("pictures/config.png"), size=(24, 24))
    config_button = ctk.CTkButton(
    master=mainmenu,
    image=gear_image,
    text="",
    command=lambda: worker_login("관리자"),
    width=40,
    height=40,
    corner_radius=0,
    fg_color="#52ADD4",
    hover_color="#52ADD4",  
    bg_color="transparent")
    config_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
    
    order_button = ctk.CTkButton(master=mainmenu, text="작업 지시", command=lambda: worker_login("작업 지시자"), font=read_font(), width=200, height=50, corner_radius=0)  # 폰트 크기, width, height 5배 조정
    order_button.pack(pady=(50,15), padx=40)

    measure_button = ctk.CTkButton(master=mainmenu, text="칭량 작업", command=lambda: worker_login("칭량 작업자"), font=read_font(), width=200, height=50, corner_radius=0)
    measure_button.pack(pady=15, padx=40)

    mix_button = ctk.CTkButton(master=mainmenu, text="배합 작업", command=lambda: worker_login("배합 작업자"), font=read_font(), width=200, height=50, corner_radius=0)
    mix_button.pack(pady=15, padx=40)

    history_button = ctk.CTkButton(master=mainmenu, text="내역 조회", command=search, font=read_font(), width=200, height=50, corner_radius=0)
    history_button.pack(pady=15, padx=40)

    exit_button = ctk.CTkButton(master=mainmenu, text="프로그램 종료", command=mainmenu.destroy, font=read_font(), width=200, height=50, corner_radius=0)
    exit_button.pack(pady=15, padx=40)

    mainmenu.mainloop()

# 앱 생성
app = ctk.CTk()
app.geometry("1725x900+0+0")  # 창 크기를 1.5배로 변경
app.title("로그인")

# 중앙 정렬을 위한 그리드 설정
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=1)
app.grid_rowconfigure(2, weight=1)
app.grid_rowconfigure(3, weight=1)
app.grid_rowconfigure(4, weight=1)

# 제목 레이블
_ = "생산 관리 시스템"
if check_measure == False:
    _ = "생산 관리 시스템\n(저울이 연결되지 않은 상태입니다.)"
title_label = ctk.CTkLabel(master=app, text=_, font=read_font(size=80))
title_label.grid(row=0, column=0, columnspan=2, pady=(150, 0), sticky="n")  # 중앙 배치

# 아이디 레이블 및 입력 필드
username_label = ctk.CTkLabel(master=app, text="아이디:", font=read_font(size=40))
username_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")  # 오른쪽 정렬
username_entry = ctk.CTkEntry(master=app, placeholder_text="아이디를 입력하세요", width=800, font=read_font(size=40))
username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")  # 왼쪽 정렬

# 비밀번호 레이블 및 입력 필드
password_label = ctk.CTkLabel(master=app, text="비밀번호:", font=read_font(size=40))
password_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
password_entry = ctk.CTkEntry(master=app, placeholder_text="비밀번호를 입력하세요", show="*", width=800, font=read_font(size=40))
password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# 버튼 프레임
button_frame = ctk.CTkFrame(master=app, fg_color="#F0F0F0")
button_frame.grid(row=3, column=0, columnspan=2, pady=60, sticky="n")

# 로그인 및 종료 버튼
login_button = ctk.CTkButton(master=button_frame, text="로그인",command=login ,width=500, height=150, font=read_font(size=60))
login_button.pack(side="left", padx=40)
exit_button = ctk.CTkButton(master=button_frame, text="종료", command=app.quit, width=500, height=150, font=read_font(size=60))
exit_button.pack(side="left", padx=40)

# 결과 레이블
result_label = ctk.CTkLabel(master=app, text="", font=read_font(size=40))
result_label.grid(row=4, column=0, columnspan=2, pady=40, sticky="n")

# 앱 실행
app.mainloop()
