import customtkinter
import CTkListbox
import datetime
import ctypes
import API

# Window specifications
window_width = 800
window_height = 600
app = customtkinter.CTk()
app.title("Currency Rate App")
app.resizable(width=False, height=False)
app.geometry(f"{window_width}x{window_height}")
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

# Centering window at middle of screen
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
position_top = int(screen_height/2 - window_height/2 - 50)
position_right = int(screen_width/2 - window_width/2)
app.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Loader for custom fonts
def loadfont(fontpath):
    pathbuf = ctypes.create_string_buffer(fontpath.encode('utf-8'))
    AddFontResourceEx = ctypes.windll.gdi32.AddFontResourceExA

    return bool(AddFontResourceEx(ctypes.byref(pathbuf), 0x10, 0))

loadfont("Fonts/LEMONMILK-Light.otf")
loadfont("Fonts/Tenada.ttf")

# Functions
def switch_event():
    if switch.get() == 1:
        customtkinter.set_appearance_mode("Dark")
        currentCurrencyBox.configure(text_color="#FFFFFF")
        convertCurrencyBox.configure(text_color="#FFFFFF")
        historyBox.configure(text_color="#FFFFFF")
    else:
        customtkinter.set_appearance_mode("Light")
        currentCurrencyBox.configure(text_color="#000000")
        convertCurrencyBox.configure(text_color="#000000")
        historyBox.configure(text_color="#000000")

def convert_to_digit(text):
    if text == None or text == "":
        return -1

    isDigit = False
    isDot = False
    whiteSpace = False
    dotsCounter = 0
    value = ""

    for letter in text:
        if letter == '.' and not isDigit:
            return 0
        elif letter == '.':
            value += letter
            dotsCounter += 1
            isDot = True
            if dotsCounter > 1:
                return 0
            continue
        
        if letter == ' ' and isDigit:
            whiteSpace = True
            isDot = False
            continue
        elif letter == ' ':
            continue

        if letter.isdigit() and whiteSpace:
            return 0

        if letter.isdigit():
            isDigit = True
            value += letter
            isDot = False
        else:
            return 0
        
    if isDot:
        return 0
    elif not isDigit:
        return -2

    finalValue = float(value)

    return evaluate_currency(finalValue)

def exchange_currencies(currentValue, currentCurrencyIndex, convertCurrencyIndex):
    currentCurrencyValue = API.currencies[currentCurrencyIndex][2]
    convertCurrencyValue = API.currencies[convertCurrencyIndex][2]

    for currency in API.latestExchangeRates:
        if currentCurrencyValue == currency[0]:
            currentCurrencyValue = currency[1]
        if convertCurrencyValue == currency[0]:
            convertCurrencyValue = currency[1]

    amountUSD = currentValue / currentCurrencyValue
    amountValue = amountUSD * convertCurrencyValue

    return evaluate_currency(amountValue)

def check_for_decimal(value):
    buffor = str(value)

    isDot = False
    isZero = False
    isDigit = False

    for char in buffor:
        if char == '.':
            isDot = True
            isDigit = False
            continue

        if char == '0' and isDot and not isDigit:
            isZero = True
        else:
            isDigit = True
            isZero = False
            
    if isZero:
        return False
    else:
        return True
    
def evaluate_currency(value):
    buffor = round(value, 2)

    if check_for_decimal(buffor):
        return round(buffor, 2)
    else:
        return int(buffor)

def on_enter_pressed(event):
    historyEntriesCounter = historyBox.size()
    text = entry.get()
    currentValue = convert_to_digit(text)
    if historyBox.curselection() != None:
        historyBox.deactivate(historyBox.curselection())

    currentCurrencyIndex = currentCurrencyBox.curselection()
    convertCurrencyIndex = convertCurrencyBox.curselection()

    if currentCurrencyIndex != None and convertCurrencyIndex != None:
        currentCurrencySymbol = API.currencies[currentCurrencyIndex][1]
        convertCurrencySymbol = API.currencies[convertCurrencyIndex][1]

        if currentValue == 0:
            convertedValue.configure(text="Incorrect numbers")
            entry.delete(0, "end")
        elif currentValue == -2:
            convertedValue.configure(text="Type value that u want to convert")
            entry.delete(0, "end")
        elif currentCurrencySymbol == convertCurrencySymbol:
            convertedValue.configure(text="You can't convert same type of currencies")
        elif currentValue == -1:
            convertedValue.configure(text="Type value that u want to convert")
        else:
            convertCurrencyValue = exchange_currencies(currentValue, currentCurrencyIndex, convertCurrencyIndex)
            convertedValue.configure(text=f"{currentValue} {currentCurrencySymbol} = {convertCurrencyValue} {convertCurrencySymbol}")
            historyBox.insert(historyEntriesCounter, f"{currentValue} {currentCurrencySymbol} ({API.currencies[currentCurrencyIndex][2]}) exchanged into {convertCurrencyValue} {convertCurrencySymbol} ({API.currencies[convertCurrencyIndex][2]}) at {datetime.datetime.now().replace(microsecond=0)}")
            entry.delete(0, "end")
    else:
        convertedValue.configure(text="You didn't choose currencies types properly")

