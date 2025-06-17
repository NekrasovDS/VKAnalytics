import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import mplcursors
from collections import Counter
import tkinter as tk
from tkinter import messagebox
from scipy.spatial.distance import cdist

def get_clusterization_two_params():
    # Получаем значения параметров из интерфейса
    def save_parameters():
        global cluster_count, group_count
        try:
            cluster_count = int(entry_cluster_count.get())
            group_count = int(entry_group_count.get())

            messagebox.showinfo("Успех",
                                f"Параметры успешно сохранены!\nКластеры: {cluster_count}\nГруппы: {group_count}")
            window.destroy()
            get_clusterization_two()
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

def get_clusterization_two():
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
                    'Направления': []
                }

            if pd.notna(row['Id группы']):
                user['Группы'].append(row['Id группы'])
            if pd.notna(row['Направление']):
                user['Направления'].append(row['Направление'])

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
        directions.update(user['Направления'])

    direction_encoder = LabelEncoder()
    direction_encoder.fit(list(directions))

    def get_direction_embeddings(user):
        return direction_encoder.transform(user['Направления']).tolist()

    for user in user_data:
        user['Direction_Embedding'] = get_direction_embeddings(user)

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

    def get_direction_embedding_for_popular_groups(user):
        if user['Popular_Group_Directions']:
            return np.mean(direction_encoder.transform(user['Popular_Group_Directions']), axis=0)
        else:
            return 0

    X = []
    filtered_users = []

    for user in user_data:
        if not user['Группы']:
            continue

        popular_group_direction_embedding = get_direction_embedding_for_popular_groups(user)
        direction_embedding = np.mean(user['Direction_Embedding']) if user['Direction_Embedding'] else 0

        X.append([popular_group_direction_embedding, direction_embedding])
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

    centroids = kmeans.cluster_centers_

    # Найдём индексы ближайших пользователей к центроидам
    closest_user_indices = []
    distances = cdist(X, centroids)
    for i in range(len(centroids)):
        closest_idx = np.argmin(distances[:, i])
        closest_user_indices.append(closest_idx)

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(X[:, 0], X[:, 1], c=user_clusters, cmap='viridis')

    # Отрисовка центроидов
    ax.scatter(centroids[:, 0], centroids[:, 1], marker='X', s=50, c='black', label='Центроиды')

    # Отметим ближайших пользователей к центроидам
    for idx in closest_user_indices:
        ax.scatter(X[idx, 0], X[idx, 1], s=200, facecolors='none', edgecolors='black', linewidths=2)
    ax.scatter([], [], s=200, facecolors='none', edgecolors='black', linewidths=2, label='Приближенные точки')

    print("\n✅ Ближайшие пользователи к центроидам:")
    for i, idx in enumerate(closest_user_indices):
        user = filtered_users[idx]

        coords = X[idx]
        formatted_coords = [f"{coord:.3f}" for coord in coords]
        print(f" - Центроид {i + 1}: {user['Имя']} {user['Фамилия']} — приближенная точка [{', '.join(formatted_coords)}]")

    ax.legend()

    ax.set_xlabel('Тематики и направления групп')
    ax.set_ylabel('Тематики самых популярных групп')
    ax.set_title('Кластерный анализ по тематикам популярных групп')

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
        if cluster not in cluster_dict:
            cluster_dict[cluster] = []
        cluster_dict[cluster].append(full_name)
    print("\n✅ Результаты кластеризации:")
    for cluster, users in cluster_dict.items():
        print(f"\n➡️ Кластер {cluster + 1} | Количество людей в кластере {len(users)}:")
        for name in users:
            print(f" - {name}")
    plt.show()