import copy
import random
from tkinter import *

import pandas as pd


class Game:
    # создание переменных класса, которые можно повторно использовать для каждой игры
    subscripts = [' ', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉', 'ₓ']
    letter_values = {" ": 0, "a": 1, "b": 3, "c": 3, "d": 2, "e": 1, "f": 4, "g": 2, "h": 4, "i": 1, "j": 8, "k": 5,
                     "l": 1, "m": 3, "n": 1, "o": 1, "p": 3, "q": 10, "r": 1, "s": 1, "t": 1, "u": 1, "v": 4, "w": 4,
                     "x": 8, "y": 4, "z": 10}
    inital_tiles = ['j', 'k', 'q', 'x', 'z', *(['b'] * 2), *(['c'] * 2), *(['f'] * 2), *(['h'] * 2), *(['m'] * 2),
                    *(['p'] * 2), *(['v'] * 2), *(['w'] * 2), *(['y'] * 2), *(['g'] * 3), *(['d'] * 4), *(['l'] * 4),
                    *(['s'] * 4), *(['u'] * 4), *(['n'] * 6), *(['r'] * 7), *(['t'] * 7), *(['o'] * 8), *(['a'] * 9),
                    *(['i'] * 9), *(['e'] * 12)]
    dic = open('dic.txt').read().split()
    dic_df = pd.DataFrame({'word': dic})
    global values
    values = letter_values
    # need to declare global copy of letter_values, as for some reason below line doesn't work otherwise
    dic_df['score'] = [sum([values[l] for l in word]) for word in dic_df['word']]
    large_dic = set(dic)
    # Расположение плиток, где значения букв или слов увеличиваются
    triple_word = {(0, 0), (0, 7), (0, 14), (7, 14), (14, 14)}
    triple_letter = {(5, 1), (9, 1), (9, 5), (5, 5), (13, 5), (9, 9), (13, 9)}
    double_word = {(1, 1), (2, 2), (3, 3), (4, 4), (13, 13), (12, 12), (11, 11), (10, 10), (13, 1), (12, 2), (11, 3),
                   (10, 4), (7, 7)}
    double_letter = {(0, 3), (2, 6), (3, 7), (2, 8), (3, 14), (11, 14), (7, 11), (6, 12), (8, 12), (6, 6), (8, 8),
                     (8, 6)}
    # константы
    DEFAULT_COLOR = 'MediumPurple' # цвета полей, где значения букв или слов увеличиваются
    TILE_COLOR = 'snow'
    TW_COLOR = 'navy'
    TL_COLOR = 'purple4'
    DW_COLOR = 'purple'
    DL_COLOR = 'blue2'
    CENTRE_COLOR = 'gold'
    BOARD_SIZE = 15
    SIDE_PANEL_SIZE = 5
    OFFSET_X = 0
    OFFSET_Y = 5
    TILE_SIZE = 25# размер поля игрового
    TITLE_FONT_SIZE = 17
    SUBTITLE_FONT_SIZE = 14
    SUBTITLE_RUS_FONT_SIZE = 10
    INFO_FONT_SIZE = 14
    TILE_FONT_SIZE = 14  # размер плиток
    # TKinter Window, размер самого окна
    window = Tk()
    window.geometry("1100x1000")
    window.resizable(height=None, width=None)

    def __init__(self, player2):
        self.__tiles_remaining = copy.deepcopy(Game.inital_tiles)
        random.shuffle(self.__tiles_remaining)
        self.__words_produced = []
        self.__tiles_occupied = set()
        self.__confirmed_board = [[' ' for x in range(Game.BOARD_SIZE)] for y in range(Game.BOARD_SIZE)]
        self.__potential_board = copy.deepcopy(self.__confirmed_board)
        self.__current_turn = 0
        self.__players = [Player(1)]
        if player2 == 'Computer':
            self.__players.append(Computer(2))
        else:
            self.__players.append(Player(2))
        self.__top_up_tiles()
        self.__buttons = []
        self.__player_tile_buttons = []
        self.__board_tile_selected = False
        self.__tile_swap = False
        self.__game_over = False
        self.__to_be_swapped = []
        self.__selected_board_tile_pos = tuple()
        self.__selected_board_tile_char = ' '
        self.__move_feedback = '                                        '
        self.__player_tile_selected = False
        self.__selected_player_tile_pos = -1
        self.__selected_player_tile_char = ' '
        self.__new_tiles = set()
        self.__round = 0
        self.__create_interface()
        self.__winner_message = ''

    def __create_interface(self): # создание интерфейса, плитки, поля и тд
        self.__create_widgets()
        self.__update_live_info()
        self.__create_board()
        self.__create_tiles()

    def __update_turn_interface(self): # обновление интерфейса поворота
        self.__update_tiles()
        self.__update_board()

    def __update_full_interface(self): # обновление всего интерфейса
        self.__update_live_info()
        self.__update_tiles()
        self.__update_board()

    def __create_widgets(self): # создание виджетов
        title = Label(Game.window, text="WELCOME TO SCRABBLE", font=("Comic Sans MS", Game.TITLE_FONT_SIZE, 'bold'))
        title.grid(row=0, columnspan=Game.BOARD_SIZE) # позиционированние элементов
                                                      # column: номер столбца, отсчет начинается с нуля
                                                      # row: номер строки, отсчет начинается с нуля
                                                      # columnspan: сколько столбцов должен занимать элемент
                                                      # padx и pady: отступы по горизонтали и вертикали соответственно от границ ячейки грида до границ элемента
                                                      # sticky: выравнивание элемента в ячейке, если ячейка больше элемента. Может принимать значения n, e, s, w, ne, nw, se, sw, которые указывают соответствующее направление выравнивания
        self.__players_label = Label(Game.window, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'italic'))
        self.__players_label.grid(row=1, columnspan=Game.BOARD_SIZE, padx=20)
        # кнопка, при нажатии на которую запускается игра человека против человека
        restart_human = Button(Game.window, text='Restart vs Human', command=self.__restart_vs_human,
                               font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width=17)
        restart_human.grid(row=2, column=Game.OFFSET_X, columnspan=Game.BOARD_SIZE // 2, pady=10)
        # кнопка, при нажатии на которую запускается игра человека против компьютера
        restart_human = Button(Game.window, text='Restart vs Computer', command=self.__restart_vs_computer,
                               font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width=17)
        restart_human.grid(row=2, column=Game.OFFSET_X + Game.BOARD_SIZE // 2 + 1, columnspan=Game.BOARD_SIZE // 2)
        # кнопка, при нажатии на которую можно перезапустить ход игрока
        reset_tiles = Button(Game.window, text='Restart Your Move', command=self.__restart_move,
                             font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width=17)
        # надпись на русском "Перезапустите свой ход :)"
        restart_rus = Label(Game.window, text="(Перезапустите свой ход :))", font=("Arial", Game.SUBTITLE_RUS_FONT_SIZE))
        restart_rus.grid(row=0, column=Game.OFFSET_X + Game.BOARD_SIZE, columnspan=Game.BOARD_SIZE,  padx=240, sticky=W)
        # кнопка, при нажатии на которую можно проверить количество очков за слово
        reset_tiles.grid(row=0, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        draft_submit_move = Button(Game.window, text='Check score per word', command=self.__handle_draft_submit_move,
                                   font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width=17)
        # надпись на русском "Можно проверить количество очков за слово:)"
        restart_rus = Label(Game.window, text="(Можно проверить количество очков за слово :))", font=("Arial", Game.SUBTITLE_RUS_FONT_SIZE))
        restart_rus.grid(row=1, column=Game.OFFSET_X + Game.BOARD_SIZE, columnspan=Game.BOARD_SIZE, padx=240, sticky=W)
        # кнопка, при нажатии на которую вы заканчиваете свой ход
        draft_submit_move.grid(row=1, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        submit_move = Button(Game.window, text='Final Submit Move', command=self.__handle_submit_move,
                             font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width=17)
        # надпись на русском "Нажмите, чтобы закончить свой ход:)"
        restart_rus = Label(Game.window, text="(Нажмите, чтобы закончить свой ход:))",
                            font=("Arial", Game.SUBTITLE_RUS_FONT_SIZE))
        restart_rus.grid(row=2, column=Game.OFFSET_X + Game.BOARD_SIZE, columnspan=Game.BOARD_SIZE, padx=240, sticky=W)
        # кнопка, при нажатии на которую вы можете обменять буквы
        submit_move.grid(row=2, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        swap_tiles = Button(Game.window, text='Swap Tiles', command=self.__handle_swap_tiles,
                            font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width=17)
        # надпись на русском "Нажмите если хотите обменять плитки с буквами:>"
        restart_rus = Label(Game.window, text="(Нажмите если хотите обменять плитки с буквами:>)",
                            font=("Arial", Game.SUBTITLE_RUS_FONT_SIZE))
        restart_rus.grid(row=3, column=Game.OFFSET_X + Game.BOARD_SIZE, columnspan=Game.BOARD_SIZE, padx=240, sticky=W)



        # кнопка, при нажатии на которую вы можете обменять буквы
        dictionary_tiles = Button(Game.window, text='Dictionary', command=self.__dictionary_tiles,
                            font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'), width=17)
        dictionary_tiles.grid(row=Game.OFFSET_Y + 15,  column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)

        # надпись на русском "Нажмите если хотите обменять плитки с буквами:>"
        restart_rus = Label(Game.window, text="(Нажмите если хотите посмотреть словарь слов и их перевод:>)",
                            font=("Arial", Game.SUBTITLE_RUS_FONT_SIZE))
        restart_rus.grid(row=Game.OFFSET_Y + 15, column=Game.OFFSET_X + Game.BOARD_SIZE, columnspan=Game.BOARD_SIZE, padx=240, sticky=W)




        # надпись, где выводят сообщение о ходе
        swap_tiles.grid(row=3, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        feedback_headline = Label(Game.window, text='Progress Message:',
                                  font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        feedback_headline.grid(row=Game.OFFSET_Y + 4, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20,
                               sticky=W)
        self.__feedback_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__feedback_label.grid(row=Game.OFFSET_Y + 5, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE,
                                   padx=20, sticky=W)
        # надпись, где показывается чей ход
        current_status_headline = Label(Game.window, font=("Arial", Game.SUBTITLE_FONT_SIZE, "bold"),
                                        text='Player Turn:')
        current_status_headline.grid(row=Game.OFFSET_Y + 7, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE,
                                     padx=20, sticky=W)
        self.__current_status_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__current_status_label.grid(row=Game.OFFSET_Y + 8, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE,
                                         padx=20, sticky=W)
        self.__current_turn_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__current_turn_label.grid(row=3, column=Game.OFFSET_X, columnspan=Game.BOARD_SIZE // 2 + 2, sticky=W)
        self.__tiles_left_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
        self.__tiles_left_label.grid(row=3, column=Game.OFFSET_X + Game.BOARD_SIZE // 2 + 1,
                                     columnspan=Game.BOARD_SIZE // 2, sticky=E, pady=5)
        # надпись, где показывается текущие результаты
        scores_headline = Label(Game.window, text="Current Scores:", font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        scores_headline.grid(row=Game.OFFSET_Y, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20,
                             sticky=W)
        self.__scores_labels = []
        for i in range(2):
            score_label = Label(Game.window, font=("Arial", Game.INFO_FONT_SIZE))
            score_label.grid(row=Game.OFFSET_Y + 1 + i, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE,
                             padx=20, sticky=W)
            self.__scores_labels.append(score_label)
        self.__tile_headline = Label(Game.window, font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        self.__tile_headline.grid(row=Game.OFFSET_Y + Game.BOARD_SIZE + 1, column=Game.OFFSET_X,
                                  columnspan=Game.BOARD_SIZE, sticky=W)

        # стоимость цветных плиток
        key = Label(Game.window, text="Cost of colored tiles:", font=("Arial", Game.SUBTITLE_FONT_SIZE, 'bold'))
        key.grid(row=Game.OFFSET_Y + 10, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        dw = Label(Game.window, text="Double Word", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg=Game.DW_COLOR)
        dw.grid(row=Game.OFFSET_Y + 11, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        dl = Label(Game.window, text="Double Letter", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg=Game.DL_COLOR)
        dl.grid(row=Game.OFFSET_Y + 12, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        tw = Label(Game.window, text="Triple Word", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg=Game.TW_COLOR)
        tw.grid(row=Game.OFFSET_Y + 13, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)
        tl = Label(Game.window, text="Triple Letter", font=("Arial", Game.INFO_FONT_SIZE, 'italic'), fg=Game.TL_COLOR)
        tl.grid(row=Game.OFFSET_Y + 14, column=Game.BOARD_SIZE, columnspan=Game.SIDE_PANEL_SIZE, padx=20, sticky=W)

    def __dictionary_tiles(self):
        '''dic = Toplevel()
        dic.title = "dictionary"
        dic.geometry("500x900")
        dic.resizable(height=None, width=None)'''

        def Scankey(event):

            val = event.widget.get()
            print(val)

            if val == '':
                data = list
            else:
                data = []
                for item in list:
                    if val.lower() in item.lower():
                        data.append(item)

            Update(data)

        def Update(data):

            listbox.delete(0, 'end')

            # put new data
            for item in data:
                listbox.insert('end', item)

        list = (' aa	"	аа " ', ' aah	"	ааа " ', ' aahed	"	ахал " ', ' aahing	"	ахать " ', ' aahs	"	ах " ', ' aal	"	аал " ', ' aalii	"	аалии " ', ' aaliis	"	алиис " ', ' aals	"	аалы " ',
                ' aardvark	"	трубкозуб " ', ' aardvarks	"	трубкозубы " ', ' aardwolf	"	земляной волк " ',
                ' aardwolves	"	земляные волки " ', ' aargh	"	аааа " ', ' aarrgh	"	аааа " ', ' aarrghh	"	ааааа " ',
                ' aarti	"	арти " ', ' aartis	"	Артис " ', ' aas	"	аас " ', ' aasvogel	"	аасвогель " ',
                ' aasvogels	"	аасфогели " ', ' ab	"	аб " ', ' aba	"	аба " ', ' abac	"	абак " ', ' abaca	"	абака " ',
                ' abacas	"	счеты " ', ' abaci	"	счеты " ', ' aback	"	ошеломленный " ', ' abacs	"	счеты " ',
                ' abacterial	"	абактериальный " ', ' abactinal	"	абактинальный " ', ' abactinally	"	абактинально " ',
                ' abactor	"	Абактор " ', ' abactors	"	абакторы " ', ' abacus	"	счеты " ', ' abacuses	"	счеты " ',
                ' abaft	"	в корме " ', ' abaka	"	абака " ', ' abakas	"	абаки " ', ' abalone	"	морское ушко " ',
                ' abalones	"	морские ушки " ', ' abamp	"	абамп " ', ' abampere	"	абампере " ',
                ' abamperes	"	абампер " ', ' abamps	"	абампы " ', ' aband	"	группа " ', ' abanded	"	покинутый " ',
                ' abanding	"	оставление " ', ' abandon	"	покидать " ', ' abandoned	"	заброшенный " ',
                ' abandonedly	"	заброшенный " ', ' abandonee	"	брошенный " ', ' abandonees	"	брошенные " ',
                ' abandoner	"	брошенный " ', ' abandoners	"	брошенные " ', ' abandoning	"	отказ от " ',
                ' abandonment	"	оставление " ', ' abandonments	"	заброшенность " ', ' abandons	"	бросает " ',
                ' abandonware	"	Брошенная посуда " ', ' abandonwares	"	Брошенные изделия " ', ' abands	"	бросает " ',
                ' abapical	"	абапальный " ', ' abas	"	абас " ', ' abase	"	унижать " ',  ' abased	"	униженный " ',
                ' abasedly	"	униженно " ', ' abasement	"	унижение " ', ' abasements	"	унижения " ',
                ' abaser	"	унижающий " ', ' abasers	"	униженные " ', ' abases	"	унижает " ', ' abash	"	смущаться " ',
                ' abashed	"	пристыженный " ', ' abashedly	"	смущенно " ', ' abashes	"	смущает " ',
                ' abashing	"	стыдливый " ', ' abashless	"	бесстыдный " ', ' abashment	"	смущение " ',
                ' abashments	"	смущения " ', ' abasia	"	абазия " ', ' abasias	"	абазиас " ', ' abasing	"	унижение " ',
                ' abask	"	абаск " ', ' abatable	"	приемлемый " ', ' abate	"	уменьшаться " ', ' abated	"	уменьшился " ',
                ' abatement	"	сокращение " ', ' abatements	"	скидки " ', ' abater	"	абатэр " ', ' abaters	"	абатеры " ',
                ' abates	"	стихает " ', ' abating	"	стихает " ', ' abatis	"	абатис " ', ' abatises	"	уменьшает " ',
                ' abator	"	Абатор " ',  ' abators	"	абаторы " ', ' abattis	"	засечка " ',
                ' abattises	"	убирает " ', ' abattoir	"	скотобойня " ', ' abattoirs	"	скотобойни " ',
                ' abattu	"	абатту " ', ' abature	"	абатура " ', ' abatures	"	абатуры " ', ' abaxial	"	абаксиальный " ',
                ' abaxile	"	абаксиль " ', ' abaya	"	Абая " ', ' abayas	"	абайи " ', ' abb	"	абб " ',
                ' abba	"	абба " ', ' abbacies	"	аббатства " ', ' abbacy	"	аббатство " ', ' abbas	"	аббас " ',
                ' abbatial	"	аббатский " ', ' abbe	"	аббат " ', ' abbed	"	аббат " ',
                ' abbes	"	аббаты " ', ' abbess	"	настоятельница " ', ' abbesses	"	настоятельницы " ',
                ' abbey	"	аббатство " ', ' abbeys	"	аббатства " ', ' abbot	"	аббат " ', ' abbotcies	"	аббатства " ',
                ' abbotcy	"	аббатство " ', ' abbots	"	настоятели " ', ' abbotship	"	аббатство " ',
                ' abbotships	"	аббатство " ', ' abbreviate	"	сокращать " ', ' abbreviated	"	сокращенный " ',
                ' abbreviates	"	сокращает " ', ' abbreviating	"	сокращение " ', ' abbreviation	"	Сокращенное название " ',
                ' abbreviations	"	сокращения " ', ' abbreviator	"	аббревиатура " ', ' abbreviators	"	аббревиатуры " ',
                ' abbreviatory	"	аббревиатура " ', ' abbreviature	"	аббревиатура " ', ' abbreviatures	"	сокращения " ',
                ' abbs	"	пресс " ',  ' abcee	"	абси " ', ' abcees	"	абцес " ', ' abcoulomb	"	абкулон " ',
                ' abcoulombs	"	абкулоны " ',  ' abdabs	"	абдабс " ', ' abdicable	"	отрекающийся " ',
                ' abdicant	"	отрекшийся " ', ' abdicants	"	отрекшиеся от престола " ', ' abdicate	"	отрекаться от престола " ',
                ' abdicated	"	отрекся от престола " ', ' abdicates	"	отрекается от престола " ', ' abdicating	"	отречение " ',
                ' abdication	"	отречение " ', ' abdications	"	отречения " ', ' abdicative	"	отрекшийся от престола " ',
                ' abdicator	"	отрекшийся от престола " ', ' abdicators	"	отрекшиеся от престола " ',
                ' abdomen	"	брюшная полость " ', ' abdomens	"	животы " ', ' abdomina	"	живот " ',
                ' abdominal	"	брюшной " ', ' abdominally	"	брюшно " ', ' abdominals	"	брюшной пресс " ',
                ' abdominoplasty	"	абдоминопластика " ', ' abdominous	"	брюшной " ', ' abduce	"	похищать " ',
                ' abduced	"	похищен " ', ' abducens	"	похищение " ', ' abducent	"	похищение " ', ' abducentes	"	похищение " ',
                ' abduces	"	похищает " ', ' abducing	"	похищение " ', ' abduct	"	похищать " ', ' abducted	"	похищен " ', ' abductee	"	похищенный " ',
                ' abductees	"	похищенные " ', ' abducting	"	похищение " ', ' abduction	"	похищение " ', ' abductions	"	похищения " ',
                ' abductor	"	похититель " ', ' abductores	"	похитители " ', ' abductors	"	похитители " ',
                ' abducts	"	похищает " ', ' abeam	"	на траверзе " ', ' abear	"	медведь " ', ' abearing	"	несущий " ',
                ' abears	"	медвежонок " ', ' abecedarian	"	абеседарий " ', ' abecedarians	"	абеседарианцы " ',
                ' abed	"	кровать " ', ' abegging	"	умоляющий " ', ' abeigh	"	возвышаться " ', ' abele	"	абель " ',
                ' abeles	"	абелес " ', ' abelia	"	абелия " ', ' abelian	"	абелев " ',
                ' abelias	"	абелиас " ', ' abelmosk	"	абельмоск " ', ' abelmosks	"	абельмоски " ',
                ' aber	"	абер " ', ' aberdevine	"	абердевайн " ', ' aberdevines	"	абердевайнс " ', ' abernethies	"	абернетис " ',
                ' abernethy	"	абернети " ', ' aberrance	"	заблуждение " ', ' aberrances	"	заблуждения " ', ' aberrancies	"	отклонения " ',
                ' aberrancy	"	отклонение от нормы " ', ' aberrant	"	аномальный " ', ' aberrantly	"	ошибочно " ', ' aberrants	"	аберранты " ',
                ' aberrate	"	аберрировать " ', ' aberrated	"	аберрированный " ', ' aberrates	"	аберрирует " ',
                ' aberrating	"	аберрирующий " ', ' aberration	"	аберрация " ', ' aberrational	"	аберративный " ',
                ' aberrations	"	аберрации " ', ' abers	"	аберс " ', ' abessive	"	одержимый " ', ' abessives	"	абессивы " ',
                ' abet	"	подстрекать " ', ' abetment	"	подстрекательство " ', ' abetments	"	пособничество " ',
                ' abets	"	подстрекает " ', ' abettal	"	соучастие " ', ' abettals	"	соучастники " ', ' abetted	"	содействовал " ',
                ' abetter	"	лучше " ', ' abetters	"	способствует " ', ' abetting	"	подстрекательство " ',
                ' abettor	"	соучастник " ', ' abettors	"	соучастники " ', ' abeyance	"	отсрочка " ',
                ' abeyances	"	отсрочки " ', ' abeyancies	"	перерывы " ', ' abeyancy	"	отсрочка " ',
                ' abeyant	"	отложенный " ', ' abfarad	"	абфарад " ', ' abfarads	"	абфарады " ', ' abhenries	"	абгенрис " ',
                ' abhenry	"	Абгенри " ', ' abhenrys	"	Абгенрис " ', ' abhominable	"	отвратительный " ',
                ' abhor	"	ненавидеть " ', ' abhorred	"	ненавидел " ', ' abhorrence	"	отвращение " ', ' abhorrences	"	отвращение " ',
                ' abhorrencies	"	отвращение " ', ' abhorrency	"	отвращение " ', ' abhorrent	"	отвратительный " ',
                ' abhorrently	"	отвратительно " ', ' abhorrer	"	ненавидящий " ', ' abhorrers	"	ненавистники " ', ' abhorring	"	ненавидящий " ',
                ' abhorrings	"	ненавидит " ', ' abhors	"	ненавидит " ', ' abid	"	ставка " ', ' abidance	"	соблюдение " ',
                ' abidances	"	пребывания " ', ' abidden	"	терпимый " ', ' abide	"	соблюдать " ', ' abided	"	пребывал " ',
                ' abider	"	соблюдающий " ', ' abiders	"	приверженцы " ', ' abides	"	пребывает " ',
                ' abiding	"	постоянный " ', ' abidingly	"	постоянно " ', ' abidings	"	пребывания " ', ' abies	"	абиес " ',
                ' abietes	"	abietes " ', ' abietic	"	абиетический " ', ' abigail	"	Эбигейл " ', ' abigails	"	эбигейлс "')

        ws = Tk()
        ws .title = "dictionary"
        ws .geometry("120x200")
        ws .resizable(height=None, width=None)


        entry = Entry(ws)
        entry.pack()
        entry.bind('<KeyRelease>', Scankey)

        listbox = Listbox(ws)
        listbox.pack()
        Update(list)

    def __update_live_info(self):
        self.__players_label.config(
            text='        ' + self.__players[0].get_type() + ' v ' + self.__players[1].get_type() + '        ')
        self.__feedback_label.config(text=self.__move_feedback + '            ')
        self.__current_turn_label.config(text='Turn(ход игрока): ' + self.__players[self.__current_turn].get_name() + '   ')
        self.__tiles_left_label.config(text="Tiles Remaining: " + str(len(self.__tiles_remaining)))
        for i in range(2):
            self.__scores_labels[i].config(
                text=self.__players[i].get_name() + ': ' + str(self.__players[i].get_current_points()) + '     ')
        self.__tile_headline.config(text=self.__players[self.__current_turn].get_name() + ' tiles:')
        if self.__game_over:
            self.__current_status_label.config(text='GAME OVER: ' + self.__winner_message + '                 ')
        elif self.__players[self.__current_turn].get_type() == 'Human' and not self.__tile_swap:
            self.__current_status_label.config(text='Awaiting human submission (Ваш ход!)                              ')
        elif self.__players[self.__current_turn].get_type() == 'Human' and self.__tile_swap:
            self.__current_status_label.config(text='Please select tiles to be swapped (Подождите, пожалуйста, плитки '
                                                    'меняются местами)                       ')
        else:
            self.__current_status_label.config(text='Patience please...computer is generating moves (Подождите, '
                                                    'пожалуйста, компьютер выполняет ход))')
            """__update_live_info отвечает за обновление информации в графическом интерфейсе для игры.
                  Функция "__update_live_info" обновляет различные метки и текстовые поля с информацией об игроках, требуя прохождения, 
                  количества оставшихся плиток и статуса игры. Она также выявила, закончилась ли игра, и если да, то выводит сообщение о победе,
                   иначе выводит ожидание хода от человека или генерирование хода компьютером. """

    def __create_board(self):
        self.__buttons = []
        for y in range(Game.BOARD_SIZE):
            for x in range(Game.BOARD_SIZE):
                button_frame = Frame(Game.window, width=Game.TILE_SIZE, height=Game.TILE_SIZE)
                button_frame.propagate(False)
                button_frame.grid(row=Game.OFFSET_Y + y, column=Game.OFFSET_X + x, sticky="nsew")
                button_tile = Button(button_frame, text='  ', font=("Arial", Game.TILE_FONT_SIZE), relief='groove')
                button_tile.bind('<Button 1>', self.__handle_button_click)
                button_tile.pack(expand=True, fill=BOTH)
                self.__buttons.append(button_tile)
        self.__update_board()
        """Этот код создает игровую доску (поле) с кнопками, которые изменяются в зависимости от пользовательского ввода
        Для этого он итерируется по координатам на игровой доске и включает каждую настройку по координатам, 
        задавая ее размер и положение в соответствии с координатами. Затем он добавляет функцию-обработчик на 
        приложение и добавляет в список кнопок. Наконец, он вызвал метод __update_board (), 
        который обновляет состояние игровой доски в соответствии с текущими значениями кнопок."""

    def __create_tiles(self):# создание плиток с буквами
        self.__player_tile_buttons = []
        tiles = self.__players[self.__current_turn].get_tiles()
        for i in range(7):
            tile_frame = Frame(Game.window, width=Game.TILE_SIZE, height=Game.TILE_SIZE)
            tile_frame.propagate(False)
            tile_frame.grid(row=Game.BOARD_SIZE + Game.OFFSET_Y + 2, column=Game.OFFSET_X + i, sticky="nsew", pady=4)
            char = tiles[i]
            color = Game.TILE_COLOR
            if char == ' ': color = Game.DEFAULT_COLOR
            text_color = 'blue3'
            if self.__player_tile_selected and self.__selected_player_tile_pos == i: text_color = 'red'
            player_tile = Button(tile_frame, text=char.upper() + Game.subscripts[Game.letter_values[char]],
                                 font=("Arial", Game.TILE_FONT_SIZE), relief='raised', bg=color, fg=text_color)
            player_tile.bind('<Button 1>', self.__handle_tile_click)
            player_tile.pack(expand=True, fill=BOTH)
            self.__player_tile_buttons.append(player_tile)
            """Данный код создает визуальную часть игры в виде плиток с буквами для игроков.
             Для этого создается список, содержащий буквы, которые получил текущий игрок. 
             Затем в цикле создается кадр (Frame), на котором размещается соответствующая буква,
              задается ее цвет (если это пробел, то используется цвет по умолчанию), а также устанавливается цвет текста 
              (если плитка выбрана, то цвет текста изменяется на красный). Созданные плитки добавляются в список плиток игрока.
               Каждая плитка имеет обработчик событий, который вызывается при щелчке на ней."""

    def __update_tiles(self): # плиток с буквами во время хода игры
        tiles = self.__players[self.__current_turn].get_tiles()
        for i in range(7):
            char = tiles[i]
            color = Game.TILE_COLOR
            if char == ' ': color = Game.DEFAULT_COLOR
            text_color = 'blue3'
            if self.__player_tile_selected and self.__selected_player_tile_pos == i: text_color = 'red'
            if self.__tile_swap and i in self.__to_be_swapped: text_color = 'green'
            self.__player_tile_buttons[i].configure(text=char.upper() + Game.subscripts[Game.letter_values[char]],
                                                    bg=color, fg=text_color)
            """Данный код отвечает за обновление плиток с буквами на игровой доске для текущего хода игры.
             Он получает список плиток игрока, который сейчас ходит, и затем для каждой плитки обновляет ее соответствующую кнопку в графическом интерфейсе игры.
             Каждая кнопка плитки получает текст (символ буквы и ее значение в скрипте), цвет фона (Game.TILE_COLOR,
             когда плитка является имеющейся, и Game.DEFAULT_COLOR, когда плитка была использована), и цвет текста 
             (синий для обычных плиток, red для выбранной пользователем плитки, и green для плиток, которые будут заменены).
             Таким образом, этот код обеспечивает правильное обновление плиток на игровой доске в соответствии с текущим состоянием игры."""

    def __update_board(self): # преобразование доски во время игры, те менять так, чтобы на ней были плитки с буквами
        for b in range(Game.BOARD_SIZE ** 2):
            y = b // 15
            x = b % 15
            self.__buttons[b].config(text=self.__potential_board[y][x].upper() + Game.subscripts[
                Game.letter_values[self.__potential_board[y][x]]])
            if self.__potential_board[y][x] != ' ':
                self.__buttons[b].config(bg=Game.TILE_COLOR)
                if self.__board_tile_selected and self.__selected_board_tile_pos == (y, x):
                    self.__buttons[b].config(fg='green')
                elif self.__confirmed_board[y][x] == ' ':
                    self.__buttons[b].config(fg='red')
                else:
                    self.__buttons[b].config(fg='black')
                    self.__buttons[b].bind('<Button 1>', self.__handle_inactive_button)
            else:
                color = Game.DEFAULT_COLOR
                if (y, x) in Game.double_word or (x, y) in Game.double_word:
                    color = Game.DW_COLOR
                elif (y, x) in Game.triple_word or (x, y) in Game.triple_word:
                    color = Game.TW_COLOR
                elif (y, x) in Game.triple_letter or (x, y) in Game.triple_letter:
                    color = Game.TL_COLOR
                elif (y, x) in Game.double_letter or (x, y) in Game.double_letter:
                    color = Game.DL_COLOR
                self.__buttons[b].config(bg=color)
                """Данный код отвечает за обновление игровой доски в интерфейсе игры. В цикле перебираются все ячейки доски,
             каждая кнопка в интерфейсе, соответствующая ячейке, обновляется в соответствии со значениями, 
             хранящимися в матрице self.__potential_board. Если значение в ячейке не равно пробелу, 
             то на кнопке отображается это значение в верхнем регистре и соответствующее значение для буквы в нижнем индексе.
             Если значение равно пробелу, то кнопка окрашивается в соответствующий цвет в зависимости от типа клетки:
             двойное/тройное слово или букву. Если клетка является выбранной, то её текст окрашивается в зеленый цвет.
             Если клетка не была подтверждена, то текст клетки окрашивается в красный цвет, в противном случае - в чёрный цвет. 
             Кнопка также привязывает метод __handle_inactive_button к событию щелчка мыши по ней."""

    def __handle_button_click(self, event): #  кнопки обработки
        # получение местоположения нажатия кнопки
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over and not self.__tile_swap:
            location = self.__buttons.index(event.widget)
            y = location // 15
            x = location % 15
            if self.__potential_board[y][x] == ' ' and self.__player_tile_selected:
                self.__potential_board[y][x] = self.__selected_player_tile_char
                self.__players[self.__current_turn].remove_tile(self.__selected_player_tile_pos)
                self.__player_tile_selected = False
                self.__new_tiles.add((y, x))
            elif self.__potential_board[y][x] == ' ' and self.__board_tile_selected:
                self.__potential_board[y][x] = self.__selected_board_tile_char
                self.__potential_board[self.__selected_board_tile_pos[0]][self.__selected_board_tile_pos[1]] = ' '
                self.__new_tiles.remove(self.__selected_board_tile_pos)
                self.__board_tile_selected = False
                self.__new_tiles.add((y, x))
            elif self.__potential_board[y][x] != ' ':
                self.__board_tile_selected = True
                self.__player_tile_selected = False
                self.__selected_board_tile_pos = (y, x)
                self.__selected_board_tile_char = self.__potential_board[y][x]
            self.__update_turn_interface()
            """__handle_button_click обрабатывает событие клика на кнопке. 
                 Если игрок является человеком, игра еще не закончена и не происходит обмен плитками,
                 то сохраняются координаты нажатой кнопки. Затем определяются координаты клетки на игровом поле, соответствующей нажатой кнопке.
                 Если клетка на игровом поле пуста и выбрана плитка игрока, то плитка помещается на эту клетку и удаляется из руки игрока. 
                 Если клетка на игровом поле пуста и выбрана плитка с игрового поля, то плитка помещается на новую клетку,
                 а на старое место ставится пустота. Если на клетке уже есть плитка, выбранная плитка игрока заменяется на выбранную плитку с игрового поля.
                 В конце обновляется интерфейс игрока."""

    def __handle_inactive_button(self, event):
        pass

    def __handle_tile_click(self, event): # касание плиток
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            location = self.__player_tile_buttons.index(event.widget)
            character = self.__players[self.__current_turn].get_tiles()[location]
            if self.__tile_swap and location not in self.__to_be_swapped:
                self.__to_be_swapped.append(location)
            elif self.__tile_swap and location in self.__to_be_swapped:
                self.__to_be_swapped.remove(location)
            elif self.__board_tile_selected and character == ' ':
                self.__board_tile_selected = False
                self.__players[self.__current_turn].return_tile(location, self.__selected_board_tile_char)
                self.__potential_board[self.__selected_board_tile_pos[0]][self.__selected_board_tile_pos[1]] = ' '
                self.__new_tiles.remove(self.__selected_board_tile_pos)
            elif character != ' ':
                self.__board_tile_selected = False
                self.__player_tile_selected = True
                self.__selected_player_tile_pos = location
                self.__selected_player_tile_char = character
            self.__update_turn_interface()
            """Метод __handle_inactive_button является заглушкой и не выполняет никаких действий при вызове.
               Метод __handle_tile_click обрабатывает нажатия на клетки, на которых находятся буквы в игре. 
               Если текущий игрок является человеческим и игра еще не окончена, метод определяет местоположение нажатой клетки и букву, которая на ней находится.
               Если игрок в данный момент находится в режиме замены плиток, то метод либо добавит выбранную игроком клетку
                в список плиток для замены, либо уберет ее из этого списка в случае повторного нажатия на уже выбранную клетку.
               В противном случае, если клетка на игровом поле была выбрана ранее игроком и на ней находится пустая клетка, 
               метод вернет выбранную игроком клетку на исходную позицию на его игровой панели.
               Если же выбранная игроком клетка содержит букву, то она будет выделена, и данные об этом будут сохранены в текущем объекте игроков,
                включая выбранную позицию и букву.
               После выполнения всех действий метод __update_turn_interface() будет вызван для отображения изменений в игровом интерфейсе."""



    # __top_up_tiles пополнения запасов игроков необходимым им количеством плиток. На вход метод получает информацию о количестве плиток, которые нужны текущему игроку, чтобы продолжить игру
    def __top_up_tiles(self):
        needed = self.__players[self.__current_turn].get_tiles_needed()
        if needed > len(self.__tiles_remaining): # Если количество нужных плиток превышает количество доступных плиток "self.__tiles_remaining",
            needed = len(self.__tiles_remaining) # то метод устанавливает "needed" равным количеству имеющихся плиток.
        to_be_added = [self.__tiles_remaining.pop() for i in range(needed)] #происходит формирование списка "to_be_added" из нужных плиток
        self.__players[self.__current_turn].refill_tiles(to_be_added) #он вызывает у текущего игрока метод "refill_tiles" и передает ему список "to_be_added", чтобы пополнить его запас плиток.

    def __restart_vs_human(self):
        self.__init__('Player')

    def __restart_vs_computer(self):
        self.__init__('Computer')

    def __restart_move(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            self.__reset_tiles()
            self.__tile_swap = False
            self.__to_be_swapped = []
            self.__update_full_interface()
            # Этот код содержит три метода, которые вызывают перезапуск игры.
            # Метод __restart_vs_human() перезапускает игру для игр между двумя игроками. Он вызывает метод init с аргументом «Игрок»,
            # который изначально запускает все переменные и интерфейс игры для игр между двумя игроками.
            # Метод __restart_vs_computer() перезапускает игру для игры против компьютера. Он вызвал метод init с аргументом «Компьютер»,
            # который изначально первоначальизирует все переменные и интерфейс игры для игры против компьютера.
            # Метод __restart_move() перезапускает ход в игре. Он предполагает, что он является активным игроком,
            # и если это так, то сбрасывает плитки, которые были выбраны ранее, и обновляет интерфейс игры.
            # Этот метод завершается без каких-либо действий.

    def __reset_tiles(self): # сбросить плитки
        chars = []
        for t in self.__new_tiles:
            chars.append(self.__potential_board[t[0]][t[1]])
            self.__potential_board[t[0]][t[1]] = ' '
        self.__new_tiles = set()
        self.__players[self.__current_turn].refill_tiles(chars)
        self.__update_turn_interface()
        self.__board_tile_selected = False
        self.__player_tile_selected = False
        # Первая строка объявляет список chars, куда будут добавляться символы из позиций с новыми плитками.
        # Затем происходит цикл, в котором каждый новая плитка в self.__new_tiles проверяется,
        # и его символ добавляется в список chars, после чего символ в позиции на доске заменяется на пробел.
        # Затем переменная self.__new_tiles очищается от элементов.
        # Плитки текущего игрока пополняются символами из списка chars методом refill_tiles() объекта-игрока self.__players[self.__current_turn].
        # Далее в игровом интерфейсе происходит обновление интерфейса текущего хода методом __update_turn_interface().
        # Переменные self.__board_tile_selected и self.__player_tile_selected устанавливаются на False,
        # что означает, что не выбраны ни плитки на доске, ни на руках у игрока.

    def __handle_submit_move(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            self.__submit_move()
            # Первая функция __handle_submit_move(self) проверяет, является ли текущий игрок человеком и игра не закончена.
            # Если это так, то вызывает функцию __submit_move(), которая отвечает за передачу хода и обновление интерфейса.

    def __handle_draft_submit_move(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__tile_swap and not self.__game_over:
            self.__check_submission()
            self.__update_full_interface()
            # Вторая функция __handle_draft_submit_move(self) схожа с первой, но также проверяет,
            # что запрошенный ход не является перестановкой плитки, и после прохождения проверки
            # вызывает функции __check_submission() и __update_full_interface(), которые проверяют допустимость хода и обновляют интерфейс.

    def __handle_swap_tiles(self):
        if self.__players[self.__current_turn].get_type() == 'Human' and not self.__game_over:
            if len(self.__new_tiles) > 0:
                self.__reset_tiles()
            self.__tile_swap = True
        self.__update_full_interface()
        # Третья функция __handle_swap_tiles(self) также проверяет, что текущий игрок является человеком и игра еще не закончилась.
        # Затем она проверяет, что длина списка новых плиток больше 0, и если это так,
        # то вызывает функцию __reset_tiles(), которая возвращает плитки обратно на доску.
        # После этого устанавливается флаг __tile_swap в значение True, что означает, что игрок начал процесс замены плиток.
        # Затем вызывается функция __update_full_interface(), которая обновляет игровой интерфейс.

    def __do_swap_tiles(self): # обмен плитками
        if len(self.__to_be_swapped) > 0:
            for location in self.__to_be_swapped:
                tile = self.__players[self.__current_turn].get_tile(location)
                self.__tiles_remaining.append(tile)
                self.__players[self.__current_turn].remove_tile(location)
            self.__tile_swap = False
            self.__move_feedback = self.__players[self.__current_turn].get_name() + ' decided to swap (решил поменять плитки) ' + str(
                len(self.__to_be_swapped)) + ' tiles          '
            self.__to_be_swapped = []
            random.shuffle(self.__tiles_remaining)
            return True
        else:
            self.__move_feedback = 'Please select at least 1 tile to be swapped (Выберите хотя бы 1 плитку для замены)'
            return False
        # Этот метод выполняет следующие действия:
        # 1. Проверяет, есть ли плитки для замены в списке "self.__to_be_swapped".
        # Если есть, то продолжает выполнение метода, иначе возвращает False и выводит сообщение об ошибке в "self.__move_feedback".
        # 2. Для каждого элемента в списке "self.__to_be_swapped" получает соответствующую плитку из руки текущего игрока
        # методом "get_tile" и удаляет ее из руки методом "remove_tile".
        # 3. Добавляет удаленные плитки в список "self.__tiles_remaining".
        # 4. Устанавливает в значении False переменную "self.__tile_swap".
        # 5. Создает сообщение о действии текущего игрока "self.__move_feedback" путем склейки имени игрока и количества замененных плиток.
        # 6. Очищает список "self.__to_be_swapped".
        # 7. Перемешивает список "self.__tiles_remaining".
        # 8. Возвращает True.

    def __submit_move(self):
        if self.__tile_swap:
            result = self.__do_swap_tiles()
            if result == False:
                print('Invalid submission (Недопустимая отправка)')
                self.__restart_move()
            else:
                self.__current_turn = (self.__current_turn + 1) % 2
                self.__top_up_tiles()
                self.__round += 1
        else:
            result = self.__check_submission()
            if result == False:
                print('Invalid submission (Недопустимая отправка)')
                self.__restart_move()
            else:
                words_created = result[0]
                word_scores = result[1]
                self.__players[self.__current_turn].add_words_played(words_created)
                self.__players[self.__current_turn].increment_score(sum(word_scores))
                self.__words_produced = self.__words_produced + words_created
                self.__confirmed_board = copy.deepcopy(self.__potential_board)
                self.__current_turn = (self.__current_turn + 1) % 2
                self.__tiles_occupied = self.__tiles_occupied.union(self.__new_tiles)
                self.__top_up_tiles()
                self.__round += 1
            self.__new_tiles = set()
            self.__check_game_over()
        self.__update_full_interface()
        if result != False and self.__players[self.__current_turn].get_type() == 'Computer':
            Game.window.after(2000, self.__generate_computer_moves)
            """ Этот код относится к классу и содержит метод `__submit_move()`,
            который вызывается при отправке хода игроком или компьютером в игре Scrabble.

            Если `self.__tile_swap` истинно (т.е. перед ходом было выбрано переставление плитки),
            то метод вызывает метод `__do_swap_tiles()` для выполнения хода.
            Если ход был неверным, то метод выводит сообщение об ошибке и вызывает метод `__restart_move()` для перезапуска текущего хода.
            Если же ход выполнен успешно, то игрок меняется, доска обновляется и раунд увеличивается на 1.

            Если `self.__tile_swap` ложно, то метод вызывает метод `__check_submission()` для проверки хода.
            Если ход был неверным, то метод выводит сообщение об ошибке и вызывает метод `__restart_move()` для перезапуска текущего хода.
            Если же ход выполнен успешно, то составляются слова из тайлов и добавляются в список игрока,
            а также обновляется его счет. Далее игрок меняется, доска обновляется, новые тайлы заменяются на старые,
            и раунд увеличивается на 1. Затем вызывается метод `__check_game_over()` для проверки окончания игры.

            После всех проверок метод обновляет интерфейс и, если игра компьютер против компьютера, через 2 секунды вызывается метод `__generate_computer_moves()`."""

    def __check_game_over(self):
        if set(self.__players[self.__current_turn].get_tiles()) == {' '} and len(self.__tiles_remaining) == 0:
            self.__game_over = True
            if self.__players[0].get_current_points() == self.__players[1].get_current_points():
                self.__winner_message = 'Tie (ПОБЕДИЛА ДРУЖБА! ПОЗДРАВЛЯЮ!)'
            elif self.__players[0].get_current_points() > self.__players[1].get_current_points():
                self.__winner_message = self.__players[0].get_name() + ' WINS (ПОБЕДИЛ, ПОЗДРАВЛЯЮ!)'
            elif self.__players[0].get_current_points() < self.__players[1].get_current_points():
                self.__winner_message = self.__players[1].get_name() + ' WINS (ПОБЕДИЛ, ПОЗДРАВЛЯЮ!)'
                """ Этот код проверяет, закончилась ли игра или нет.
                 Если все игровые плитки игрока равны пробелу и не осталось ни одной плитки, то игра заканчивается.
                 После этого выводится сообщение о победителе: если количество очков обоих игроков равно, выводится сообщение "Tie" (Ничья),
                 в противном случае выводится имя игрока с наибольшим количеством очков и "WINS" (Победил)."""

    def __check_submission(self):
        x_s = set()
        y_s = set()
        for tile in self.__new_tiles:
            x_s.add(tile[1])
            y_s.add(tile[0])
        if len(x_s) > 1 and len(y_s) > 1:
            self.__move_feedback = 'Place tiles on a single row/column (Поместите плитки в одну строку / столбец)'
            return False
        # Сканирование построчно
        unused_tiles = copy.deepcopy(self.__new_tiles)
        new_words = []
        word_scores = []
        complete_tile_usage = False
        for y in range(Game.BOARD_SIZE):
            new_word = False
            old_tile = False
            current_word = ''
            current_word_score = 0
            score_multiplier = 1
            tiles_used = set()
            for x in range(Game.BOARD_SIZE):
                try:
                    current_tile = self.__potential_board[y][x]
                except:
                    print()
                    for i in self.__potential_board:
                        print(i)
                    input()
                    print(Game.BOARD_SIZE)
                    print(x, y)
                previous_tile = self.__confirmed_board[y][x]
                if current_tile != ' ':
                    if len(current_word) == 0:
                        start = [y, x]
                    current_word += current_tile
                    current_word_score += Game.letter_values[current_tile]
                    # print(previous_tile,current_tile)
                    if previous_tile == ' ':
                        tiles_used.add((y, x))
                        new_word = True
                        if (y, x) in Game.double_word or (x, y) in Game.double_word:
                            # print('DOUBLE WORD')
                            score_multiplier *= 2
                        elif (y, x) in Game.triple_word or (x, y) in Game.triple_word:
                            # print('TRIPLE WORD')
                            score_multiplier *= 3
                        elif (y, x) in Game.double_letter or (x, y) in Game.double_letter:
                            # print('DOUBLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile]
                        elif (y, x) in Game.triple_letter or (x, y) in Game.triple_letter:
                            # print('TRIPLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile] * 2

                    elif previous_tile == current_tile:
                        old_tile = True
                if current_tile == ' ' or x == Game.BOARD_SIZE - 1:
                    if new_word and len(current_word) > 1:
                        if current_word not in Game.large_dic:
                            self.__move_feedback = current_word.upper() + ' is not in the dictionary (этого слова нет в словаре!)'
                            return False
                        if tiles_used == self.__new_tiles:
                            complete_tile_usage = True
                        current_word_score *= score_multiplier
                        new_words.append(current_word)
                        word_scores.append(current_word_score)
                        if old_tile:
                            unused_tiles = unused_tiles - tiles_used
                    current_word = ''
                    current_word_score = 0
                    score_multiplier = 1
                    new_word = False
                    old_tile = False
                    tiles_used = set()
                    # Этот код определяет метод под названием «__check_submission», который является частью класса //).
                    # Метод проверяет, находятся ли плитки, размещенные на игровом поле, в одной строке или столбце.
                    # Если они не находятся в одной строке или столбце, он устанавливает переменную «self.__move_feedback» в сообщение,
                    # которое инструктирует игрока размещать плитки в одной строке/столбце, и возвращает False.

                    # Если плитки находятся в одной строке или столбце, метод затем сканирует игровое поле строку за строкой,
                    # чтобы проверить слова, образованные размещением новых плиток.
                    # Он использует переменные «__potential_board» и «__confirmed_board» // для определения позиций плиток на доске.
                    # Для каждой строки он находит все слова, образованные новыми плитками,
                    # и подсчитывает их баллы на основе правил игры (например, балл за двойное слово, балл за тройную букву и т. д.).

                    # Если формируется новое слово, которого нет в игровом словаре, метод устанавливает «self.__move_feedback» в сообщение,
                    # информирующее игрока о том, что слова нет в словаре, и возвращает False.

                    # Затем метод проверяет, используются ли все вновь размещенные плитки для формирования слов.
                    # Если используются все вновь размещенные плитки, для параметра «complete_tile_usage» устанавливается значение «Истина».

                    # Наконец, метод возвращает список новых слов и их оценок, а также набор неиспользуемых плиток.

        # Сканирование столбца за столбцом
        for x in range(Game.BOARD_SIZE):
            new_word = False
            old_tile = False
            current_word = ''
            tiles_used = set()
            for y in range(Game.BOARD_SIZE):
                current_tile = self.__potential_board[y][x]
                previous_tile = self.__confirmed_board[y][x]
                if current_tile != ' ':
                    if len(current_word) == 0:
                        start = [y, x]
                    current_word += current_tile
                    current_word_score += Game.letter_values[current_tile]
                    if previous_tile == ' ':
                        tiles_used.add((y, x))
                        new_word = True
                        if (y, x) in Game.double_word or (x, y) in Game.double_word:
                            # print('DOUBLE WORD')
                            score_multiplier *= 2
                        elif (y, x) in Game.triple_word or (x, y) in Game.triple_word:
                            # print('TRIPLE WORD')
                            score_multiplier *= 3
                        elif (y, x) in Game.double_letter or (x, y) in Game.double_letter:
                            # print('DOUBLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile]
                        elif (y, x) in Game.triple_letter or (x, y) in Game.triple_letter:
                            # print('TRIPLE LETTER', current_tile)
                            current_word_score += Game.letter_values[current_tile] * 2
                    elif previous_tile == current_tile:
                        old_tile = True
                if current_tile == ' ' or y == Game.BOARD_SIZE - 1:
                    if new_word and len(current_word) > 1:
                        if current_word not in Game.large_dic:
                            self.__move_feedback = current_word.upper() + ' is not in the dictionary (этого слова нет в словаре!'
                            return False
                        if tiles_used == self.__new_tiles:
                            complete_tile_usage = True
                        current_word_score *= score_multiplier
                        new_words.append(current_word)
                        word_scores.append(current_word_score)
                        if old_tile:
                            unused_tiles = unused_tiles - tiles_used
                    current_word = ''
                    current_word_score = 0
                    score_multiplier = 1
                    new_word = False
                    old_tile = False
                    tiles_used = set()
                    """Данный код является частью класса Game и выполняет анализ потенциальной доски,
                    чтобы определить валидность хода и набранные очки.
                    Он проходит по каждой клетки доски и проверяет, есть ли на этой клетке буква или нет.
                    Если на клетке есть буква, то она добавляется в текущее слово, и счетчик очков увеличивается на значение буквы (которое задается в словаре letter_values).
                    Затем проверяется, была ли эта плитка уже использована при предыдущих ходах, и если это новая плитка,
                    то определяется, является ли это слово с двойным или тройным коэффициентом за использование этой плитки.
                    Если текущая плитка не соответствует предыдущей плитке в слове, то слово считается новым.
                    Если текущая плитка пуста или достигнут конец строки, а текущее слово длинное, оно добавляется в список новых слов,
                    и вычисляется количество очков, которые будут заработаны за это слово, учитывая множитель слова и множитель букв.
                    Если на доске использовано уже существующее слово, его количество набранных очков не учитывается.
                    Если в текущей клетке нет буквы, текущее слово завершается и очки определяются в зависимости от позиции букв в слове.
                    Если за время прохода по доске были использованы все новые плитки, complete_tile_usage становится True.
                    Если текущее слово не находится в словаре, текущий ход считается недопустимым.
                    В конце прохода список новых слов и общее количество очков для каждого слова возвращаются,
                    чтобы использоваться в самой игре."""

        right_angle = False
        if len(unused_tiles) > 0:
            if len(x_s) == 1:
                for t in self.__new_tiles:
                    y = t[0]
                    x = t[1]
                    try:
                        if self.__potential_board[y][x + 1] != ' ':
                            right_angle = True
                            break
                    except:
                        print("AAARRRGGGGHH")
                    try:
                        if self.__potential_board[y][x - 1] != ' ':
                            right_angle = True
                            break
                    except:
                        print("AAARRRGGGGHH")
            elif len(y_s) == 1:
                for t in self.__new_tiles:
                    y = t[0]
                    x = t[1]
                    try:
                        if self.__potential_board[y + 1][x] != ' ':
                            right_angle = True
                            break
                    except:
                        print("AAARRRGGGGHH")
                    try:
                        if self.__potential_board[y - 1][x] != ' ':
                            right_angle = True
                            break
                    except:
                        print("AAARRRGGGGHH")

        if self.__round > 0 and len(unused_tiles) != 0 and not right_angle:
            self.__move_feedback = 'Form new words with existing tiles (Создайте новые слова из существующих плиток)'
            return False
        if self.__round == 0 and (7, 7) not in self.__new_tiles:
            self.__move_feedback = 'Place first word on centre square (Поместите первое слово в центральный квадрат)'
            return False
        if not complete_tile_usage:
            self.__move_feedback = 'Form a single word with all tiles used (Сформируйте одно слово из всех используемых плиток)'
            return False
        if len(new_words) == 0:
            self.__move_feedback = 'Create at least one new word (Создайте хотя бы одно новое слово)'
            return False
        if self.__players[self.__current_turn].get_type() == 'Human':
            self.__move_feedback = 'VALID SUBMISSION - ' + str(sum(word_scores)) + ' POINTS!'
        else:
            self.__move_feedback = 'COMPUTER SUBMISSION - ' + str(sum(word_scores)) + ' POINTS'
        if len(self.__new_tiles) == 7:
            word_scores.append(50)
            new_words.append('BINGO BONUS!!')
            self.__move_feedback += ' (+50 bingo)'
        print([new_words, word_scores])
        return [new_words, word_scores]
    #Этот код представляет собой метод в классе, который проверяет допустимость хода в игре Scrabble.
    # Код проверяет несколько условий и возвращает список сформированных новых слов и соответствующих оценок,
    # если ход действителен, в противном случае он возвращает False.
    #Код проверяет, есть ли неиспользуемые плитки, образуют ли новые плитки прямой угол с существующими плитками,
    # находится ли первый ход в центральном квадрате, все ли плитки используются для образования одного слова и есть ли хотя бы одна образуется новое слово. В зависимости от этих условий и типа игрока, делающего ход (человек или компьютер), код устанавливает соответствующие сообщения обратной связи.
    #Если игрок использовал все семь плиток за один ход, добавляется бонус в 50 очков.
    #Наконец, код возвращает список сформированных новых слов и соответствующие баллы, если ход действителен,
    # в противном случае он возвращает False.


    def __generate_computer_moves(self):
        best_move_score = 0
        best_move_direction = ''
        best_move_board = []
        best_move_tiles = set()
        tiles = self.__players[self.__current_turn].get_tiles()
        for iterator in range(2):
            for tile in self.__tiles_occupied:
                current_tile = self.__confirmed_board[tile[0]][tile[1]]
                tiles.append(current_tile)
                if iterator == 0:
                    words = self.__players[self.__current_turn].get_highest_scoring_moves(tiles, current_tile)
                else:
                    words = self.__players[self.__current_turn].get_lowest_scoring_moves(tiles, current_tile)
                for w in words:
                    # placing vertically
                    pos = w.index(current_tile)
                    start = (tile[0] - pos, tile[1])
                    max_length = 15 - tile[0]
                    if max_length >= len(w):
                        valid = True
                        for i in range(len(w)):
                            y = start[0] + i
                            x = start[1]
                            if self.__potential_board[y][x] == ' ':
                                self.__new_tiles.add((y, x))
                                self.__potential_board[y][x] = w[i]
                            elif self.__potential_board[y][x] == w[i]:
                                continue
                            else:
                                valid = False
                                break
                        if valid:
                            result = self.__check_submission()
                            if result != False:
                                score = sum(result[1])
                                if score > best_move_score:
                                    best_move_score = score
                                    best_move_board = copy.deepcopy(self.__potential_board)
                                    best_move_tiles = copy.deepcopy(self.__new_tiles)

                    # placing horizontally
                    start = (tile[0], tile[1] - pos)
                    max_length = 15 - tile[1]
                    if max_length >= len(w):
                        valid = True
                        for i in range(len(w)):
                            y = start[0]
                            x = start[1] + i
                            if self.__potential_board[y][x] == ' ':
                                self.__new_tiles.add((y, x))
                                self.__potential_board[y][x] = w[i]
                            elif self.__potential_board[y][x] == w[i]:
                                continue
                            else:
                                valid = False
                                break
                        if valid:
                            result = self.__check_submission()
                            if result != False:
                                score = sum(result[1])
                                if score > best_move_score:
                                    best_move_score = score
                                    best_move_board = copy.deepcopy(self.__potential_board)
                                    best_move_tiles = copy.deepcopy(self.__new_tiles)

                    self.__new_tiles = set()
                    self.__potential_board = copy.deepcopy(self.__confirmed_board)

                tiles.pop()
                j = 1

            if best_move_score != 0:
                break
                #Этот код является методом внутри класса, поэтому некоторые переменные и функции, используемые в коде,
                # Он реализует метод __generate_computer_moves, который генерирует ходы компьютерного игрока в игре с поддержкой нескольких игроков.
                # Этот метод определяет лучший ход компьютера на основе текущего состояния доски и игровых плиток.
                # Вот шаги, выполняемые методом __generate_computer_moves:
                # Инициализация переменных: best_move_score (лучший счет хода), best_move_direction (лучшее направление хода),
                # best_move_board (лучшая доска после хода) и best_move_tiles (лучшие игровые плитки после хода).
                # Получение игровых плиток текущего игрока: tiles = self.__players[self.__current_turn].get_tiles().
                # Цикл с двумя итерациями (for iterator in range(2)), который будет выполнять следующие действия дважды, используя разные итераторы:
                # Обход каждой плитки на доске, занятой игроком: for tile in self.__tiles_occupied.
                # Получение текущей плитки: current_tile = self.__confirmed_board[tile[0]][tile[1]].
                # Добавление текущей плитки к списку игровых плиток: tiles.append(current_tile).
                # В зависимости от значения итератора (0 или 1), вызывается одна из двух функций игрока (get_highest_scoring_moves или get_lowest_scoring_moves)
                # для получения списка возможных слов, которые можно сформировать из игровых плиток. Полученные слова сохраняются в переменной words.
                # Происходит итерация по каждому слову (w) в списке words.
                # Для каждого слова проверяются два варианта размещения на доске: вертикальное и горизонтальное.
                # Проверяется возможность размещения слова вертикально на доске. Вычисляются начальные координаты
                # и максимальная длина для размещения слова. Затем проверяется, можно ли разместить слово на доске
                # без пересечений с другими плитками или незаполненными ячейками. Если размещение возможно, то происходит проверка правильности

            # если слова не найдены, алгоритм повторяется, но вместо этого ищет 10 ходов с наименьшим количеством очков для каждой плитки
        for t in best_move_tiles:
            char = best_move_board[t[0]][t[1]]
            self.__players[self.__current_turn].remove_char(char)

        if best_move_score > 0:
            self.__new_tiles = copy.deepcopy(best_move_tiles)
            self.__potential_board = copy.deepcopy(best_move_board)
        else:
            self.__tile_swap = True
            self.__to_be_swapped = [i for i in range(7)]
        self.__update_turn_interface()
        Game.window.after(2000, self.__submit_move)


class Player:
    def __init__(self, position):
        self._points = 0
        self._tiles = [' ' for i in range(7)]
        self._words_played = []
        self._type = 'Human'
        self._name = 'Player ' + str(position)

    def refill_tiles(self, new_tiles):
        l = len(new_tiles)
        for i in range(l):
            self._tiles[self._tiles.index(' ')] = new_tiles.pop(0)

    def remove_tile(self, pos):
        self._tiles[pos] = ' '

    def remove_char(self, char):
        self._tiles[self._tiles.index(char)] = ' '

    def return_tile(self, pos, char):
        self._tiles[pos] = char

    def get_tiles_needed(self):
        return self._tiles.count(' ')

    def get_tile(self, location):
        return self._tiles[location]

    def get_tiles(self):
        return self._tiles

    def get_words_played(self):
        return self._words_played

    def get_current_points(self):
        return self._points

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def add_words_played(self, words):
        self._words_played = self._words_played + words

    def increment_score(self, points):
        self._points += points

        #__init__(self, position): Метод инициализации класса Player. Он устанавливает начальные значения для переменных игрока,
        # включая количество очков (_points), список игровых плиток (_tiles), список сыгранных слов (_words_played),
        # тип игрока (_type) и имя игрока (_name).
        # refill_tiles(self, new_tiles): Метод для замены пустых игровых плиток новыми плитками.
        # Он принимает список новых плиток (new_tiles) и заменяет пустые плитки игрока на эти новые плитки.
        # remove_tile(self, pos): Метод для удаления плитки из указанной позиции (pos) в списке игровых плиток игрока.
        # Он заменяет плитку на пустой символ ' '.
        # remove_char(self, char): Метод для удаления указанного символа (char) из списка игровых плиток игрока.
        # Он заменяет первое вхождение символа на пустой символ ' '.
        # return_tile(self, pos, char): Метод для возвращения плитки в указанную позицию (pos) в списке игровых плиток игрока.
        # Он заменяет пустую плитку на указанный символ (char).
        # get_tiles_needed(self): Метод для получения количества пустых плиток, требующих заполнения у игрока.
        # Он возвращает количество пустых плиток (' ') в списке игровых плиток.
        # get_tile(self, location): Метод для получения плитки из указанной позиции (location) в списке игровых плиток игрока.
        # Он возвращает символ плитки по указанному индексу.
        # get_tiles(self): Метод для получения списка игровых плиток игрока. Он возвращает весь список игровых плиток.
        # get_words_played(self): Метод для получения списка сыгранных слов игрока. Он возвращает список _words_played.
        # get_current_points(self): Метод для получения текущего количества очков игрока. Он возвращает значение _points.
        # get_name(self): Метод для получения имени игрока. Он возвращает значение _name.
        # get_type(self): Метод для получения типа игрока. Он возвращает значение _type.
        # add_words_played(self, words): Метод для добавления списка слов (words) в список сыгранных слов игрока.
        # Он конкатенирует переданный список слов с текущим списком _words_played.
        # increment_score(self, points): Метод для увеличения колич



class Computer(Player):
    def __init__(self, position):
        super().__init__(position)
        self._type = 'Computer'

    def get_highest_scoring_moves(self, tiles, must_have):
        # попытки найти 10 самых результативных слов из доступных плиток
        relevant_tiles = Game.dic_df[[all(
            True if (word.count(letter) <= tiles.count(letter)) and (must_have in word) else False for letter in word)
                                      for word in Game.dic_df['word']]]
        relevant_tiles = relevant_tiles.sort_values('score', ascending=False).head(10)
        # печать (relevant_tiles.head())
        return list(relevant_tiles['word'])

    def get_lowest_scoring_moves(self, tiles, must_have):
        relevant_tiles = Game.dic_df[[all(
            True if (word.count(letter) <= tiles.count(letter)) and (must_have in word) else False for letter in word)
                                      for word in Game.dic_df['word']]]
        relevant_tiles = relevant_tiles.sort_values('score', ascending=True).head(10)
        return list(relevant_tiles['word'])
    # Computer` добавляет некоторые методы, специфичные для компьютерного игрока. Вот объяснение этих методов:
    # - `__init__(self, position)`: Метод инициализации класса `Computer`.
    # Он вызывает метод `__init__` суперкласса (`Player`) с помощью `super().__init__(position)`, чтобы унаследовать и инициализировать переменные из родительского класса.
    # Затем он устанавливает тип игрока как `'Computer'`.
    # - `get_highest_scoring_moves(self, tiles, must_have)`:
    # Метод для получения списка высокооцененных слов из доступных игровых плиток компьютерного игрока.
    # Он использует полу-метод грубой силы для попытки найти 10 слов с наибольшими очками, используя доступные плитки (`tiles`) и обязательную плитку (`must_have`).
    # Он фильтрует словарь (`Game.dic_df`), выбирая только слова, которые удовлетворяют условиям
    # (количество каждой буквы в слове меньше или равно количеству этой буквы в доступных плитках и обязательная плитка должна присутствовать в слове).
    # Затем он сортирует полученные слова по убыванию и выбирает 10 слов с наивысшими очками.
    # - `get_lowest_scoring_moves(self, tiles, must_have)`:
    # Метод для получения списка низкооцененных слов из доступных игровых плиток компьютерного игрока.
    # Он работает аналогично методу `get_highest_scoring_moves`, но сортирует слова по возрастанию очков, чтобы выбрать 10 слов с наименьшими очками.
    # После определения класса `Computer`, вызывается конструктор класса `Game` с аргументом `'Computer'`,
    # а затем вызывается метод `mainloop()` объекта `Game.window`, который запускает главный цикл окна Tkinter и позволяет игре работать в интерактивном режиме.

Game('Computer')
Game.window.mainloop()