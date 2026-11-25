
import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
import uuid
import os
from pathlib import Path

import minecraft_launcher_lib

GAME_VERSION = "1.21.11"
APP_NAME = "RightVisuals"
GAME_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / ".rightvisuals"

BG = "#080B12"
PANEL = "#101725"
BLUE = "#2588FF"
WHITE = "#F2F6FF"
MUTED = "#8493AA"

root = tk.Tk()
root.title("RightVisuals Launcher")
root.geometry("1050x680")
root.minsize(900, 600)
root.configure(bg=BG)

username = tk.StringVar()
ram = tk.IntVar(value=4)
status = tk.StringVar(value="Добро пожаловать в RightVisuals")
busy = False


def label(parent, text, size, color=WHITE, bold=False):
    return tk.Label(
        parent,
        text=text,
        bg=parent["bg"],
        fg=color,
        font=("Segoe UI", size, "bold" if bold else "normal")
    )


def set_status(text):
    root.after(0, lambda: status.set(text))


def set_busy(value):
    global busy
    busy = value
    root.after(0, lambda: install_button.config(
        state="disabled" if value else "normal"
    ))
    root.after(0, lambda: play_button.config(
        state="disabled" if value else "normal"
    ))


def install_game():
    global busy
    if busy:
        return

    set_busy(True)
    set_status("Подготовка Minecraft и Fabric...")

    def task():
        try:
            GAME_DIR.mkdir(parents=True, exist_ok=True)

            fabric = minecraft_launcher_lib.mod_loader.get_mod_loader("fabric")

            if not fabric.is_minecraft_version_supported(GAME_VERSION):
                raise RuntimeError(
                    "Fabric пока не поддерживает Minecraft " + GAME_VERSION
                )

            set_status("Загрузка Minecraft и установка Fabric...")
            installed_version = fabric.install(
                GAME_VERSION,
                str(GAME_DIR)
            )

            set_status("Готово! Установлена версия " + installed_version)
            root.after(0, lambda: messagebox.showinfo(
                "RightVisuals",
                "Minecraft " + GAME_VERSION + " + Fabric установлены!"
            ))

        except Exception as error:
            set_status("Ошибка установки")
            root.after(0, lambda: messagebox.showerror(
                "Ошибка",
                str(error)
            ))
        finally:
            set_busy(False)

    threading.Thread(target=task, daemon=True).start()


def launch_game():
    global busy

    nick = username.get().strip()

    if not nick or len(nick) > 16:
        messagebox.showwarning(
            "RightVisuals",
            "Введи ник длиной от 1 до 16 символов."
        )
        return

    if not nick.replace("_", "").isalnum():
        messagebox.showwarning(
            "RightVisuals",
            "Используй только латинские буквы, цифры и _."
        )
        return

    if busy:
        return

    set_busy(True)
    set_status("Подготовка запуска...")

    def task():
        try:
            fabric = minecraft_launcher_lib.mod_loader.get_mod_loader("fabric")
            loader_version = fabric.get_latest_loader_version(GAME_VERSION)
            version_id = fabric.get_installed_version(
                GAME_VERSION,
                loader_version
            )

            options = {
                "username": nick,
                "uuid": uuid.uuid3(
                    uuid.NAMESPACE_DNS,
                    "OfflinePlayer:" + nick
                ).hex,
                "token": "0",
                "executablePath": "java",
                "jvmArguments": [
                    f"-Xmx{ram.get()}G",
                    "-Xms1G"
                ],
                "launcherName": "RightVisuals",
                "launcherVersion": "1.0"
            }

            command = minecraft_launcher_lib.command.get_minecraft_command(
                version_id,
                str(GAME_DIR),
                options
            )

            set_status("Запуск Minecraft...")
            subprocess.Popen(command, cwd=str(GAME_DIR))
            set_status("Minecraft запущен!")

        except FileNotFoundError:
            set_status("Не найдена Java")
            root.after(0, lambda: messagebox.showerror(
                "Java не найдена",
                "Для запуска Minecraft нужна совместимая Java 21. "
                "Добавим автоматическую настройку Java следующим этапом."
            ))
        except Exception as error:
            set_status("Не удалось запустить игру")
            root.after(0, lambda: messagebox.showerror(
                "Ошибка запуска",
                str(error)
            ))
        finally:
            set_busy(False)

    threading.Thread(target=task, daemon=True).start()


