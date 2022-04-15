import openpyxl
import qrcode
from qrcode.image.styledpil import StyledPilImage

tableName = "Students.xlsx"


def makeQrCode(code):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=50,
        border=1,
    )
    qr.add_data(str(code))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white",
                        image_factory=StyledPilImage,
                        embeded_image_path="logo.png")
    return img


wb = openpyxl.load_workbook(tableName, data_only=True)

wb.active = 0

listSheet = wb.active
studentsNum = int(str(listSheet['F2'].value))
codes = []

for i in range(2, studentsNum + 2):
    codes.append('943020' + str(listSheet['A' + str(i)].value).zfill(2) + str(listSheet['C' + str(i)].value).zfill(2) +
                 str(ord(listSheet['D' + str(i)].value)).zfill(2))

for i in range(2, studentsNum + 2):
    print(codes[i - 2])
    makeQrCode(codes[i - 2]).save("Codes/" + str(listSheet['B' + str(i)].value).split()[0] +
                                  "-" + str(listSheet['C' + str(i)].value) +
                                  str(listSheet['D' + str(i)].value) + ".png")
    print("---Done!---")




