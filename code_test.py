import sys
import time

import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())

# Проверка подключенных устройств с последовательным интерфейсом USB
while not ports:
    print('Отсутствуют  устройства с последовательным интерфейсом USB')
    input('Подключите к USB порту пульт КИА и нажмите клавишу "Enter"')
    ports = list(serial.tools.list_ports.comports())

# https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
# Выводим информацию о каждом подключенном устройстве с
# последовательным интерфейсом USB
for port in ports:
    # print(f"device: {port.device}")
    print(f"name: {port.name}")
    # print(f"description: {port.description}")
    # print(f"hwid: {port.hwid}")
    # print(f"vid: {port.vid}")
    # print(f"pid: {port.pid}")
    print(f"serial_number: {port.serial_number}")
    # print(f"location: {port.location}")
    # print(f"manufacturer: {port.manufacturer}")
    # print(f"product: {port.product}")
    # print(f"interface: {port.interface}")
    print(f"description: {port.description}\n")

# Проверка серийного номера и присвоение номера порта
port_ser: str = port.serial_number
port_ser_1: str = "8D8621A75052"
port_ser_2: str = "8D7E14974950"

reg_0: str
reg_1: str

# N делитель для деления входного ВЧ-сигнала до частоты PFD (fPFD)
FREQ_PFD: int = 120
DENOMINATOR: int = 2**25

if port_ser == port_ser_1:
    ser = serial.Serial(port.name, 9600)
    # print(f"serial_number 8D8621A75052  name: {port.name}")
elif port_ser == port_ser_2:
    ser = serial.Serial(port.name, 9600)
    # print(f"serial_number 8D75759C5752 name: {port.name}")
elif port_ser != port_ser_1 or port_ser != port_ser_2:
    print('Подключенное устройство не является авторизированным пультом КИА')


# Функция проверки ввода частоты
def get_user_input() -> int:
    while True:
        try:
            FREQ_LO: int = 8400
            FREQ_HI: int = 10100
            freq = int(input('Введите частоту между 8400 МГц и 10100 МГц с шагом'
                             ' в 1 МГц. Для выхода из программы введите 0 \n'))
            if FREQ_LO <= freq <= FREQ_HI:
                return freq
            elif freq == 0:
                sys.exit()
        except ValueError:
            print("Неверный ввод данных. Введите корректное значение частоты!")


# Функция отправки комманды 'pw01011000' на МК с признаком готовности приема данных
def get_bit_start() -> str:
    ser.write('pw01011000'.encode('utf-8'))
    # decoded_response = ser.readline().decode('utf-8')
    # print('Data to sent', data, 'Received data', decoded_response[0:-1])
    return ser.readline().decode('utf-8')


# Функция деления 32 бит на 4 части по 8 бит (с дальнейшей отправкой каждой части)

def get_bit_and_send(regbyte) -> str:

    for num_8 in range(0, 32, 8):
        data_8 = 'sw' + regbyte[num_8:num_8 + 8]
        ser.write(data_8.encode('utf-8'))
        response_8 = ser.readline()
        decoded_response_8 = response_8.decode('utf-8')
        print('Data to sent byte', data_8, 'Dec', int(regbyte[num_8:num_8 + 8], 2),
              '| Received data', decoded_response_8[0:-1])
    return decoded_response_8


# Функция отправки комманды 'pw11011000' на МК с признаком окончания приема данных
def get_bit_stop() -> str:
    ser.write('pw11011000'.encode('utf-8'))
    return ser.readline().decode('utf-8')
    # print('Data to sent', data, 'Received data', decoded_response[0:-1])


