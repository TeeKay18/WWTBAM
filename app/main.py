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

from app.colors import white, purple, green, orange, blue, black, red, dark_green
from app.game import Game


app_folder = Path("app")
times_new_roman = "Times New Roman"
graphics_folder = app_folder / "graphics"
lifelines_width, lifelines_height = 50, 30
answers = ["A", "B", "C", "D"]
answers_localization = ".question_frame.answers_frame.answer_"
lifelines_localization = ".game_frame.lifelines_frame."
fifty_localization = lifelines_localization + "fifty_button"
ddip_localization = lifelines_localization + "doubledip_button"
switch_localization = lifelines_localization + "switch_button"
curq_localization = ".game_frame.tree_frame.current_question_lst"
buttons_localization = ".question_frame.answers_frame.button_"
lifeline_names = ["switch", "doubledip", "fifty"]
walkaway_text = "Rezygnuję"
newgame_text = "Nowa gra"
answer_step = 1000

qfont_size = 16
gbutton_size = 18
tfont_size = 18
abutton_size = 12
afont_size = 12


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
                                         thread_ddip, "doubledip_button")
    lifelines_frame.grid(row=0, column=0)

    fifty_button.grid(row=0, column=0)
    switch_button.grid(row=0, column=1)
    doubledip_button.grid(row=0, column=2)


def tree_listbox(root: tk.Frame, wdth: int, num_questions: int, new_name: str) -> tk.Listbox:
    tree_font = Font(family=times_new_roman, size=tfont_size)
    return tk.Listbox(root, height=num_questions,
                      bg=purple, fg=white,
                      width=wdth, font=tree_font,
                      bd=0, highlightthickness=0,
                      name=new_name)


def get_widget(id: str) -> tk.Widget:
    return gui.nametowidget(id)


def update_game_tree(no_question: int) -> None:
    get_widget(curq_localization).delete(num_questions-no_question, num_questions-no_question)
    get_widget(curq_localization).insert(num_questions-no_question, " •")


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
    button_font = Font(family=times_new_roman, size=gbutton_size)
    button_frame = tk.Frame(game_frame, name="button_frame")
    game_button = tk.Button(button_frame, bg=orange, fg=white,
                            text=newgame_text, font=button_font, padx=23,
                            command=start_thread_lets_play, name="game_button")
    button_frame.grid(row=2, column=0)
    game_button.grid(row=0, column=0)


def set_question_box() -> None:
    question_font = Font(family=times_new_roman, size=qfont_size)
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


def first_wrong_answer(widget: tk.Text) -> None:
    set_widget_color(widget, red)


def confirm_final_answer(widget: tk.Text) -> None:
    set_widget_color(widget, orange)


def show_correct_answer(widget: tk.Text) -> None:
    set_widget_color(widget, dark_green)


def clear_text(widget: tk.Widget) -> None:
    widget.config(state="normal")
    widget.delete("1.0", "end")
    widget.config(state="disabled")


def clear_question_and_answer_boxes():
    question_localization = ".question_frame.question_text"
    clear_text(get_widget(question_localization))
    for letter in answers:
        ans_widget = get_widget(answers_localization + letter)
        clear_text(ans_widget)
        set_widget_color(ans_widget, purple)


def green_answer(answers: List[str], localization: str):
    for answer in answers:
        ans_widget = get_widget(localization + answer)
        ans_text = ans_widget.get("1.0", "end-1c")
        if game.answer_correct(ans_text, game.current_question):
            show_correct_answer(ans_widget)


def winning_sequence() -> None:
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


def losing_sequence():
    play(game.get_music_for_question()[4])
    gui.after(3500, lambda: clear_question_and_answer_boxes())
    game.game_on = False
    reset_new_game_button()


def verify_correct_answer(game: Game, user_answer: str,
                          answers: List[str], localization: str) -> None:
    green_answer(answers, localization)
    if game.answer_correct(user_answer, game.current_question):
        winning_sequence()
    else:
        losing_sequence()

    game.question_answered = False
    game.question_shown = False


