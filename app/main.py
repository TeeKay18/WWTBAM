import pygame
import codecs
import tkinter as tk
from tkinter.font import Font
from app.colors import white, purple, green, orange, blue
from app.game import Game
from pathlib import Path
from PIL import Image, ImageTk

app_folder = Path("app")
times_new_roman = "Times New Roman"


def play(file_path: str) -> None:
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


def play_intro() -> None:
    play(str(app_folder / "music" / "intro.mp3"))


def resize_image(image: ImageTk.PhotoImage, width: int, height: int) -> ImageTk.PhotoImage:
    image = image.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)


def button_with_image(root: tk.Tk, img: ImageTk.PhotoImage) -> None:
    button = tk.Button(root, image=img, bd=0, bg=purple)
    button.image = img
    return button


def set_lifelines():
    graphics_folder = app_folder / "graphics"
    width, height = 46, 30

    lifelines_frame = tk.Frame(game_frame)

    fifty_image = Image.open(str(graphics_folder / "fifty.png"))
    fifty_image_resized = resize_image(fifty_image, width, height)
    fifty_button = button_with_image(lifelines_frame, fifty_image_resized)

    switch_image = Image.open(str(graphics_folder / "switch.png"))
    switch_image_resized = resize_image(switch_image, width, height)
    switch_button = button_with_image(lifelines_frame, switch_image_resized)

    doubledip_image = Image.open(str(graphics_folder / "doubledip.png"))
    doubledip_image_resized = resize_image(doubledip_image, width, height)
    doubledip_button = button_with_image(lifelines_frame, doubledip_image_resized)

    lifelines_frame.grid(row=0, column=0)

    fifty_button.grid(row=0, column=0)
    switch_button.grid(row=0, column=1)
    doubledip_button.grid(row=0, column=2)


def tree_listbox(root: tk.Frame, wdth: int, num_questions: int) -> tk.Listbox:
    tree_font = Font(family=times_new_roman, size=18)
    return tk.Listbox(root, height=num_questions,
                      bg=purple, fg=white,
                      width=wdth, font=tree_font,
                      bd=0, highlightthickness=0)


def parse_tree():
    tree_frame = tk.Frame(game_frame)

    with codecs.open(str(app_folder / "config.txt"), "r", "utf-8") as file:
        data = file.read()
        parsed_data = data.splitlines()

        currency = parsed_data[0]
        prices = parsed_data[1:len(parsed_data)-1]
        num_questions = len(prices)
        guaranteed_questions = parsed_data[len(parsed_data)-1].split(sep=" ")
        guaranteed_questions = [int(num) for num in guaranteed_questions] + [num_questions]

        prices_lst = tree_listbox(tree_frame, 9, num_questions)
        no_question_lst = tree_listbox(tree_frame, 2, num_questions)
        current_question_lst = tree_listbox(tree_frame, 1, num_questions)

        for i in range(len(prices)):
            end = "end"
            prices_lst.insert(end, prices[i] + " " + currency)
            no_question_lst.insert(end, num_questions-i)
            current_question_lst.insert(end, " ")
        for num in guaranteed_questions:
            prices_lst.itemconfig(num_questions-num, fg=green)
            no_question_lst.itemconfig(num_questions-num, fg=green)
        tree_frame.grid(row=1, column=0)

        no_question_lst.grid(row=0, column=0)
        current_question_lst.grid(row=0, column=1)
        prices_lst.grid(row=0, column=2)

        prices_lst.configure(justify="right")
        no_question_lst.configure(justify="right")
        prices_lst.bindtags((prices_lst, tree_frame, "all"))
        current_question_lst.bindtags((current_question_lst, tree_frame, "all"))
        no_question_lst.bindtags((no_question_lst, tree_frame, "all"))

    return guaranteed_questions


def set_game_button():
    button_font = Font(family=times_new_roman, size=18)
    button_frame = tk.Frame(game_frame)
    game_button = tk.Button(button_frame, bg=orange, fg=white,
                            text="Nowa gra", font=button_font, padx=17,
                            command=lets_play)
    button_frame.grid(row=2, column=0)
    game_button.grid(row=0, column=0)


def set_question_box() -> None:
    question_font = Font(family=times_new_roman, size=16)
    question_text = tk.Text(question_frame, height=2, font=question_font,
                            bg=purple, fg=white, width=56, wrap="word")
    question_text.grid(row=0, column=0, padx=14, pady=12)


def answer_text(root: tk.Frame, fnt: Font) -> tk.Text:
    return tk.Text(root, height=1, font=fnt,
                   bg=purple, fg=white, width=34)


def set_answer_boxes():
    answer_font = Font(family=times_new_roman, size=12)
    answers_frame = tk.Frame(question_frame, bg=blue)
    answer_A = answer_text(answers_frame, answer_font)
    answer_B = answer_text(answers_frame, answer_font)
    answer_C = answer_text(answers_frame, answer_font)
    answer_D = answer_text(answers_frame, answer_font)   
    answer_A.grid(row=0, column=0, padx=10, pady=12)
    answer_B.grid(row=0, column=1)
    answer_C.grid(row=1, column=0)
    answer_D.grid(row=1, column=1)
    answers_frame.grid(row=1, column=0)


def lets_play():
    game = Game(guaranteed_questions)
    print(game)


if __name__ == "__main__":
    gui = tk.Tk(className='Milionerzy')
    gui.geometry("800x500")
    gui.configure(bg=blue)

    pygame.init()

    game_frame = tk.Frame(gui)
    question_frame = tk.Frame(gui, bg=blue)

    game_frame.grid(row=0, column=0)
    question_frame.grid(row=0, column=1)

    play_intro()
    set_lifelines()
    guaranteed_questions = parse_tree()
    set_game_button()
    set_question_box()
    set_answer_boxes()
    gui.mainloop()
