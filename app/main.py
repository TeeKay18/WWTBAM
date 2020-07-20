import codecs
import pygame
import random
import threading
import tkinter as tk

from pathlib import Path
from PIL import Image, ImageTk
from time import sleep
from tkinter.font import Font
from typing import List, Callable

from app.colors import white, purple, green, orange, blue, black
from app.game import Game


app_folder = Path("app")
times_new_roman = "Times New Roman"
graphics_folder = app_folder / "graphics"
lifelines_width, lifelines_height = 50, 30


def play(file_path: Path) -> None:
    pygame.mixer.music.load(str(file_path))
    pygame.mixer.music.play()


def stop_music() -> None:
    pygame.mixer.music.stop()


def play_intro() -> None:
    play(app_folder / "music" / "intro.mp3")


def resize_image(image: ImageTk.PhotoImage, width: int, height: int) -> ImageTk.PhotoImage:
    image = image.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)


def button_with_image(root: tk.Tk, img: ImageTk.PhotoImage, func: Callable, new_name: str) -> None:
    button = tk.Button(root, image=img, bd=0, bg=purple, command=func, name=new_name)
    button.image = img
    return button


def set_lifelines() -> None:
    lifelines_frame = tk.Frame(game_frame, name="lifelines_frame")

    fifty_image = Image.open(str(graphics_folder / "fifty.png"))
    fifty_image_resized = resize_image(fifty_image, lifelines_width, lifelines_height)
    fifty_button = button_with_image(lifelines_frame, fifty_image_resized,
                                     thread_fifty, "fifty_button")

    switch_image = Image.open(str(graphics_folder / "switch.png"))
    switch_image_resized = resize_image(switch_image, lifelines_width, lifelines_height)
    switch_button = button_with_image(lifelines_frame, switch_image_resized,
                                      thread_switch, "switch_button")

    doubledip_image = Image.open(str(graphics_folder / "doubledip.png"))
    doubledip_image_resized = resize_image(doubledip_image, lifelines_width, lifelines_height)
    doubledip_button = button_with_image(lifelines_frame, doubledip_image_resized,
                                         None, "doubledip_button")
    lifelines_frame.grid(row=0, column=0)

    fifty_button.grid(row=0, column=0)
    switch_button.grid(row=0, column=1)
    doubledip_button.grid(row=0, column=2)


def tree_listbox(root: tk.Frame, wdth: int, num_questions: int, new_name: str) -> tk.Listbox:
    tree_font = Font(family=times_new_roman, size=18)
    return tk.Listbox(root, height=num_questions,
                      bg=purple, fg=white,
                      width=wdth, font=tree_font,
                      bd=0, highlightthickness=0,
                      name=new_name)


def update_game_tree(no_question: int) -> None:
    localization = ".game_frame.tree_frame.current_question_lst"
    gui.nametowidget(localization).delete(num_questions-no_question, num_questions-no_question)
    gui.nametowidget(localization).insert(num_questions-no_question, " •")


def parse_tree() -> List[int]:
    tree_frame = tk.Frame(game_frame, name="tree_frame")

    with codecs.open(str(app_folder / "config.txt"), "r", "utf-8") as file:
        data = file.read()
        parsed_data = data.splitlines()

        currency = parsed_data[0]
        prices = parsed_data[1:-1]
        num_questions = len(prices)
        guaranteed_questions = parsed_data[-1].split(sep=" ")
        guaranteed_questions = [int(num) for num in guaranteed_questions] + [num_questions]

        prices_lst = tree_listbox(tree_frame, 9, num_questions, "prices_lst")
        no_question_lst = tree_listbox(tree_frame, 2, num_questions, "no_question_lst")
        current_question_lst = tree_listbox(tree_frame, 2, num_questions, "current_question_lst")

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

        # This makes sure that tree is read-only
        read_only = tree_frame, "all"
        prices_lst.bindtags((prices_lst, read_only))
        current_question_lst.bindtags((current_question_lst, read_only))
        no_question_lst.bindtags((no_question_lst, read_only))

    return guaranteed_questions