def check_answer_correct_double_dip(button_name: str, game: Game) -> None:
    if game.game_on and game.question_shown and not game.question_answered:
        letter = button_name[-1]
        answer_widget = get_widget(answers_localization + letter)
        confirm_final_answer(answer_widget)
        final_ans_sound = game.lifeline_themes[2]
        play(final_ans_sound)
        user_answer = answer_widget.get("1.0", "end-1c")
        if game.answer_correct(user_answer, game.current_question):
            gui.after(3900, lambda: green_answer(answers, answers_localization))
            gui.after(4000, lambda: winning_sequence())
            gui.after(4000, lambda: change_button_image(ddip_localization, "doubledipused.png"))
        else:
            answer_text = get_widget(answers_localization + letter)
            gui.after(3900, lambda: first_wrong_answer(answer_text))
            gui.after(4000, lambda: play(game.lifeline_themes[3]))
        f = check_answer_correct
        get_widget(buttons_localization + "A").config(command=lambda: f("button_A", game))
        get_widget(buttons_localization + "B").config(command=lambda: f("button_B", game))
        get_widget(buttons_localization + "C").config(command=lambda: f("button_C", game))
        get_widget(buttons_localization + "D").config(command=lambda: f("button_D", game))


def check_answer_correct(button_name: str, game: Game) -> None:
    if game.game_on and game.question_shown and not game.question_answered:
        game.question_answered = True
        letter = button_name[-1]
        answer_widget = get_widget(answers_localization + letter)

        confirm_final_answer(answer_widget)
        final_ans_sound = game.get_music_for_question()[2]
        if game.double_dip == game.question_number:
            play(game.lifeline_themes[4])
            change_button_image(ddip_localization, "doubledipused.png")
        elif final_ans_sound is not None:
            play(final_ans_sound)

        user_answer = answer_widget.get("1.0", "end-1c")

        time_verification = 0
        if game.question_number < game.guaranteed_questions[0]:
            time_verification = 2000
        elif game.question_number == game.guaranteed_questions[0]:
            time_verification = 3000
        elif game.question_number < game.guaranteed_questions[1]:
            time_verification = 4500
        elif game.question_number == game.guaranteed_questions[2]:
            time_verification = 6000
        else:
            time_verification = 7000
        gui.after(time_verification, lambda: verify_correct_answer(game, user_answer,
                                                                   answers, answers_localization))


def answer_button(root: tk.Frame, new_name: str, game: Game) -> tk.Button:
    button_font = Font(family=times_new_roman, size=abutton_size)
    letter = new_name[-1]
    return tk.Button(root, name=new_name, bg=black, fg=white,
                     font=button_font, width=3, height=1,
                     text=letter, command=lambda: check_answer_correct(new_name, game))


def set_answer_boxes(game: Game) -> None:
    answer_font = Font(family=times_new_roman, size=afont_size)
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
    get_widget(localization).config(text=newgame_text, padx=23, command=start_thread_lets_play)


def set_walkaway_button():
    localization = ".game_frame.button_frame.game_button"
    get_widget(localization).config(text=walkaway_text, padx=19, command=thread_on_walkaway)


def thread_on_walkaway() -> None:
    create_thread(on_walkaway)


def on_walkaway() -> None:
    if game.question_shown and game.double_dip != game.question_number:
        game.game_on = False
        stop_music()
        green_answer(answers, answers_localization)
        gui.after(4000, lambda: clear_question_and_answer_boxes())
        reset_new_game_button()


def reset_lifeline_graphics() -> None:
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
    create_thread(lets_play)


def insert_text(textbox: tk.Text, text: str) -> None:
    textbox.configure(state="normal")
    textbox.insert("end", text)
    textbox.configure(state="disabled")


def write_answer(question: list, indices: list, stop: int, end: int, answer_str: str) -> None:
    localization = ".question_frame.answers_frame."
    answer_index = random.choice(indices)
    indices.remove(answer_index)
    answer_widget = get_widget(localization + answer_str)
    insert_text(answer_widget, question[answer_index])


def confirm_question_shown():
    game.question_shown = True


