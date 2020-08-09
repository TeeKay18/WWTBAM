import codecs

from typing import List
from secrets import SystemRandom
from pathlib import Path
from app.crypto import decryption


class Game:

    def __init__(self, guaranteed_questions: List[int]):
        self.guaranteed_questions = guaranteed_questions
        self.question_number = 1
        self.game_on = False
        self.question_shown = False
        self.question_answered = False
        self.current_question = []
        self.fifty_fifty = 0
        self.switch = 0
        self.double_dip = 0
        self.guaranteed_sum = 0
        self.rng = SystemRandom()

        self.questions_path = Path("app") / "questions" / "questions.txt"
        self.music_path = Path("app") / "music"

        common_symbols = ["q" + str(i) for i in range(5, 16)]
        common_symbols_two = ["q1-5", "q6-11", "q7-12", "q8-13", "q9-14"]

        question_theme_symbols = ["q1-5"] + common_symbols[1:]
        question_themes = [self.music_path / (symbol + "music.mp3")
                           for symbol in question_theme_symbols]

        final_ans_symbols = common_symbols_two[1:] + ["q10-15"]
        final_ans_themes = [self.music_path / (symbol + "final.mp3")
                            for symbol in final_ans_symbols]

        correct_ans_symbols = ["q1-4"] + common_symbols
        correct_ans_themes = [self.music_path / (symbol + "correct.mp3")
                              for symbol in correct_ans_symbols]

        wrong_ans_symbols = common_symbols_two + ["q10"] + ["q15"]
        wrong_ans_themes = [self.music_path / (symbol + "wrong.mp3")
                            for symbol in wrong_ans_symbols]

        lets_play_symbols = common_symbols_two + ["q10-15"]
        lets_play_symbols.remove("q6-11")
        lets_play_symbols.insert(1, "q6")
        lets_play_symbols.append("q11")
        lets_play_themes = [self.music_path / (symbol + "letsplay.mp3")
                            for symbol in lets_play_symbols]

        self.lifeline_themes = [self.music_path / "50-50.mp3",
                                self.music_path / "doubledip1guess.mp3",
                                self.music_path / "doubledip1ans.mp3",
                                self.music_path / "doubledip2guess.mp3",
                                self.music_path / "doubledip2ans.mp3",
                                self.music_path / "switchthequestion.mp3"]

        fst_guaranteed = guaranteed_questions[0]
        snd_guaranteed = guaranteed_questions[1]
        victory = guaranteed_questions[2]

        lp_indices = [0] + [-1] * (fst_guaranteed-1) +\
                     [(i-fst_guaranteed+1) % 7 for i in range(fst_guaranteed, snd_guaranteed+1)] +\
                     [(i-snd_guaranteed+1) % 7 for i in range(snd_guaranteed+1, victory)]
        q_indices = [0] * (fst_guaranteed) + [(i-fst_guaranteed+1) % 11
                                              for i in range(fst_guaranteed, victory)]
        fa_indices = [-1] * (fst_guaranteed) + [(i-fst_guaranteed) % 5
                                                for i in range(fst_guaranteed, victory)]
        ca_indices = [0] * (fst_guaranteed-1) + [(i-fst_guaranteed+1) % 12
                                                 for i in range(fst_guaranteed, victory+1)]
        wa_indices = [0] * (fst_guaranteed) + [(i-fst_guaranteed+1) % 6
                                               for i in range(fst_guaranteed, snd_guaranteed)] +\
                                              [(i-snd_guaranteed+1) % 5
                                               for i in range(snd_guaranteed, victory-1)] + [6]

        self.music_settings = [[lets_play_themes[lp_indices[i]]
                                if lp_indices[i] >= 0 else None,
                                question_themes[q_indices[i]],
                                final_ans_themes[fa_indices[i]]
                                if fa_indices[i] >= 0 else None,
                                correct_ans_themes[ca_indices[i]],
                                wrong_ans_themes[wa_indices[i]]
                                ] for i in range(victory)
                               ]

    def _get_questions_file_content(self) -> str:
        with codecs.open(self.questions_path, "r", "utf-8") as questions_file:
            return decryption(questions_file.read().encode())
        return None

    def get_questions(self) -> None:
        questions_data = self._get_questions_file_content().splitlines()
        self._questions = [[int(questions_data[i]),
                            questions_data[i+1],
                            questions_data[i+2],
                            questions_data[i+3],
                            questions_data[i+4],
                            questions_data[i+5]]
                           for i in range(0, int(len(questions_data)), 6)]
        self._questions = sorted(self._questions, key=lambda x: x[0])

    def choose_random_question(self) -> list:
        q_split = int(len(self._questions) / self.guaranteed_questions[-1])
        minimum = (self.question_number-1) * q_split
        maximum = self.question_number * q_split
        if self.question_number == self.guaranteed_questions[-1]:
            maximum = len(self._questions)-1
        rand_index = self.rng.randrange(minimum, maximum)
        question = self._questions[rand_index]
        self._questions.remove(question)
        self.current_question = question
        return question

    def answer_correct(self, answer: str, question: list) -> bool:
        return answer == question[2]

    def lifeline_fifty_fifty(self, question: list) -> list:
        self.fifty_fifty = self.question_number
        fst_wrong_answer = question[self.rng.randrange(3, 5)]
        question.remove(fst_wrong_answer)
        snd_wrong_answer = question[self.rng.randrange(3, 4)]
        question.remove(snd_wrong_answer)
        return [fst_wrong_answer, snd_wrong_answer]

    def lifeline_switch(self):
        self.switch = self.question_number
        return self.choose_random_question()

    def get_music_for_question(self):
        if self.question_number != self.guaranteed_questions[-1]+1:
            return self.music_settings[self.question_number-1]
        return None

    def reset_lifelines(self):
        self.fifty_fifty = 0
        self.switch = 0
        self.double_dip = 0
