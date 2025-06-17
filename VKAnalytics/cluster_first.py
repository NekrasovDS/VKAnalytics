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

def get_clusterization_one_params():
    # Получаем значения параметров из интерфейса
    def save_parameters():
        global cluster_count
        try:
            cluster_count = int(entry_cluster_count.get())

            messagebox.showinfo("Успех",
                                f"Параметры успешно сохранены!\nКластеры: {cluster_count}")
            window.destroy()
            get_clusterization_one()  # Запуск кластеризации с новыми параметрами
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите числовые значения.")

    # Создаем окно для ввода параметров
    window = tk.Tk()
    window.title("Параметры кластеризации")

    label_cluster_count = tk.Label(window, text="Количество кластеров:")
    label_cluster_count.pack(pady=5)
    entry_cluster_count = tk.Entry(window)
    entry_cluster_count.pack(pady=5)

    button_ok = tk.Button(window, text="Запустить", command=save_parameters)
    button_ok.pack(pady=20)

    window.mainloop()

def get_clusterization_one():

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
                if user:
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

        if user:
            user_data.append(user)

        return user_data


    user_data = process_user_data(df)

    directions = set()
    for user in user_data:
        directions.update(user['Направления'])

    direction_encoder = LabelEncoder()
    direction_encoder.fit(list(directions))


    def get_direction_embeddings(user):
        if not user['Направления']:
            return []
        return direction_encoder.transform(user['Направления']).tolist()

    def get_most_common_direction(user):
        if not user['Направления']:
            return None
        return Counter(user['Направления']).most_common(1)[0][0]


    for user in user_data:
        user['Direction_Embedding'] = get_direction_embeddings(user)
        user['Most_Common_Direction'] = get_most_common_direction(user)

    X = []
    filtered_users = []

    for user in user_data:
        if user['Most_Common_Direction'] is None:
            continue

        direction_embedding = np.mean(user['Direction_Embedding']) if user['Direction_Embedding'] else 0
        most_common_direction = direction_encoder.transform([user['Most_Common_Direction']])[0]

        X.append([direction_embedding, most_common_direction])
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

    print(f"\n✅ Ближайшие пользователи к центроидам:")
    for i, idx in enumerate(closest_user_indices):
        user = filtered_users[idx]

        coords = X[idx]
        formatted_coords = [f"{coord:.3f}" for coord in coords]
        print(f" - Центроид {i + 1}: {user['Имя']} {user['Фамилия']} — приближенная точка [{', '.join(formatted_coords)}]")

    ax.legend()

    ax.set_xlabel('Тематики и направления групп')
    ax.set_ylabel('Самое популярное направление для одного пользователя')
    ax.set_title('Кластерный анализ по интересам')

    labels = [f"{user['Имя']} {user['Фамилия']}" for user in filtered_users]


    def set_custom_style(sel):
        sel.annotation.set_fontsize(10)
        sel.annotation.set_bbox(dict(facecolor='lightyellow', edgecolor='black', boxstyle='round,pad=0.5'))
        sel.annotation.set_text(labels[sel.index])
        sel.annotation.set_color('black')
        sel.annotation.set_fontweight('bold')


    cursor = mplcursors.cursor(scatter, hover=True)
    cursor.connect("add", set_custom_style)

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
