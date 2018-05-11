import xlrd


def go_from_excel(num):
    txt = 'history' + str(num) + '.xls'
    data = xlrd.open_workbook(txt)
    sheet = data.sheets()[0]
    rows = sheet.nrows
    text1 = []
    text2 = []
    for i in range(rows):
        text = sheet.row_values(i)[1][1:-1].split(',')
        for x, t in enumerate(text):
            text[x]=float(t)
        text1.append(text)
    for i in range(rows):
        text = sheet.row_values(i)[2][1:-1].split(',')
        for x, t in enumerate(text):
            text[x] = float(t)
        text2.append(text)

    print text1
    print text2
    print zip(text1, text2)


go_from_excel(23)
