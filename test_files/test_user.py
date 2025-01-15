from pynput import keyboard
from pynput.keyboard import Key

freq = int(input('Введите частоту между 8400 МГц и 10100 МГц с шагом'
                 ' в 1 МГц. Для выхода из программы нажмите клавишу "Esc" \n'))

def inp_freq():
    freq = int(input('Введите частоту между 8400 МГц и 10100 МГц с шагом'
                 ' в 1 МГц. Для выхода из программы нажмите клавишу "Esc" \n'))
    return freq

def user_step_enter():
    def on_key_release(key):
        global freq
        #freq = inp_freq()
        if key == Key.right:
            # print("Right key clicked")
            freq += 100
            freq_print(freq)

        elif key == Key.left:
            # print("Left key clicked")
            freq -= 100
            freq_print(freq)

        elif key == Key.esc:
            exit()

    with keyboard.Listener(on_release=on_key_release) as listener:
        listener.join()

def freq_print(freq):
    FREQ_LO: int = 7500
    FREQ_HI: int = 10500
    if FREQ_LO <= freq <= FREQ_HI:
        print(freq)
        user_step_enter()
    else:
        print("Неверный ввод данных. Введите корректное значение частоты!")
        freq = int(input('Введите частоту между 8400 МГц и 10100 МГц с шагом'
                 ' в 1 МГц. Для выхода из программы нажмите клавишу "Esc" \n'))
        #user_step_enter(freq)

    #print(freq)
    return freq

#freq = inp_freq()
user_step_enter()

#
# # Функция проверки ввода корректной частоты
# def get_user_input() -> int:
#     while True:
#         try:
#             FREQ_LO: int = 7500
#             FREQ_HI: int = 10500
#             freq = float(input('Введите частоту между 7500 МГц и 10500 МГц.'
#                              'Для выхода из программы введите 0 \n'))
#             if FREQ_LO <= freq <= FREQ_HI:
#                 return freq
#             elif freq == 0:
#                 sys.exit()
#         except ValueError:
#             print("Неверный ввод данных. Введите корректное значение частоты!")
