from typing import List
from pathlib import Path


class Game:

    def __init__(self, guaranteed_questions: List[int]):
        self.question_number = 1
        self.fifty_fifty = True
        self.switch = True
        self.double_dip = True
        self.guaranteed_sum = 0

        self.questions_path = Path("app") / "config.txt"
        self.music_path = Path("app") / "music"

        self.common_symbols = ["q" + str(i) for i in range(5, 16)]
        self.common_symbols_two = ["q1-5", "q6-11", "q7-12", "q8-13", "q9-14"]

        self.question_theme_symbols = ["q1-5"] + self.common_symbols[1:]
        self.question_themes = [self.music_path / (symbol + "music.mp3")
                                for symbol in self.question_theme_symbols]

        self.correct_ans_symbols = ["q1-4"] + self.common_symbols
        self.correct_ans_themes = [self.music_path / (symbol + "correct.mp3")
                                   for symbol in self.correct_ans_symbols]

        self.wrong_ans_symbols = self.common_symbols_two + ["q15"]
        self.wrong_ans_themes = [self.music_path / (symbol + "wrong.mp3")
                                 for symbol in self.wrong_ans_symbols]

        self.lets_play_symbols = self.common_symbols_two + ["q10-15"]
        self.lets_play_symbols.remove("q6-11")
        self.lets_play_symbols.insert(1, "q6")
        self.lets_play_symbols.insert(2, "q11")
        self.lets_play_themes = [self.music_path / (symbol + "letsplay.mp3")
                                 for symbol in self.lets_play_symbols]

        self.lifeline_themes = [self.music_path / "50-50.mp3",
                                self.music_path / "doubledip1ans.mp3",
                                self.music_path / "doubledip1guess.mp3",
                                self.music_path / "doubledip2ans.mp3",
                                self.music_path / "doubledip2guess.mp3",
                                self.music_path / "switchthequestion.mp3"]
