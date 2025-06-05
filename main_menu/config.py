import pickle
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import pandas as pd
from datetime import datetime

def check_web(id, password):
    url = "https://raw.githubusercontent.com/wisj98/measurement_web/main/test.csv"
    df = pd.read_csv(url)
    df = df[(df["ID"] == id) & (df["password"] == password) & (df["program"] == "measurement")]
    if len(df) == 0:
        return "아이디나 비밀번호를 확인해주세요.\n아이디, 비밀번호 찾기 문의는 010-2113-2067로 부탁드립니다."
    if datetime.strptime(df.iloc[0]["until"], "%Y/%m/%d") >= datetime.today():
        return True
    else:
        return f"사용 기한이 {df.iloc[0]["until"]} 부로 만료되었습니다."

def check_pickle():
    try:
        with open("config.pickle","rb") as fr:
            config = pickle.load(fr)
    except:
        config = {
                  "BOM 경로":"",
                  "내역 경로":"",
                  "작업 지시자":[],
                  "칭량 작업자":[],
                  "배합 작업자":[],
                  "관리자":[],
                  "배합 가마":[],
                  "작업 전 점검사항":""
                  }
        with open("config.pickle", "wb") as f:
            pickle.dump(config, f)
    return config

def root(which):
    root_ = ctk.CTk()
    root_.geometry("700x150")
    root_.title(f"{which} 설정")

    config = check_pickle()

    path_label = ctk.CTkLabel(root_, text=f"현재 경로:\n{config[f"{which}"]}", wraplength=350, font=("Pretendard Medium", 14, "bold"), width=600)
    path_label.pack(pady=20, padx=10)

    def set_new_path():
        new_path = filedialog.askdirectory(title="새로운 경로 선택")
        if new_path:
            config[f"{which}"] = new_path+"/"
            path_label.configure(text=f"현재 경로: {config[f"{which}"]}")
            with open("config.pickle","wb") as f:
                pickle.dump(config, f)
    
    set_path_button = ctk.CTkButton(root_, text="새로운 경로 지정", command=set_new_path, font=("Pretendard Medium", 14, "bold"))
    set_path_button.pack(pady=10)

    root_.mainloop()

