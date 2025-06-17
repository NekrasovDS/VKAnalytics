import openpyxl as ox
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
import random
import tkinter as tk
from tkinter import messagebox

def get_diagram():
    def count_phrases(list1, list2):
        counts = {phrase: 0 for phrase in list1}
        for phrase in list2:
            if phrase in counts:
                counts[phrase] += 1
        return counts

    def delete_n(x):
        return [s.replace("\n", "") for s in x]

    def remove_zeros(dictionary):
        return {key: value for key, value in dictionary.items() if value != 0}

    try:
        wb = ox.load_workbook(filename="user_database_1.xlsx")
    except FileNotFoundError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Ошибка", "Файл 'user_database_1.xlsx' не найден!")
        return

    wb.active = 0
    sheet = wb.active

    xlsx_themes = []
    for row in sheet.iter_rows(min_row=2, max_col=5, values_only=True):
        cell_value = row[4]
        if cell_value is not None:
            xlsx_themes.append(cell_value)

    with open('thematics.txt', "r", encoding="utf8") as f:
        themes = f.readlines()

    res_with_zeros = count_phrases(delete_n(themes), xlsx_themes)
    res = remove_zeros(res_with_zeros)
    print(f'Количественная характеристика каждой тематики, полученная из Excel файла:\n', res)

    fig, ax = plt.subplots(figsize=(10, 7))

    total = sum(res.values())
    percentages = {key: value / total * 100 for key, value in res.items()}

    filtered_res = {k: v for k, v in res.items() if (v / total * 100) >= 2}
    filtered_percentages = {k: v / total * 100 for k, v in filtered_res.items()}

    wedges, texts, autotexts = ax.pie(
        filtered_res.values(),
        labels=None,
        autopct=lambda pct: f'{pct:.2f}%' if pct >= 2 else '',
        startangle=90,
        colors=random.choices(list(mplcolors.CSS4_COLORS.values()), k=len(filtered_res)),
        textprops={'fontsize': 6},
        pctdistance=0.85
    )

    # Устанавливаем подписи только для тематик >= 2%
    for i, wedge in enumerate(wedges):
        texts[i].set_text(list(filtered_res.keys())[i])

    for text in texts:
        text.set(size=6, horizontalalignment='center', verticalalignment='center')
    for autotext in autotexts:
        autotext.set(size=6)

    labels = [f'{l}: {s}' for l, s in zip(filtered_res.keys(), filtered_res.values())]
    ax.legend(labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8, ncol=2)

    ax.axis('equal')
    ax.set_title('Тематики групп', fontsize=14)
    plt.tight_layout()
    plt.show()



