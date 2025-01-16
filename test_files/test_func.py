from pynput import keyboard
from pynput.keyboard import Key

#freq = int(input('Введите частоту между 7500 МГц и 10100 МГц с шагом'
#                 ' в 1 МГц. Для выхода из программы нажмите клавишу "Esc" \n'))


def user_input_freq():

    freq = int(input('Введите частоту между 7500 МГц и 10100 МГц с шагом'
                 ' в 1 МГц. Для выхода из программы нажмите клавишу "Esc" \n'))
    return freq

def check_valid_freq():
    FREQ_LO: int = 7500
    FREQ_HI: int = 10500
    freq = user_input_freq()

    if FREQ_LO <= freq <= FREQ_HI:
        print(freq)
        #user_step_enter(freq)
        return freq
    else:
        print("Неверный ввод данных. Введите корректное значение частоты!")
        user_input_freq()



def user_step_enter():
    def on_key_release(key):
        freq_valid = check_valid_freq()
        if key == Key.right:
            # print("Right key clicked")
            freq_valid += 100
            print(freq_valid)

        elif key == Key.left:
            # print("Left key clicked")
            freq_valid -= 100
            print(freq_valid)

        elif key == Key.esc:
            exit()

    with keyboard.Listener(on_release=on_key_release) as listener:
        listener.join()


user_input_freq()


