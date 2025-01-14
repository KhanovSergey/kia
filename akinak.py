import os
import sys

import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())

# Проверка подключенных устройств с последовательным интерфейсом USB
while not ports:
    print('Отсутствуют  устройства с последовательным интерфейсом USB')
    input('Подключите к USB порту пульт КИА и нажмите клавишу "Enter"')
    ports = list(serial.tools.list_ports.comports())

# Выводим информацию о каждом подключенном устройстве с
# последовательным интерфейсом USB
for port in ports:
    print(f"name: {port.name}")
    print(f"serial_number: {port.serial_number}")
    print(f"description: {port.description}\n")

reg_zero = ""
reg_one = ""

# N делитель для деления входного ВЧ-сигнала до частоты PFD (fPFD)
FREQ_PFD: int = 120000000
DENOMINATOR: int = 2**25
MHZ_TO_HZ: int = 1000000

ser = serial.Serial(port.name, 9600)
print('ser         ', ser)


# Функция проверки ввода корректной частоты
def get_user_input() -> int:
    while True:
        try:
            FREQ_LO: int = 7500
            FREQ_HI: int = 10500
            freq = float(input('Введите частоту между 7500 МГц и 10500 МГц.'
                             'Для выхода из программы введите 0 \n'))
            if FREQ_LO <= freq <= FREQ_HI:
                return freq
            elif freq == 0:
                sys.exit()
        except ValueError:
            print("Неверный ввод данных. Введите корректное значение частоты!")


# Функция отправки комманды 'pw01011000' на МК с признаком готовности приема данных
def get_bit_start() -> str:
    ser.write('pw01011000'.encode('utf-8'))
    return ser.readline().decode('utf-8')


# Функция деления 32 бит на 4 части по 8 бит (с дальнейшей отправкой каждой части)

def get_bit_and_send(regbyte) -> str:

    for num_8 in range(0, 32, 8):
        data_8 = 'sw' + regbyte[num_8:num_8 + 8]
        ser.write(data_8.encode('utf-8'))
        response_8 = ser.readline()
        decoded_response_8 = response_8.decode('utf-8')
        print('Data to sent byte', data_8, 'Dec', (regbyte[num_8:num_8 + 8], 2),
              '| Received data', decoded_response_8[0:-1])
    return decoded_response_8


# Функция отправки комманды 'pw11011000' на МК с признаком окончания приема данных
def get_bit_stop() -> str:
    ser.write('pw11011000'.encode('utf-8'))
    return ser.readline().decode('utf-8')


# benchmark (декоратор) для определения времени выполнения кода (обертка)
def benchmark(func):
    import time

    def _wrapper():
        start = time.time()  # фиксируем время старта работы кода
        func()
        finish = time.time()  # фиксируем время окончания работы кода
        res = finish - start
        res_mil_sec = res * 1000
        print('Время работы в миллисекундах: ', '{:.3f}'.format(res_mil_sec))

    return _wrapper


@benchmark
def get_file_txt():
    data: str = 'pw00011000'
    ser.write(data.encode('utf-8'))
    response = ser.readline()
    decoded_response = response.decode('utf-8')
    print('\nData to sent', data, 'Received data', decoded_response[0:-1])
    print('Питание включено')

    data: str = 'pw01011000'
    ser.write(data.encode('utf-8'))
    response = ser.readline()
    decoded_response = response.decode('utf-8')
    print('\nData to sent', data, 'Received data', decoded_response[0:-1])

    data: str = 'pw11011000'
    ser.write(data.encode('utf-8'))
    print('ser.write(data.encode('')) ', ser.write(data.encode('utf-8')))
    response = ser.readline()
    print('response = ser.readline()     ', ser.readline())
    decoded_response = response.decode('utf-8')
    print('response.decode('')   ', response.decode('utf-8'))
    print('\nData to sent', data, 'Received data', decoded_response[0:-1])

    regmap_file = open(os.path.realpath('ADF435x_ADF5355_register_values.txt'))

    # Цикл построчного считывания значений регистров, удаления последних значений 0х
    # преобразование значений в 32 битную двоичную систему
    # отправка в МК пакетами по 8 бит
    # и вывод ответа, полученного от МК

    for line in regmap_file:

        if line[-1] == '\n':
            regint = int(line[2:-1], 16)
        else:
            regint = int(line[2:], 16)

        regbyte = '{:0b}'.format(regint)
        regbyte = regbyte.zfill(32)
        print('\nHex', hex(regint), 'Byte', regbyte)

        # INT REGISTER (RO)
        if regbyte[-4:] == '0000':
            global reg_zero
            reg_zero = regbyte

        # FRAC1 REGISTER (R1)
        if regbyte[-4:] == '0001':
            global reg_one
            reg_one = regbyte

        get_bit_start()
        get_bit_and_send(regbyte)
        get_bit_stop()

    regmap_file.close()

    print('\nИнициализация прошла успешно')

    # 16-битное значение, установленное битами [19:4] в регистре 0
    int_n = int(reg_zero[12:28], 2)

    # FRAC1 - 25-битное значение, установленное битами [28:4] в регистре 1
    int_frac_one = int(reg_one[3:28], 2)

    # формула расчета выходной частоты RFout (rf_out) внещнего VCO
    rf_out = (round(FREQ_PFD * (int_n + int_frac_one / DENOMINATOR))) / MHZ_TO_HZ

    print('\nКоэф.деления:', int_n, ', Частота:', rf_out, 'MHz', ' Прямой',
          rf_out - 75, 'MHz', ' Зеркальный', rf_out + 75, 'MHz')


get_file_txt()


# # Код для ручного ввода частоты с последующем вывыдом результатов
# @benchmark
def get_enter_freq():
    #import time
    while True:
        rf_out = get_user_input()
        #start = time.time()  # фиксируем время старта работы кода

        # 16-битное значение, установленное битами [19:4] в регистре 0
        int_n = int((rf_out * MHZ_TO_HZ) / FREQ_PFD)

        # FRAC1 - 25-битное значение, установленное битами [28:4] в регистре 1
        int_frac_one_ost = (rf_out * MHZ_TO_HZ / FREQ_PFD - int_n) * DENOMINATOR
        int_frac_one = round(int_frac_one_ost)
        rf_out = (round(FREQ_PFD * (int_n + int_frac_one_ost / DENOMINATOR))) / MHZ_TO_HZ

        # формируем FRAC1 для отправки
        regbyte = '{:0b}'.format(int_frac_one)
        regbyte = reg_one[0:3] + regbyte.zfill(25) + "0001"
        print('\nHex', hex(int(regbyte, 2)), 'Byte', regbyte)

        get_bit_start()
        get_bit_and_send(regbyte)
        get_bit_stop()

        # формируем int для отправки
        regbyte = '{:0b}'.format(int_n)
        regbyte = reg_zero[0:12] + regbyte.zfill(16) + "0000"
        print('\nHex', hex(int(regbyte, 2)), 'Byte', regbyte)

        get_bit_start()
        get_bit_and_send(regbyte)
        get_bit_stop()

        #finish = time.time()  # фиксируем время окончания работы кода
       # res = finish - start
        #res_mil_sec = res * 1000

        print('\nЧастота ', rf_out, 'MHz', 'Коэф.деления:', int_n)
        #print('Время работы в миллисекундах: ', '{:.3f}'.format(res_mil_sec))


get_enter_freq()

# Закрываем порт
ser.close()