def set_game_button() -> None:
    button_font = Font(family=times_new_roman, size=18)
    button_frame = tk.Frame(game_frame, name="button_frame")
    game_button = tk.Button(button_frame, bg=orange, fg=white,
                            text="Nowa gra", font=button_font, padx=23,
                            command=start_thread_lets_play, name="game_button")
    button_frame.grid(row=2, column=0)
    game_button.grid(row=0, column=0)


def set_question_box() -> None:
    question_font = Font(family=times_new_roman, size=16)
    question_text = tk.Text(question_frame, height=2, font=question_font,
                            bg=purple, fg=white, width=57, wrap="word",
                            name="question_text", state="disabled")
    question_text.grid(row=0, column=0, padx=14, pady=12)


def answer_text(root: tk.Frame, fnt: Font, new_name: str) -> tk.Text:
    return tk.Text(root, height=1, font=fnt,
                   bg=purple, fg=white, width=34,
                   name=new_name, state="disabled")


def set_widget_color(widget: tk.Text, color: str) -> None:
    widget.configure(state="normal")
    widget.configure(bg=color)
    widget.configure(state="disabled")


def confirm_final_answer(widget: tk.Text) -> None:
    set_widget_color(widget, orange)


def show_correct_answer(widget: tk.Text) -> None:
    set_widget_color(widget, green)


def clear_question_and_answer_boxes():
    question_localization = ".question_frame.question_text"
    answers_localization = ".question_frame.answers_frame.answer_"
    answers = ["A", "B", "C", "D"]
    gui.nametowidget(question_localization).config(state="normal")
    gui.nametowidget(question_localization).delete("1.0", "end")
    gui.nametowidget(question_localization).config(state="disabled")
    for letter in answers:
        gui.nametowidget(answers_localization + letter).config(state="normal", bg=purple)
        gui.nametowidget(answers_localization + letter).delete("1.0", "end")
        gui.nametowidget(answers_localization + letter).config(state="disabled")


def green_answer(answers: List[str], localization: str):
    for answer in answers:
        ans_widget = gui.nametowidget(localization + answer)
        ans_text = ans_widget.get("1.0", "end-1c")
        if game.answer_correct(ans_text, game.current_question):
            show_correct_answer(ans_widget)


def verify_correct_answer(game: Game, user_answer: str,
                          answers: List[str], localization: str) -> None:
    green_answer(answers, localization)
    if game.answer_correct(user_answer, game.current_question):
        play(game.get_music_for_question()[3])
        time_next_question = 0
        if game.question_number < game.guaranteed_questions[0]:
            time_next_question = 1500
        elif game.question_number == game.guaranteed_questions[0]:
            time_next_question = 8000
        elif game.question_number < game.guaranteed_questions[1]:
            time_next_question = 4000
        elif game.question_number == game.guaranteed_questions[1]:
            time_next_question = 9000
        else:
            time_next_question = 6500
        game.question_number += 1
        gui.after(time_next_question, lambda: start_thread_lets_play())
    else:
        play(game.get_music_for_question()[4])
        gui.after(3500, lambda: clear_question_and_answer_boxes())
        game.game_on = False
        reset_new_game_button()

    game.question_answered = False
    game.question_shown = False


def check_answer_correct(button_name: str, game: Game) -> None:
    localization = ".question_frame.answers_frame.answer_"
    if game.game_on and game.question_shown and not game.question_answered:
        game.question_answered = True
        letter = button_name[-1]
        answer_widget = gui.nametowidget(localization + letter)

        confirm_final_answer(answer_widget)
        final_ans_sound = game.get_music_for_question()[2]
        if final_ans_sound is not None:
            play(final_ans_sound)

        user_answer = answer_widget.get("1.0", "end-1c")

        answers = ["A", "B", "C", "D"]
        time_verification = 0
        if game.question_number < game.guaranteed_questions[0]:
            time_verification = 500
        elif game.question_number == game.guaranteed_questions[0]:
            time_verification = 1500
        elif game.question_number < game.guaranteed_questions[1]:
            time_verification = 4500
        elif game.question_number == game.guaranteed_questions[2]:
            time_verification = 6000
        else:
            time_verification = 7000
        gui.after(time_verification, lambda: verify_correct_answer(game, user_answer,
                                                                   answers, localization))