def chars_limit(event):
    string = entry.get()
    if len(string) >= 12:
        entry.delete(12, "end")

def historyBox_event(event):
    string = historyBox.get()
    buffor = string.split(' ')
    convertedValue.configure(text=f"{buffor[0]} {buffor[1]} = {buffor[5]} {buffor[6]}")

    currentCurrencySymbol = historyBox.get().split()[1]
    convertedCurrencySymbol = historyBox.get().split()[6]

    counterForCurrentSymbol = 0
    for symbol in API.currencies:
        if(symbol[1] == currentCurrencySymbol):
            break
        counterForCurrentSymbol += 1

    counterForConvertSymbol = 0
    for symbol in API.currencies:
        if(symbol[1] == convertedCurrencySymbol):
            break
        counterForConvertSymbol += 1

    currentCurrencyBox.activate(counterForCurrentSymbol)
    convertCurrencyBox.activate(counterForConvertSymbol)

def clearButton_event():
    historyBox.delete("all")

def loadButton_event():
    File = 'historyOfExchanges.txt'
    fileData = []

    # Deleting unnecessary spaces from file
    try:
        fileDataBuffor = []
        with open(File, 'r', encoding="utf-8") as output:
            for line in output:
                fileDataBuffor.append(line.strip().split(' '))

        for cluster in fileDataBuffor:
            buffor = []
            for char in cluster:
                if not len(char) == 0:
                    buffor.append(char)
            fileData.append(buffor)

        if len(fileData) == 0: convertedValue.configure(text="historyOfExchanges.txt is empty")
        else:
            if correctnessOfTheDocument(fileData):
                historyBox.delete("all")
                
                counter = 0
                for line in fileData:
                    buffor = ""
                    
                    for cluster in line:
                        if len(buffor) == 0:
                            buffor += cluster
                        else:
                            buffor += ' ' + cluster

                    historyBox.insert(counter, buffor)
                    counter += 1

                convertedValue.configure(text="Your file has been loaded")
            else:
                convertedValue.configure(text="historyOfExchanges.txt has wrong data")
    except:
        convertedValue.configure(text="historyOfExchanges.txt doesn't exist")

def correctnessOfTheDocument(fileData):
    for line in fileData:
        if not len(line) == 11: return False

        # 1 cluster
        if not check_is_it_number(line[0]): return False
        
        # 2 cluster
        symbolCorrectness = False
        for symbol in API.currencies:
            if symbol[1] == line[1]:
                symbolCorrectness = True

        if not symbolCorrectness: return False

        # 3 cluster
        codeBuffor = ""
        for char in line[2]:
            if char == '(' or char == ')': continue
            else:
                codeBuffor += char

        codeCorrectness = False
        for code in API.currencies:
            if code[2] == codeBuffor:
                codeCorrectness = True

        if not codeCorrectness: return False

        # 4 cluster
        if line[3] != 'exchanged': return False

        # 5 cluster
        if line[4] != 'into': return False

        # 6 cluster
        if not check_is_it_number(line[5]): return False

        # 7 cluster
        symbolCorrectness = False
        for symbol in API.currencies:
            if symbol[1] == line[6]:
                symbolCorrectness = True

        if not symbolCorrectness: return False

        # 8 cluster
        codeBuffor = ""
        for char in line[7]:
            if char == '(' or char == ')': continue
            else:
                codeBuffor += char

        codeCorrectness = False
        for code in API.currencies:
            if code[2] == codeBuffor:
                codeCorrectness = True

        if not codeCorrectness: return False

        # 9 cluster
        if line[8] != 'at': return False

        # 10 & 11 cluser
        dataString = line[9] + ' ' + line[10]
        dataFormat = "%Y-%m-%d %H:%M:%S"

        try:
            datetime.datetime.strptime(dataString, dataFormat)
        except:
            return False

    return True