# dataclass benchmark для определения времени выполнения кода
def benchmark(func):
    import time

    def wrapper():
        start = time.time()  # фиксируем время старта работы кода
        func()
        finish = time.time()  # фиксируем время окончания работы кода
        res = finish - start
        res_mil_sec = res * 1000
        print('Время работы в миллисекундах: ', '{:.3f}'.format(res_mil_sec))
        # print('[*] Время выполнения: {} секунд.'.format(end - start))


    # def wrapper(*args, **kwargs):
    #     start = time.time()  # фиксируем время старта работы кода
    #     return_value = func(*args, **kwargs)
    #     finish = time.time()  # фиксируем время окончания работы кода
    #     res = finish - start
    #     res_mil_sec = res * 1000
    #     print('Время работы в миллисекундах: ', '{:.3f}'.format(res_mil_sec))
    #     # print('[*] Время выполнения: {} секунд.'.format(end - start))
    #     return return_value

    return wrapper


@benchmark
def get_file_txt():
    data: str = 'pw00011000'
    ser.write(data.encode('utf-8'))
    response = ser.readline()
    decoded_response = response.decode('utf-8')
    # print('\nData to sent', data, 'Received data', decoded_response[0:-1])
    print('Питание включено')

    data: str = 'pw01011000'
    ser.write(data.encode('utf-8'))
    response = ser.readline()
    decoded_response = response.decode('utf-8')
    # print('\nData to sent', data, 'Received data', decoded_response[0:-1])
    # print('CE sint = 1')

    data: str = 'pw11011000'
    ser.write(data.encode('utf-8'))
    response = ser.readline()
    decoded_response = response.decode('utf-8')
    print('\nData to sent', data, 'Received data', decoded_response[0:-1])

    regmap_file = open(r"c:\Dev\kia\ADF435x_ADF5355_register_values_8999.txt")
    # regmap_file = open(r"C:\Users\wadm\Desktop\ADF435x_ADF5355_register_values.txt")

    # Цикл построчного считывания значений регистров, удаления последних значений 0х
    # преобразование значений в 32 битную двоичную систему
    # отправка в МК пакетами по 8 бит
    # и вывод ответа, полученного от МК

    for line in regmap_file:

        if line[-1] == '\n':
            regint = int(line[2:-1], 16)
            print("line[2:-1]", line[2:-1])  # view
            print("line[:-1]", line[:-1])  # view
        else:
            regint = int(line[2:], 16)
            print("line[2:]", line[2:])  # view

        regbyte = '{:0b}'.format(regint)
        # print('regbyte ', regbyte)
        regbyte = regbyte.zfill(32)
        print('\nHex', hex(regint), 'Byte', regbyte)

        # INT REGISTER (RO)
        if regbyte[-4:] == '0000':
            reg_0 = regbyte

        # FRAC1 REGISTER (R1)
        if regbyte[-4:] == '0001':
            reg_1 = regbyte

        get_bit_start()
        get_bit_and_send(regbyte)
        get_bit_stop()

    regmap_file.close()

    print('\nИнициализация прошла успешно')

    # 16-битное значение, установленное битами [19:4] в регистре 0
    int_n = int(reg_0[12:28], 2)

    # FRAC1 - 25-битное значение, установленное битами [28:4] в регистре 1
    int_frac_one = int(reg_1[3:28], 2)

    # формула расчета выходной частоты RFout (rf_out) внещнего VCO
    rf_out = int(FREQ_PFD * (int_n + int_frac_one / DENOMINATOR))

    print('\nКоэф.деления:', int_n, ', Частота:', rf_out, 'MHz', ' Прямой',
          rf_out - 75, 'MHz', ' Зеркальный', rf_out + 75, 'MHz')


get_file_txt()


