import tkinter as tk
import sys
import vkinfo
import diagram
import cluster_first
import cluster_second
import cluster_third
import threading

class ConsoleOutput:
    def __init__(self, master):
        self.master = master
        master.title("Console Output")

        self.text_area = tk.Text(master, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill="both")
        self.text_area.config(state=tk.DISABLED)

        self.old_stdout = sys.stdout
        sys.stdout = self

    def write(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def flush(self):
        pass

    def close(self):
        sys.stdout = self.old_stdout

def clear_console():
    console.text_area.config(state=tk.NORMAL)
    console.text_area.delete("1.0", tk.END)
    console.text_area.config(state=tk.DISABLED)


def set_buttons_state(state):
    for btn in buttons:
        btn.config(state=state)

def run_threaded(func, delay_after_finish=0):
    def wrapper():
        set_buttons_state(tk.DISABLED)
        try:
            print("Загрузка... Пожалуйста, подождите.\n")
            func()
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        finally:
            if delay_after_finish > 0:
                root.after(delay_after_finish, lambda: set_buttons_state(tk.NORMAL))
            else:
                set_buttons_state(tk.NORMAL)
    threading.Thread(target=wrapper).start()

def get_information():
    clear_console()
    run_threaded(vkinfo.get_info_login)

def get_diagram():
    clear_console()
    diagram.get_diagram()

def get_clusterization_one():
    clear_console()
    cluster_first.get_clusterization_one_params()

def get_clusterization_two():
    clear_console()
    cluster_second.get_clusterization_two_params()

def get_clusterization_three():
    clear_console()
    cluster_third.get_clusterization_three_params()

root = tk.Tk()
root.title("VK Info Calculator")

console = ConsoleOutput(root)

button5 = tk.Button(root, text="Получить данные", command=get_information)
button4 = tk.Button(root, text="Построить диаграмму", command=get_diagram)
button3 = tk.Button(root, text="Построить кластеры по интересам", command=get_clusterization_one)
button2 = tk.Button(root, text="Построить кластеры по тематикам популярных групп", command=get_clusterization_two)
button1 = tk.Button(root, text="Построить кластеры по часто встречаемым популярным группам", command=get_clusterization_three)

buttons = [button1, button2, button3, button4, button5]

button1.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5, ipady=5)
button2.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5, ipady=5)
button3.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5, ipady=5)
button4.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5, ipady=5)
button5.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5, ipady=5)

root.mainloop()