def write_question(question: list) -> None:
    game.question_shown = False
    question_widget = get_widget(".question_frame.question_text")
    gui.after(500, lambda: insert_text(question_widget, question[1]))
    indices = [i for i in range(2, 6)]
    # cannot loop on that
    gui.after(answer_step, lambda: write_answer(question, indices, 2, 5, "answer_A"))
    gui.after(answer_step*2, lambda: write_answer(question, indices, 2, 5, "answer_B"))
    gui.after(answer_step*3, lambda: write_answer(question, indices, 2, 5, "answer_C"))
    gui.after(answer_step*4, lambda: write_answer(question, indices, 2, 5, "answer_D"))
    gui.after(int(answer_step*4.5), lambda: confirm_question_shown())


def next_question():
    clear_question_and_answer_boxes()
    music = game.get_music_for_question()
    if music:
        if music[0] is not None:
            play(music[0])
            sleep(5)
        play(music[1])
        question = game.choose_random_question()
        write_question(question)
    else:
        game.game_on = False
        reset_new_game_button()


def lets_play():
    clear_question_and_answer_boxes()
    game.question_shown = False
    game_pointer = game.question_number-1
    if game_pointer > 0:
        update_game_tree(game.question_number-1)
    game.game_on = True
    next_question()


def reset_pointers() -> None:
    get_widget(curq_localization).delete(1, num_questions)
    for i in range(num_questions):
        get_widget(curq_localization).insert(i, " ")


def thread_switch() -> None:
    create_thread(switch_the_question)


def change_button_image(localization: str, image_path: str) -> None:
    image = Image.open(str(graphics_folder / image_path))
    image_resized = resize_image(image, lifelines_width, lifelines_height)
    button = get_widget(localization)
    button.config(image=image_resized)
    button.image = image_resized


def switch_the_question() -> None:
    if (game.game_on and game.question_shown and not game.switch
       and game.double_dip != game.question_number):
        game.switch = game.question_number
        change_button_image(switch_localization, "switchactivated.png")
        play(game.lifeline_themes[-1])
        gui.after(2000, lambda: green_answer(answers, answers_localization))
        gui.after(5000, lambda: clear_question_and_answer_boxes())
        music = game.get_music_for_question()
        gui.after(6000, lambda: play(music[1]))
        gui.after(6500, lambda: change_button_image(switch_localization, "switchused.png"))
        gui.after(7000, lambda: write_question(game.lifeline_switch()))


def thread_fifty() -> None:
    create_thread(fifty_fifty)


def fifty_fifty() -> None:
    if (game.game_on and game.question_shown and not game.fifty_fifty
       and game.double_dip != game.question_number):
        game.fifty_fifty = game.question_number
        change_button_image(fifty_localization, "fiftyused.png")
        random_wrong_answers = game.lifeline_fifty_fifty(game.current_question)
        play(game.lifeline_themes[0])
        for answer in answers:
            answer_text = get_widget(answers_localization + answer)
            if answer_text.get("1.0", "end-1c") in random_wrong_answers:
                clear_text(answer_text)
        music = game.get_music_for_question()
        gui.after(1000, lambda: play(music[1]))


def thread_ddip():
    create_thread(double_dip)


def create_thread(func: Callable) -> None:
    thread = threading.Thread(target=func)
    thread.daemon = True
    thread.start()


def double_dip():
    if (game.game_on and game.question_shown and not game.double_dip
       and game.fifty_fifty != game.question_number):
        game.double_dip = game.question_number
        change_button_image(ddip_localization, "doubledipactivated.png")
        play(game.lifeline_themes[1])
        buttons_localization = ".question_frame.answers_frame.button_"
        f = check_answer_correct_double_dip
        get_widget(buttons_localization + "A").config(command=lambda: f("button_A", game))
        get_widget(buttons_localization + "B").config(command=lambda: f("button_B", game))
        get_widget(buttons_localization + "C").config(command=lambda: f("button_C", game))
        get_widget(buttons_localization + "D").config(command=lambda: f("button_D", game))


if __name__ == "__main__":
    gui = tk.Tk(className='Milionerzy')
    gui.geometry("820x500")
    gui.configure(bg=blue)

    pygame.init()

    game_frame = tk.Frame(gui, name="game_frame", bg=purple)
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