def answer_button(root: tk.Frame, new_name: str, game: Game) -> tk.Button:
    button_font = Font(family=times_new_roman, size=12)
    letter = new_name[-1]
    return tk.Button(root, name=new_name, bg=black, fg=white,
                     font=button_font, width=3, height=1,
                     text=letter, command=lambda: check_answer_correct(new_name, game))


def set_answer_boxes(game: Game) -> None:
    answer_font = Font(family=times_new_roman, size=12)
    answers_frame = tk.Frame(question_frame, bg=blue, name="answers_frame")
    answer_A = answer_text(answers_frame, answer_font, "answer_A")
    answer_B = answer_text(answers_frame, answer_font, "answer_B")
    answer_C = answer_text(answers_frame, answer_font, "answer_C")
    answer_D = answer_text(answers_frame, answer_font, "answer_D")

    button_A = answer_button(answers_frame, "button_A", game)
    button_B = answer_button(answers_frame, "button_B", game)
    button_C = answer_button(answers_frame, "button_C", game)
    button_D = answer_button(answers_frame, "button_D", game)

    button_A.grid(row=0, column=0)
    answer_A.grid(row=0, column=1)
    button_B.grid(row=0, column=2)
    answer_B.grid(row=0, column=3)
    button_C.grid(row=1, column=0)
    answer_C.grid(row=1, column=1)
    button_D.grid(row=1, column=2)
    answer_D.grid(row=1, column=3)
    answers_frame.grid(row=1, column=0)


def reset_new_game_button():
    localization = ".game_frame.button_frame.game_button"
    gui.nametowidget(localization).config(text="Nowa gra", padx=23, command=start_thread_lets_play)


def set_walkaway_button():
    localization = ".game_frame.button_frame.game_button"
    gui.nametowidget(localization).config(text="Rezygnuję", padx=19, command=thread_on_walkaway)


def thread_on_walkaway() -> None:
    thread = threading.Thread(target=on_walkaway)
    thread.daemon = True
    thread.start()


def on_walkaway() -> None:
    if game.question_shown:
        localization = ".question_frame.answers_frame.answer_"
        game.game_on = False
        stop_music()
        answers = ["A", "B", "C", "D"]
        green_answer(answers, localization)
        gui.after(4000, lambda: clear_question_and_answer_boxes())
        reset_new_game_button()


def reset_lifeline_graphics() -> None:
    lifelines_localization = ".game_frame.lifelines_frame."
    lifeline_names = ["switch", "doubledip", "fifty"]
    button = "_button"
    for lifeline in lifeline_names:
        change_button_image(lifelines_localization + lifeline + button, lifeline + ".png")


def setup_new_game() -> None:
    set_walkaway_button()
    reset_pointers()
    game.question_number = 1
    game.question_shown = False
    game.get_questions()
    reset_lifeline_graphics()
    game.reset_lifelines()


def start_thread_lets_play():
    if not game.game_on:
        setup_new_game()
    game.question_shown = False
    thread = threading.Thread(target=lets_play)
    thread.daemon = True
    thread.start()


def insert_text(textbox: tk.Text, text: str) -> None:
    textbox.configure(state="normal")
    textbox.insert("end", text)
    textbox.configure(state="disabled")


def write_answer(question: list, indices: list, stop: int, end: int, answer_str: str) -> None:
    localization = ".question_frame.answers_frame."
    answer_index = random.choice(indices)
    indices.remove(answer_index)
    answer_widget = gui.nametowidget(localization + answer_str)
    insert_text(answer_widget, question[answer_index])


def confirm_question_shown():
    game.question_shown = True