def check_is_it_number(num):
    if num == None or num == "":
        return False

    isDigit = False
    isDot = False
    whiteSpace = False
    dotsCounter = 0
    value = ""

    for letter in num:
        if letter == '.' and not isDigit:
            return False
        elif letter == '.':
            value += letter
            dotsCounter += 1
            isDot = True
            if dotsCounter > 1:
                return False
            continue
        
        if letter == ' ' and isDigit:
            whiteSpace = True
            isDot = False
            continue
        elif letter == ' ':
            continue

        if letter.isdigit() and whiteSpace:
            return False

        if letter.isdigit():
            isDigit = True
            value += letter
            isDot = False
        else:
            return False
        
    if isDot:
        return False
    elif not isDigit:
        return False

    return True

def saveButton_event():
    convertedValue.configure(text="Your file has been saved")

    historyList = []

    counter = 0
    for entry in range(0, historyBox.size()):
        historyList.append(historyBox.get(counter))
        counter += 1

    with open('historyOfExchanges.txt', 'w', encoding="utf-8") as output:
        for entry in historyList:
            output.write(entry)
            output.write("\n")

# GUI
switch = customtkinter.CTkSwitch(app, text="", command=switch_event, onvalue=0, offvalue=1)
switch.place(relx=0.074, rely=0.03, anchor=customtkinter.CENTER)

title = customtkinter.CTkLabel(app, text="Currency Rate App", fg_color="transparent", font=('Tenada', 35))
title.place(relx=0.495, rely=0.07, anchor=customtkinter.CENTER)

convertedValue = customtkinter.CTkLabel(app, text="", fg_color="transparent", font=('LEMONMILK-Light', 20))
convertedValue.place(relx=0.5, rely=0.22, anchor=customtkinter.CENTER)

entry = customtkinter.CTkEntry(app, placeholder_text="Enter the value")
entry.place(relx=0.5, rely=0.36, anchor=customtkinter.CENTER)
entry.bind("<Return>", on_enter_pressed)
entry.bind("<Key>", chars_limit)

textTypeCurrency = customtkinter.CTkLabel(app, text="Current currency: ", fg_color="transparent", font=('LEMONMILK-Light', 10))
textTypeCurrency.place(relx=0.232, rely=0.32, anchor=customtkinter.CENTER)

currentCurrencyBox = CTkListbox.CTkListbox(app, width=200)
currentCurrencyBox.place(relx=0.23, rely=0.435, anchor=customtkinter.CENTER)

textConvertCurrency = customtkinter.CTkLabel(app, text="Convert to: ", fg_color="transparent", font=('LEMONMILK-Light', 10))
textConvertCurrency.place(relx=0.77, rely=0.32, anchor=customtkinter.CENTER)

convertCurrencyBox = CTkListbox.CTkListbox(app, width=200)
convertCurrencyBox.place(relx=0.77, rely=0.435, anchor=customtkinter.CENTER)

counter = 1
for value in API.currencies:
    currentCurrencyBox.insert(counter, f"{value[0]}: {value[1]}")
    convertCurrencyBox.insert(counter, f"{value[0]}: {value[1]}")
    counter += 1

historyBox = CTkListbox.CTkListbox(app, width=634, height=140, command=historyBox_event)
historyBox.place(relx=0.5, rely=0.72, anchor=customtkinter.CENTER)

clearButton = customtkinter.CTkButton(app, text="Clear", command=clearButton_event, width=50)
clearButton.place(relx=0.718, rely=0.9, anchor=customtkinter.CENTER)

loadButton = customtkinter.CTkButton(app, text="Load", command=loadButton_event, width=50)
loadButton.place(relx=0.8, rely=0.9, anchor=customtkinter.CENTER)

saveButton = customtkinter.CTkButton(app, text="Save", command=saveButton_event, width=50)
saveButton.place(relx=0.882, rely=0.9, anchor=customtkinter.CENTER)

app.mainloop()