def worker(which):
    # 기본 설정
    root = ctk.CTk()
    root.geometry("500x400")
    root.title(f"{which} 관리")

    config = check_pickle()
    workers = config[which]

    # 리스트박스 프레임
    list_frame = ctk.CTkFrame(root)
    list_frame.pack(pady=10, fill="both", expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(list_frame, height=10, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    def refresh_listbox():
        listbox.delete(0, tk.END)
        for i, (name, pw) in enumerate(workers):
            listbox.insert(tk.END, f"ID: {name} | 비밀번호: {pw}")

    refresh_listbox()

    # 입력 프레임
    input_frame = ctk.CTkFrame(root)
    input_frame.pack(pady=10)

    name_entry = ctk.CTkEntry(input_frame, placeholder_text="ID")
    name_entry.grid(row=0, column=0, padx=5)

    pw_entry = ctk.CTkEntry(input_frame, placeholder_text="비밀번호", show="*")
    pw_entry.grid(row=0, column=1, padx=5)

    # 추가 함수
    def add_worker():
        name = name_entry.get().strip()
        pw = pw_entry.get().strip()
        if name and pw:
            workers.append([name, pw])
            config[which] = workers
            with open("config.pickle","wb") as f:
                pickle.dump(config, f)
            refresh_listbox()
            name_entry.delete(0, tk.END)
            pw_entry.delete(0, tk.END)

    # 삭제 함수
    def delete_worker():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            del workers[index]
            config[which] = workers
            with open("config.pickle","wb") as f:
                pickle.dump(config, f)
            refresh_listbox()

    # 버튼 프레임
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)

    add_button = ctk.CTkButton(button_frame, text="추가", command=add_worker)
    add_button.grid(row=0, column=0, padx=10)

    del_button = ctk.CTkButton(button_frame, text="삭제", command=delete_worker)
    del_button.grid(row=0, column=1, padx=10)

    root.mainloop()

def gama(which="배합 가마"):
    root = ctk.CTk()
    root.geometry("500x400")
    root.title(f"{which} 관리")

    config = check_pickle()
    workers = config[which]

    list_frame = ctk.CTkFrame(root)
    list_frame.pack(pady=10, fill="both", expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(list_frame, height=10, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    def refresh_listbox():
        listbox.delete(0, tk.END)
        for i, name in enumerate(workers):
            listbox.insert(tk.END, f"{name}")

    refresh_listbox()

    # 입력 프레임
    input_frame = ctk.CTkFrame(root)
    input_frame.pack(pady=10)

    name_entry = ctk.CTkEntry(input_frame, placeholder_text="가마명")
    name_entry.grid(row=0, column=0, padx=5)

    # 추가 함수
    def add_worker():
        name = name_entry.get().strip()
        if name:
            workers.append(name)
            config[which] = workers
            with open("config.pickle","wb") as f:
                pickle.dump(config, f)
            refresh_listbox()
            name_entry.delete(0, tk.END)

    # 삭제 함수
    def delete_worker():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            del workers[index]
            config[which] = workers
            with open("config.pickle","wb") as f:
                pickle.dump(config, f)
            refresh_listbox()

    # 버튼 프레임
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)

    add_button = ctk.CTkButton(button_frame, text="추가", command=add_worker)
    add_button.grid(row=0, column=0, padx=10)

    del_button = ctk.CTkButton(button_frame, text="삭제", command=delete_worker)
    del_button.grid(row=0, column=1, padx=10)

    root.mainloop()

def check_list():
    root_ = ctk.CTk()
    root_.geometry("700x400")
    root_.title("작업 전 점검사항 등록")

    config = check_pickle()
    check = config["작업 전 점검사항"]

    # 안내 라벨
    label = ctk.CTkLabel(root_, text="한 줄에 하나씩 점검 항목을 작성하세요.")
    label.pack(pady=10)

    # 텍스트 박스
    textbox = ctk.CTkTextbox(root_, width=650, height=250)
    textbox.pack(padx=20, pady=10)

    # 기존 점검사항 불러오기
    textbox.delete("1.0", "end")
    for item in check:
        textbox.insert("end", f"{item}\n")

    # 저장 함수
    def save_checklist():
        new_content = textbox.get("1.0", "end").strip().splitlines()
        config["작업 전 점검사항"] = [line.strip() for line in new_content if line.strip()]
        with open("config.pickle", "wb") as f:
            pickle.dump(config, f)

    # 저장 버튼
    save_button = ctk.CTkButton(root_, text="저장", command=save_checklist)
    save_button.pack(pady=10)

    root_.mainloop()

def config():
    window = ctk.CTk()
    window.geometry("600x600+0+0")
    window.title("환경 설정")

    ctk.CTkButton(master=window, text="BOM 경로 관리", command=lambda:root("BOM 경로"), height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=(20,10), padx=20)
    ctk.CTkButton(master=window, text="내역 경로 관리", command=lambda:root("내역 경로"), height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=10, padx=20)
    ctk.CTkButton(master=window, text="작업 지시자 등록", command=lambda:worker("작업 지시자"), height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=10, padx=20)
    ctk.CTkButton(master=window, text="칭량 작업자 등록", command=lambda:worker("칭량 작업자"), height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=10, padx=20)
    ctk.CTkButton(master=window, text="배합 작업자 등록", command=lambda:worker("배합 작업자"), height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=10, padx=20)
    ctk.CTkButton(master=window, text="관리자 등록", command=lambda:worker("관리자"), height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=10, padx=20)
    ctk.CTkButton(master=window, text="배합 가마명 등록", command=gama, height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=10, padx=20)
    ctk.CTkButton(master=window, text="작업 전 점검사항 등록", command=check_list, height =50, width = 300, font=("Pretendard Medium", 14, "bold")).pack(pady=10, padx=20)

    window.mainloop()

if __name__ == "__main__":
    config()