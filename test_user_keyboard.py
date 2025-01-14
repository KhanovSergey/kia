from pynput import keyboard
from pynput.keyboard import Key


freq = int(input('Введите частоту между 8400 МГц и 10100 МГц с шагом'
             ' в 1 МГц. Для выхода из программы нажмите клавишу "Esc" \n'))

def user_step_enter():
    def on_key_release(key):
        global freq
        if key == Key.right:
            # print("Right key clicked")
            freq = freq + 100
            print(freq)

        elif key == Key.left:
            # print("Left key clicked")
            freq = freq - 100
            print(freq)

        elif key == Key.esc:
            exit()

    with keyboard.Listener(on_release=on_key_release) as listener:
        listener.join()

user_step_enter()


# def on_key_release(key):
#     global freq
#     if key == Key.right:
#         #print("Right key clicked")
#         freq = freq + 100
#         print(freq)
#
#     elif key == Key.left:
#         #print("Left key clicked")
#         freq = freq - 100
#         print(freq)
#
#     elif key == Key.esc:
#         exit()
#
#
# with keyboard.Listener(on_release=on_key_release) as listener:
#     listener.join()