def write_question(question: list) -> None:
    game.question_shown = False
    question_widget = gui.nametowidget(".question_frame.question_text")
    gui.after(500, lambda: insert_text(question_widget, question[1]))
    indices = [i for i in range(2, 6)]
    answer_step = 1000
    # cannot loop on that
    gui.after(answer_step, lambda: write_answer(question, indices, 2, 5, "answer_A"))
    gui.after(answer_step*2, lambda: write_answer(question, indices, 2, 5, "answer_B"))
    gui.after(answer_step*3, lambda: write_answer(question, indices, 2, 5, "answer_C"))
    gui.after(answer_step*4, lambda: write_answer(question, indices, 2, 5, "answer_D"))
    gui.after(int(answer_step*4.5), lambda: confirm_question_shown())


def next_question():
    clear_question_and_answer_boxes()
    music = game.get_music_for_question()
    if music[0] is not None:
        play(music[0])
        sleep(5)
    play(music[1])
    question = game.choose_random_question()
    write_question(question)


def lets_play():
    clear_question_and_answer_boxes()
    game.question_shown = False
    game_pointer = game.question_number-1
    if game_pointer > 0:
        update_game_tree(game.question_number-1)
    game.game_on = True
    if game.game_on:
        next_question()


def reset_pointers() -> None:
    localization = ".game_frame.tree_frame.current_question_lst"
    gui.nametowidget(localization).delete(1, num_questions)
    for i in range(num_questions):
        gui.nametowidget(localization).insert(i, " ")


def thread_switch() -> None:
    thread = threading.Thread(target=switch_the_question)
    thread.daemon = True
    thread.start()


def change_button_image(localization: str, image_path: str) -> None:
    image = Image.open(str(graphics_folder / image_path))
    image_resized = resize_image(image, lifelines_width, lifelines_height)
    button = gui.nametowidget(localization)
    button.config(image=image_resized)
    button.image = image_resized


def switch_the_question() -> None:
    if game.game_on and game.question_shown and not game.switch:
        switch_localization = ".game_frame.lifelines_frame.switch_button"
        change_button_image(switch_localization, "switchactivated.png")
        play(game.lifeline_themes[-1])
        answers = ["A", "B", "C", "D"]
        answers_localization = ".question_frame.answers_frame.answer_"
        gui.after(2000, lambda: green_answer(answers, answers_localization))
        gui.after(5000, lambda: clear_question_and_answer_boxes())
        music = game.get_music_for_question()
        gui.after(6000, lambda: play(music[1]))
        gui.after(6500, lambda: change_button_image(switch_localization, "switchused.png"))
        gui.after(7000, lambda: write_question(game.lifeline_switch()))


def thread_fifty() -> None:
    thread = threading.Thread(target=fifty_fifty)
    thread.daemon = True
    thread.start()


def fifty_fifty() -> None:
    if game.game_on and game.question_shown and not game.fifty_fifty:
        fifty_localization = ".game_frame.lifelines_frame.fifty_button"
        change_button_image(fifty_localization, "fiftyused.png")
        random_wrong_answers = game.lifeline_fifty_fifty(game.current_question)
        answers_localization = ".question_frame.answers_frame.answer_"
        answers = ["A", "B", "C", "D"]
        play(game.lifeline_themes[0])
        for answer in answers:
            answer_text = gui.nametowidget(answers_localization + answer)
            if answer_text.get("1.0", "end-1c") in random_wrong_answers:
                answer_text.config(state="normal")
                answer_text.delete("1.0", "end")
                answer_text.config(state="disabled")
        music = game.get_music_for_question()
        gui.after(1000, lambda: play(music[1]))


if __name__ == "__main__":
    gui = tk.Tk(className='Milionerzy')
    gui.geometry("820x500")
    gui.configure(bg=blue)

    pygame.init()

    game_frame = tk.Frame(gui, name="game_frame")
    question_frame = tk.Frame(gui, bg=blue, name="question_frame")

    game_frame.grid(row=0, column=0)
    question_frame.grid(row=0, column=1)

    play_intro()
    set_lifelines()
    guaranteed_questions = parse_tree()
    num_questions = guaranteed_questions[-1]
    game = Game(guaranteed_questions)
    game.get_questions()
    set_game_button()
    set_question_box()
    set_answer_boxes(game)
    gui.mainloop()
