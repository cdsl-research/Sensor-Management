import machine

#execfile("bmp280_module.py")

# BMP280のアドレス
BMP280_I2C_ADDRESS = 0x76

# BMP280のレジスタ
BMP280_REG_TEMP_XLSB = 0xFC
BMP280_REG_TEMP_LSB = 0xFB
BMP280_REG_TEMP_MSB = 0xFA
BMP280_REG_PRESS_XLSB = 0xF9
BMP280_REG_PRESS_LSB = 0xF8
BMP280_REG_PRESS_MSB = 0xF7
BMP280_REG_CONFIG = 0xF5
BMP280_REG_CTRL_MEAS = 0xF4
BMP280_REG_STATUS = 0xF3
BMP280_REG_RESET = 0xE0
BMP280_REG_ID = 0xD0

# BMP280の設定
BMP280_OSRS_T = 1  # Temperature oversampling x 1
BMP280_OSRS_P = 1  # Pressure oversampling x 1
BMP280_MODE = 3    # Normal mode

# 設定の計算
ctrl_meas = (BMP280_OSRS_T << 5) | (BMP280_OSRS_P << 2) | BMP280_MODE

# グローバル変数
calibration_params = {}

def init_bmp280(i2c):
    global calibration_params
    
    # BMP280の初期化
    i2c.writeto_mem(BMP280_I2C_ADDRESS, BMP280_REG_CTRL_MEAS, bytes([ctrl_meas]))

    # 補正パラメータの読み取り
    
    #read_calibration_paramsを別ファイルに置く場合
    
    #data = i2c.readfrom_mem(BMP280_I2C_ADDRESS, 0x88, 24)
    #calibration_params = read_calibration_params(data)
    
    def read_calibration_params():
        data = i2c.readfrom_mem(BMP280_I2C_ADDRESS, 0x88, 24)

        dig_T1 = data[1] << 8 | data[0]
        dig_T2 = data[3] << 8 | data[2]
        dig_T3 = data[5] << 8 | data[4]
        dig_P1 = data[7] << 8 | data[6]
        dig_P2 = data[9] << 8 | data[8]
        dig_P3 = data[11] << 8 | data[10]
        dig_P4 = data[13] << 8 | data[12]
        dig_P5 = data[15] << 8 | data[14]
        dig_P6 = data[17] << 8 | data[16]
        dig_P7 = data[19] << 8 | data[18]
        dig_P8 = data[21] << 8 | data[20]
        dig_P9 = data[23] << 8 | data[22]

        return {
            'dig_T1': dig_T1,
            'dig_T2': dig_T2,
            'dig_T3': dig_T3,
            'dig_P1': dig_P1,
            'dig_P2': dig_P2,
            'dig_P3': dig_P3,
            'dig_P4': dig_P4,
            'dig_P5': dig_P5,
            'dig_P6': dig_P6,
            'dig_P7': dig_P7,
            'dig_P8': dig_P8,
            'dig_P9': dig_P9,
        }
        
    
    calibration_params = read_calibration_params()

def read_temp(i2c):
    data = i2c.readfrom_mem(BMP280_I2C_ADDRESS, BMP280_REG_PRESS_MSB, 6)
    
    # 温度
    adc_T = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

    var1 = ((((adc_T >> 3) - (calibration_params['dig_T1'] << 1))) * (calibration_params['dig_T2'])) >> 11
    var2 = (((((adc_T >> 4) - (calibration_params['dig_T1'])) * ((adc_T >> 4) - (calibration_params['dig_T1']))) >> 12) * (calibration_params['dig_T3'])) >> 14
    t_fine = var1 + var2
    temperature = (t_fine * 5 + 128) >> 8
    
    if var1 == 0:
        return None
    
    return temperature / 100.0
    
def read_pressure(i2c):
    data = i2c.readfrom_mem(BMP280_I2C_ADDRESS, BMP280_REG_PRESS_MSB, 6)
    
    adc_T = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

    var1 = ((((adc_T >> 3) - (calibration_params['dig_T1'] << 1))) * (calibration_params['dig_T2'])) >> 11
    var2 = (((((adc_T >> 4) - (calibration_params['dig_T1'])) * ((adc_T >> 4) - (calibration_params['dig_T1']))) >> 12) * (calibration_params['dig_T3'])) >> 14
    t_fine = var1 + var2
    
    # 気圧
    adc_P = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)

    var1 = t_fine - 128000
    var2 = var1 * var1 * calibration_params['dig_P6']
    var2 = var2 + ((var1 * calibration_params['dig_P5']) << 17)
    var2 = var2 + (calibration_params['dig_P4'] << 35)
    var1 = ((var1 * var1 * calibration_params['dig_P3']) >> 8) + ((var1 * calibration_params['dig_P2']) << 12)
    var1 = (((1 << 47) + var1) * calibration_params['dig_P1']) >> 33

    if var1 == 0:
        return None

    p = 1048576 - adc_P
    p = (((p << 31) - var2) * 3125) // var1
    var1 = (calibration_params['dig_P9'] * (p >> 13) * (p >> 13)) >> 25
    var2 = (calibration_params['dig_P8'] * p) >> 19
    pressure = ((p + var1 + var2) >> 8) + (calibration_params['dig_P7'] << 4)

    return pressure / 25600.0
