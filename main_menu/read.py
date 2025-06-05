import os
import pandas as pd

def read_recipe(path):
    recipes = [file[:-5] for file in os.listdir(path) if file.endswith('.xlsx')]
    recipe_dict = {}
    for recipe in recipes:
        recipe_path = path+recipe+".xlsx"
        df = pd.read_excel(recipe_path)

        for_a = []
        for_b = []
        etc = ["거래처:"+df.iloc[0]["거래처"], "작성일:"+ df.iloc[0]["작성일"]]

        for _, row in df.iterrows():
            for_a.append([row["원료명"], row["함량(%)"], row["편차(%)"], row["벌크(Y/N)"]])
            for_b.append([row["원료명"], row["작업 순번"], row["대기시간 (분)"]])

        for_a.sort(key=lambda x: x[1])
        for_a.reverse()
        for_b.sort(key=lambda x: x[1])

        recipe_dict[recipe] = {"칭량":for_a, "배합":for_b, "기타 정보":etc}
        
    return recipe_dict

def read_code(path):
    recipes = [file[:-5] for file in os.listdir(path) if file.endswith('.xlsx')]
    code_dict = {}
    for recipe in recipes:
        recipe_path = path+recipe+".xlsx"
        df = pd.read_excel(recipe_path)

        for _, row in df.iterrows():
            if row["바코드(원료코드)"] not in code_dict.keys():
                code_dict[row["바코드(원료코드)"]] = row["원료명"]
        
    return code_dict

def format_number(num, threshold=1e-3):
    if num >= 1000:
        return str(round(num / 1000, 3)) + "(Kg)"
    if abs(num) < threshold and num != 0:
        return f"{round(num, 5):.5f}".rstrip('0').rstrip('.')
    else:
        return str(round(num, 5))
    
def read_font(size = 14, bold = "bold"):
    if bold: return ("pretendard medium", size, bold)
    else: return ("pretendard medium", size)

if __name__ == "__main__":
    print(read_recipe("recipes/"))