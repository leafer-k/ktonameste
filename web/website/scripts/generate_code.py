def generate_codes(number, className, grade):
    return str(str(number).zfill(2) + str(str(grade).zfill(2)) + str(ord(className)).zfill(2))