# Sidebar
sidebar = tk.Frame(root, bg="#0C111C", width=230)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

label(sidebar, "RIGHT", 27, BLUE, True).pack(
    anchor="w", padx=25, pady=(35, 0)
)
label(sidebar, "VISUALS", 27, WHITE, True).pack(
    anchor="w", padx=25
)
label(sidebar, "MINECRAFT LAUNCHER", 9, MUTED).pack(
    anchor="w", padx=26, pady=(4, 45)
)

for item in ["Главная", "Моды", "Профиль", "Настройки"]:
    tk.Label(
        sidebar,
        text="   " + item,
        bg="#0C111C",
        fg=WHITE if item == "Главная" else MUTED,
        font=("Segoe UI", 12),
        anchor="w",
        padx=20,
        pady=15
    ).pack(fill="x", padx=8)

label(sidebar, "RIGHTVISUALS © 2026", 9, MUTED).pack(
    side="bottom", pady=25
)

# Main content
main = tk.Frame(root, bg=BG)
main.pack(side="left", fill="both", expand=True, padx=45, pady=35)

label(main, "MINECRAFT JAVA EDITION", 11, BLUE, True).pack(anchor="w")
label(main, "ТВОЯ ИГРА. ТВОИ ПРАВИЛА.", 25, WHITE, True).pack(
    anchor="w", pady=(10, 5)
)
label(main, "Добро пожаловать в RightVisuals Launcher", 11, MUTED).pack(
    anchor="w"
)

hero = tk.Frame(main, bg=PANEL, height=230)
hero.pack(fill="x", pady=30)
hero.pack_propagate(False)

label(hero, "RIGHTVISUALS", 29, WHITE, True).pack(
    anchor="w", padx=30, pady=(35, 5)
)
label(hero, "PREMIUM EDITION", 11, BLUE, True).pack(
    anchor="w", padx=32
)
label(hero, "Minecraft 1.21.11  •  Fabric", 12, MUTED).pack(
    anchor="w", padx=32, pady=20
)

profile = tk.Frame(main, bg=BG)
profile.pack(fill="x", pady=(0, 18))

label(profile, "ИГРОВОЙ НИК", 10, MUTED, True).pack(anchor="w")
tk.Entry(
    profile,
    textvariable=username,
    bg=PANEL,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    font=("Segoe UI", 13),
    width=30
).pack(anchor="w", ipady=12, pady=8)

label(main, "ОПЕРАТИВНАЯ ПАМЯТЬ (RAM)", 10, MUTED, True).pack(
    anchor="w"
)

ram_scale = tk.Scale(
    main,
    from_=2,
    to=12,
    orient="horizontal",
    variable=ram,
    bg=BG,
    fg=WHITE,
    troughcolor=PANEL,
    highlightthickness=0,
    activebackground=BLUE,
    length=300
)
ram_scale.pack(anchor="w", pady=5)

buttons = tk.Frame(main, bg=BG)
buttons.pack(anchor="w", pady=20)

install_button = tk.Button(
    buttons,
    text="УСТАНОВИТЬ FABRIC",
    command=install_game,
    bg=PANEL,
    fg=WHITE,
    activebackground=BLUE,
    activeforeground=WHITE,
    relief="flat",
    font=("Segoe UI", 10, "bold"),
    padx=22,
    pady=15,
    cursor="hand2"
)
install_button.pack(side="left", padx=(0, 12))

play_button = tk.Button(
    buttons,
    text="▶  ИГРАТЬ",
    command=launch_game,
    bg=BLUE,
    fg=WHITE,
    activebackground="#176BD0",
    activeforeground=WHITE,
    relief="flat",
    font=("Segoe UI", 11, "bold"),
    padx=35,
    pady=15,
    cursor="hand2"
)
play_button.pack(side="left")

tk.Label(
    main,
    textvariable=status,
    bg=BG,
    fg=MUTED,
    font=("Segoe UI", 10)
).pack(anchor="w", pady=10)

root.mainloop()