# Код для ручного ввода частоты с последующем вывыдом результатов
#@benchmark
def get_enter_freq():
    while True:
        rf_out = get_user_input()
        # 16-битное значение, установленное битами [19:4] в регистре 0
        int_n = int(int(rf_out) / FREQ_PFD)
        print('int_n   ', int_n)

        # FRAC1 - 25-битное значение, установленное битами [28:4] в регистре 1
        int_frac_one_ost = (rf_out / FREQ_PFD - int_n) * DENOMINATOR
        int_frac_one = round(int_frac_one_ost)
        rf_out = int(FREQ_PFD * (int_n + int_frac_one_ost / DENOMINATOR))


        @benchmark
        def get_tim():
            #
            # # 16-битное значение, установленное битами [19:4] в регистре 0
            # int_n = int(int(rf_out) / FREQ_PFD)
            # print('int_n   ', int_n)
            #
            # # FRAC1 - 25-битное значение, установленное битами [28:4] в регистре 1
            # int_frac_one_ost = (rf_out / FREQ_PFD - int_n) * DENOMINATOR
            # int_frac_one = round(int_frac_one_ost)
            # rf_out = int(FREQ_PFD * (int_n + int_frac_one_ost / DENOMINATOR))

            # формируем FRAC1 для отправки
            regbyte = '{:0b}'.format(int_frac_one)
            print('regbyte frac1', regbyte)
            regbyte = "000" + regbyte.zfill(25) + "0001"
            # print('regbyte.zfill(25) frac1  TYPE', type(regbyte))

            get_bit_start()
            get_bit_and_send(regbyte)
            get_bit_stop()

            # формируем int для отправки
            regbyte = '{:0b}'.format(int_n)
            print('\nHex', hex(int_n), 'Byte {:0b}.format(int_n)', regbyte)
            regbyte = "000000000000" + regbyte.zfill(16) + "0000"
            # print('regbyte   int_n ', regbyte)
            print('\nHex', hex(int_n), 'Byte', regbyte)

            get_bit_start()
            get_bit_and_send(regbyte)
            get_bit_stop()

            print('\nHex', hex(int(regbyte, 2)), 'Byte', regbyte)
            print('\n Частота ', rf_out, 'MHz', 'Коэф.деления:', int_n)

        get_tim()
        # rf_out = get_user_input()
        # start = time.time()
        # # 16-битное значение, установленное битами [19:4] в регистре 0
        # int_n = int(int(rf_out) / FREQ_PFD)
        # print('int_n   ', int_n)
        #
        # # FRAC1 - 25-битное значение, установленное битами [28:4] в регистре 1
        # int_frac_one_ost = (rf_out / FREQ_PFD - int_n) * DENOMINATOR
        # int_frac_one = round(int_frac_one_ost)
        # rf_out = int(FREQ_PFD * (int_n + int_frac_one_ost / DENOMINATOR))
        #
        # # формируем FRAC1 для отправки
        # regbyte = '{:0b}'.format(int_frac_one)
        # print('regbyte frac1', regbyte)
        # regbyte = "000" + regbyte.zfill(25) + "0001"
        # # print('regbyte.zfill(25) frac1  TYPE', type(regbyte))
        #
        # get_bit_start()
        # get_bit_and_send(regbyte)
        # get_bit_stop()
        #
        # # формируем int для отправки
        # regbyte = '{:0b}'.format(int_n)
        # print('\nHex', hex(int_n), 'Byte {:0b}.format(int_n)', regbyte)
        # regbyte = "000000000000" + regbyte.zfill(16) + "0000"
        # # print('regbyte   int_n ', regbyte)
        # print('\nHex', hex(int_n), 'Byte', regbyte)
        #
        # get_bit_start()
        # get_bit_and_send(regbyte)
        # get_bit_stop()
        #
        # print('\nHex', hex(int(regbyte, 2)), 'Byte', regbyte)
        # print('\n Частота ', rf_out, 'MHz', 'Коэф.деления:', int_n)
        # # get_tim()
        # # get_user_input()
        #
        # finish = time.time()
        # res = finish - start
        # print('start  ', start)
        # print('finish   ', finish)
        # print('res   ', res)
        # res_mil_sec = res * 1000
        # print('Время работы в миллисекундах: ', '{:.3f}'.format(res_mil_sec))


get_enter_freq()

# Закрываем порт
ser.close()
