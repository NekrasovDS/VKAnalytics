import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import mplcursors
from collections import Counter
import tkinter as tk
from tkinter import messagebox

def get_clusterization_three_params():
    # Получаем значения параметров из интерфейса
    def save_parameters():
        global cluster_count, group_count
        try:
            cluster_count = int(entry_cluster_count.get())
            group_count = int(entry_group_count.get())

            messagebox.showinfo("Успех",
                                f"Параметры успешно сохранены!\nКластеры: {cluster_count}\nГруппы: {group_count}")
            window.destroy()
            get_clusterization_three()  # Запуск кластеризации с новыми параметрами
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите числовые значения.")

    # Создаем окно для ввода параметров
    window = tk.Tk()
    window.title("Параметры кластеризации")

    label_cluster_count = tk.Label(window, text="Количество кластеров:")
    label_cluster_count.pack(pady=5)
    entry_cluster_count = tk.Entry(window)
    entry_cluster_count.pack(pady=5)

    label_group_count = tk.Label(window, text="Количество групп:")
    label_group_count.pack(pady=5)
    entry_group_count = tk.Entry(window)
    entry_group_count.pack(pady=5)

    button_ok = tk.Button(window, text="Запустить", command=save_parameters)
    button_ok.pack(pady=20)

    window.mainloop()


def get_clusterization_three():
    try:
        df = pd.read_excel('user_database_1.xlsx')
    except FileNotFoundError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Ошибка", "Файл 'user_database_1.xlsx' не найден!")
        return

    def process_user_data(df):
        user_data = []
        user = {}

        for index, row in df.iterrows():
            if pd.notna(row['Имя']):
                if user and user['Группы']:
                    user_data.append(user)
                user = {
                    'Имя': row['Имя'],
                    'Фамилия': row['Фамилия'],
                    'Id': row['Id пользователя'],
                    'Группы': [],
                    'Направление': []
                }

            if pd.notna(row['Id группы']):
                user['Группы'].append(row['Id группы'])
            if pd.notna(row['Направление']):
                user['Направление'].append(row['Направление'])

        if user and user['Группы']:
            user_data.append(user)

        return user_data

    user_data = process_user_data(df)

    group_theme_map = {}
    for index, row in df.iterrows():
        group_id = row.get('Id группы')
        theme = row.get('Направление')
        if pd.notna(group_id) and pd.notna(theme):
            group_theme_map[group_id] = theme

    directions = set()
    for user in user_data:
        directions.update(user['Направление'])

    direction_encoder = LabelEncoder()
    direction_encoder.fit(list(directions))

    for user in user_data:
        user['Direction_Embedding'] = direction_encoder.transform(user['Направление']).tolist()

    group_counter = Counter()
    for user in user_data:
        group_counter.update(user['Группы'])

    popular_groups = [group for group, _ in group_counter.most_common(group_count)]

    print(f"\n✅ ТОП {group_count} самых популярных групп и их тематика:")
    for group_id in popular_groups:
        theme = group_theme_map.get(group_id, "Нет данных")
        result_counter = group_counter[group_id]
        print(f"Группа ID: {int(group_id)} | Тематика: {theme} | Количество встреченных: {result_counter}")

    def get_popular_group_directions(user):
        user_groups = set(user['Группы'])
        directions = []
        for group in user_groups:
            if group in popular_groups:
                theme = group_theme_map.get(group)
                if theme:
                    directions.append(theme)
        return list(set(directions))

    for user in user_data:
        user['Popular_Group_Directions'] = get_popular_group_directions(user)

    # Новый: LabelEncoder для групп
    group_encoder = LabelEncoder()
    group_encoder.fit(list(group_counter.keys()))

    def get_cluster_feature_vector(user):
        popular_group_ids = [group for group in user['Группы'] if group in popular_groups]
        if popular_group_ids:
            encoded_groups = group_encoder.transform(popular_group_ids)
            group_ids_embedding = np.mean(encoded_groups)
        else:
            group_ids_embedding = 0

        direction_embedding = np.mean(user['Direction_Embedding']) if user['Direction_Embedding'] else 0

        return [group_ids_embedding, direction_embedding]

    X = []
    filtered_users = []

    for user in user_data:
        if not user['Группы']:
            continue

        feature_vector = get_cluster_feature_vector(user)
        X.append(feature_vector)
        filtered_users.append(user)

    X = np.array(X)

    if len(X) == 0:
        print("Недостаточно данных для кластеризации.")
        return

    kmeans = KMeans(n_clusters=cluster_count, random_state=42)
    kmeans.fit(X)
    user_clusters = kmeans.predict(X)

    for i, user in enumerate(filtered_users):
        user['Cluster'] = user_clusters[i]

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(X[:, 0], X[:, 1], c=user_clusters, cmap='viridis')

    # Отображение центроидов
    centroids = kmeans.cluster_centers_
    ax.scatter(centroids[:, 0], centroids[:, 1],
               marker='X', s=50, c='black', label='Центроиды')

    ax.legend()

    plt.xlabel('Самое популярное направление для одного пользователя')
    plt.ylabel('Тематики самых популярных групп')
    plt.title('Кластерный анализ по часто встречаемым популярным группам')

    labels = [f"{user['Имя']} {user['Фамилия']}" for user in filtered_users]
    mplcursors.cursor(scatter, hover=True).connect(
        "add", lambda sel: sel.annotation.set_text(labels[sel.index])
    )

    plt.colorbar(scatter)

    # Тестовый вывод
    cluster_dict = {}
    for user in filtered_users:
        cluster = user['Cluster']
        full_name = f"{user['Имя']} {user['Фамилия']}"
        cluster_dict.setdefault(cluster, []).append(full_name)

    print("\n✅ Результаты кластеризации:")
    for cluster, users in cluster_dict.items():
        print(f"\n➡️ Кластер {cluster + 1} | Количество людей в кластере {len(users)}:")
        for name in users:
            print(f" - {name}")

    plt.show()