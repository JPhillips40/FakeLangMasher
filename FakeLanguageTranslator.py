import random
import requests
import uuid
import json
import math
import string
from typing import List, Dict, Tuple

# Constants
KEY = "(enter key)"
ENDPOINT = "https://api.cognitive.microsofttranslator.com"
LOCATION = "southcentralus"
CONSTRUCTED_URL = ENDPOINT + '/translate'

HEADERS = {
    'Ocp-Apim-Subscription-Key': KEY,
    'Ocp-Apim-Subscription-Region': LOCATION,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

class bcolors:
    YELLOW = '\033[93m' # View dictionary
    GREEN = '\033[92m' # Translate
    CYAN = '\033[96m' # Add Translation
    BLUE = '\033[94m' # Edit Dict
    MAGENTA = '\033[95m' # List names
    PINK = '\033[38;5;206m' # Generate new names
    RED = '\033[91m' # quit, cancel, etc
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'
    
    def get_color (colorCode: str, string: str) -> str:
        return f"{colorCode}{string}{bcolors.ENDC}"
    def get_bold_color(colorCode: str) -> str:
        BOLD = '1m'
        colorCode = colorCode[:-1]
        return f"{colorCode};{BOLD}"

# File paths
DICTIONARY_FILE = 'Lann\u00e8.json'
FIRST_NAMES_FILE = 'Lann\u00e8_firstNames.json'
LAST_NAMES_FILE = 'Lann\u00e8_lastNames.json'

def translate_str(lang: str, inp: str, transl: bool = False) -> str:
    params = {}
    if transl:
        params = {
        'api-version': '3.0',
        'from': 'en',
        'to': [lang],
        'toScript': 'Latn'
        }
    else:
        params = {
        'api-version': '3.0',
        'from': 'en',
        'to': [lang]
        }

    body = [{
        'text': inp
    }]
    
    #pull translation from Azure and convert to JSON list
    request = requests.post(CONSTRUCTED_URL, params=params, headers=HEADERS, json=body)
    response = request.json()
    
    if transl:
        return response[0]['translations'][0]['transliteration']['text'].lower()
    else:
        return response[0]['translations'][0]['text'].lower()

def merge_words(word1: str, word2: str, weight1: float, weight2: float) -> str:
    firstLength = math.ceil(len(word1) * weight1)
    firstPortion = word1[:firstLength]
    
    secondLength = math.ceil(len(word2) * weight2)
    secondPortion = word2[secondLength:]

    return (firstPortion + secondPortion)

def flip_words(merged: str) -> str:
    length = math.ceil(len(merged) * 0.5)
    firstPortion = merged[length:]
    secondPortion = merged[:length]

    return(firstPortion + secondPortion)

def print_possible_translations(translations: List[List[str]]) -> None:
    count = len(translations)
    iterations = round(math.pow(2, count))

    for it in range(iterations):
        output = []
        for word in range(count):
            multiple = math.pow(2,word)
            if (it % multiple == 0 and (it / multiple) % 2 != 0):
                output.append(translations[word][1])
            else:
                nearestMult = multiple * math.floor(it / multiple)
                if (nearestMult != 0):
                    if ((nearestMult / multiple) % 2 != 0 and it >= nearestMult and it <= nearestMult + multiple and multiple != 1):
                        output.append(translations[word][1])
                    else:
                        output.append(translations[word][0])
                else:
                    output.append(translations[word][0])
        print(*output, sep=' | ')

def print_word_forms(translations: List[List[str]], translationsFlip: List[List[str]], selectedWord: int) -> None:
    print("1) " + translations[selectedWord][0])
    print("2) " + translations[selectedWord][1])
    print("3) " + translationsFlip[selectedWord][0])
    print("4) " + translationsFlip[selectedWord][1])

def save_distribution_input(inp: str, translations: List[List[str]], translationsFlip: List[List[str]], selectedWord: int, inputs: List[str], dictionary: Dict[str, str]) -> None:
    confirmation = "Saved \"" + inputs[selectedWord] + "\" as \""
    if inp == '1':
        dictionary[inputs[selectedWord]] = translations[selectedWord][0]
        confirmation += translations[selectedWord][0] + "\"."
    elif inp == '2':
        dictionary[inputs[selectedWord]] = translations[selectedWord][1]
        confirmation += translations[selectedWord][1] + "\"."
    elif inp == '3':
        dictionary[inputs[selectedWord]] = translationsFlip[selectedWord][0]
        confirmation += translationsFlip[selectedWord][0] + "\"."
    elif inp == '4':
        dictionary[inputs[selectedWord]] = translationsFlip[selectedWord][1]
        confirmation += translationsFlip[selectedWord][1] + "\"."
    if inp != 'c':
        print(confirmation)

def capitalize_first(inp: str) -> str:
    return inp[0].upper() + inp[1:]

def load_json_file(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json_file(file_path: str, data: Dict) -> None:
    with open(file_path, 'w') as f:
        json.dump(data, f)

def view_dictionary(dictionary: Dict[str, str]) -> None:
    dictChoice = input(bcolors.get_color(bcolors.get_bold_color(bcolors.YELLOW), "\nBrowse (b), Search (s): ")).lower()

    if dictChoice == 'b':
        print('')
        for key in sorted(dictionary):
            print(bcolors.get_color(bcolors.YELLOW, key) + ": " + dictionary[key])
        print('')

    elif dictChoice == 's':
        searchType = input(bcolors.get_color(bcolors.YELLOW, "Words (w), Definitions(d): ")).lower()
        if searchType == 'w':
            searchChoice = input(bcolors.get_color(bcolors.YELLOW, "Word to search: ")).lower()
            print('')
            dictFound = False
            for word in dictionary:
                if searchChoice in word:
                    print(bcolors.get_color(bcolors.YELLOW, word) + ": " + dictionary[word])
                    dictFound = True
            if dictFound == False:
                print(bcolors.get_color(bcolors.RED, "No matching entry in dictionary found."))
            print('')
                
        elif searchType == 'd':
            searchChoice = input(bcolors.get_color(bcolors.YELLOW, "Definition to search: ")).lower()
            print('')
            dictFound = False
            for key in sorted(dictionary):
                if searchChoice in dictionary[key]:
                    print(bcolors.get_color(bcolors.YELLOW, key) + ": " + dictionary[key])
                    dictFound = True
            if dictFound == False:
                print(bcolors.get_color(bcolors.RED, "No matching entry in dictionary found."))
            print('')

def translate_sentence(dictionary: Dict[str, str]) -> None:
    detailChoice = input(bcolors.get_color(bcolors.get_bold_color(bcolors.GREEN), "Detail mode? (y/n): ")).lower()

    #take user input, remove punctuation, and split to list
    userInput = input(bcolors.get_color(bcolors.GREEN, "Sentence to translate, words separated by spaces: "))
    inputs = userInput.split()
    for i in range(len(inputs)):
        inputs[i] = (inputs[i].replace('-', ' ')).replace(string.punctuation, '')
    print('')

    translatable = True
    if (len(inputs) == 0):
        translatable = False
    elif (inputs[0] == ' '):
        translatable = False

    if translatable == False:
        print(bcolors.get_color(bcolors.RED, "Could not translate."))

    allWordsInDict = True
    inDict = []
    match = False
    for inp in inputs:
        exactMatch = False
        for word in dictionary:
            if inp in word:
                print(word + ": " + dictionary[word])
                match = True
                if inp == word:
                    inDict.append(dictionary[word])
                    exactMatch = True
        if exactMatch == False:
            inDict.append("not-in-dict")
            allWordsInDict = False
    if match:
        print('')

    translations = []
    translations0 = []
    translations1 = []
    translations2 = []
    translationsFlip = []
    translationsFlip0 = []
    translationsFlip1 = []
    translationsFlip2 = []

    counter = 0
    for i in inputs:
        inDict.append("not-in-dict")
    if translatable:
        for word in inputs:
            words0 = []
            words1 = []
            words2 = []
            wordsFlip0 = []
            wordsFlip1 = []
            wordsFlip2 = []
            translatable = True
            if inDict[counter] == "not-in-dict":
                trans1 = translate_str(lang='ht', inp=word, transl=False)
                trans2 = translate_str(lang='lv', inp=word, transl=False)
            
                print(word + ": " + trans1)
                print(word + ": " + trans2)
                print('')
                if trans1 == word or trans2 == word:
                    print(bcolors.get_color(bcolors.RED, "Untranslatable word: ") + word + "\n")
                    translatable = False
                    break

                wordVar0_0 = merge_words(trans1, trans2, .5, .5)
                wordVar0_1 = merge_words(trans2, trans1, .5, .5)
                wordVar1_0 = merge_words(trans1, trans2, .65, .35)
                wordVar1_1 = merge_words(trans2, trans1, .65, .35)
                wordVar2_0 = merge_words(trans1, trans2, .35, .65)
                wordVar2_1 = merge_words(trans2, trans1, .35, .65)

                words0.append(wordVar0_0)
                words0.append(wordVar0_1)
                words1.append(wordVar1_0)
                words1.append(wordVar1_1)
                words2.append(wordVar2_0)
                words2.append(wordVar2_1)
                translations0.append(words0)
                translations1.append(words1)
                translations2.append(words2)

                wordsFlip0.append(flip_words(wordVar0_0))
                wordsFlip0.append(flip_words(wordVar0_1))
                wordsFlip1.append(flip_words(wordVar1_0))
                wordsFlip1.append(flip_words(wordVar1_1))
                wordsFlip2.append(flip_words(wordVar2_0))
                wordsFlip2.append(flip_words(wordVar2_1))
                translationsFlip0.append(wordsFlip0)
                translationsFlip1.append(wordsFlip1)
                translationsFlip2.append(wordsFlip2)
            else:
                words0.append(inDict[counter])
                words0.append(inDict[counter])
                words1.append(inDict[counter])
                words1.append(inDict[counter])
                words2.append(inDict[counter])
                words2.append(inDict[counter])
                translations0.append(words0)
                translations1.append(words1)
                translations2.append(words2)

                wordsFlip0.append(inDict[counter])
                wordsFlip0.append(inDict[counter])
                wordsFlip1.append(inDict[counter])
                wordsFlip1.append(inDict[counter])
                wordsFlip2.append(inDict[counter])
                wordsFlip2.append(inDict[counter])
                translationsFlip0.append(wordsFlip0)
                translationsFlip1.append(wordsFlip1)
                translationsFlip2.append(wordsFlip2)
            counter += 1
        
    if translatable:
        translations.append(translations0)
        translations.append(translations1)
        translations.append(translations2)
        translationsFlip.append(translationsFlip0)
        translationsFlip.append(translationsFlip1)
        translationsFlip.append(translationsFlip2)

        print(bcolors.get_color(bcolors.GREEN, "Translations (50/50):"))
        print_possible_translations(translations0)
        print(bcolors.get_color(bcolors.GREEN, "\nTranslations (50/50)(flipped):"))
        print_possible_translations(translationsFlip0)
        print('')
        if detailChoice == 'y':
            print(bcolors.get_color(bcolors.GREEN, "Translations (65/35):"))
            print_possible_translations(translations1)
            print(bcolors.get_color(bcolors.GREEN, "\nTranslations (65/35)(flipped):"))
            print_possible_translations(translationsFlip1)
            print('')
            print(bcolors.get_color(bcolors.GREEN, "Translations (35/65):"))
            print_possible_translations(translations2)
            print(bcolors.get_color(bcolors.GREEN, "\nTranslations (35/65)(flipped):"))
            print_possible_translations(translationsFlip2)
            print('')

        if allWordsInDict == False:
            saveChoice = input(bcolors.get_color(bcolors.get_bold_color(bcolors.CYAN), "Save word to dictionary? (y/n): ")).lower()
            selectedWord = 1
            if saveChoice == 'y':
                if len(inputs) > 1:
                    selectedWord = int(input(bcolors.get_color(bcolors.CYAN, "Select an inputted word: ")))
                    while selectedWord > len(inputs) or selectedWord < 1:
                        selectedWord = int(input(bcolors.get_color(bcolors.CYAN, "Select an inputted word: ")))
                selectedWord -= 1

                detailSaveChoice = '1'
                if detailChoice == 'y':
                    detailSaveChoice = input(bcolors.get_color(bcolors.CYAN, "Select a language distribution to choose from: "))
                    while int(detailSaveChoice) < 1 or int(detailSaveChoice) > 3:
                        detailSaveChoice = input(bcolors.get_color(bcolors.CYAN, "Select a language distribution to choose from: "))
                print('')

                print_word_forms(translations[int(detailSaveChoice) - 1], translationsFlip[int(detailSaveChoice) - 1], selectedWord)
                print('')

                for word in dictionary:
                    if inputs[selectedWord] in word:
                        print(word + ": " + dictionary[word])
                print('')

                chosenTranslation = input(bcolors.get_color(bcolors.CYAN, "Select a translation to save or cancel (c): "))
                if detailSaveChoice == '1':
                    save_distribution_input(chosenTranslation, translations0, translationsFlip0, selectedWord, inputs, dictionary)
                elif detailSaveChoice == '2':
                    save_distribution_input(chosenTranslation, translations1, translationsFlip1, selectedWord, inputs, dictionary)
                elif detailSaveChoice == '3':
                    save_distribution_input(chosenTranslation, translations2, translationsFlip2, selectedWord, inputs, dictionary)
                elif chosenTranslation == 'c':
                    return

    repeatChoice = input(bcolors.get_color(bcolors.get_bold_color(bcolors.GREEN), "Translate again? (y/n): ")).lower()
    if repeatChoice == 'y':
        translate_sentence(dictionary)
    print('')

def add_translation(dictionary: Dict[str, str]) -> None:
    print('')
    wordEnglish = input(bcolors.get_color(bcolors.CYAN, "Word in English: "))
    wordTranslation = input(bcolors.get_color(bcolors.CYAN, "Word translated: "))

    dictionary[wordEnglish] = wordTranslation
    print(bcolors.get_color(bcolors.get_bold_color(bcolors.CYAN), "Saved \"" + wordEnglish + "\" as \"" + wordTranslation + "\""))
    print('')

def edit_dictionary(dictionary: Dict[str, str]) -> None:
    searchChoice = input(bcolors.get_color(bcolors.BLUE, "Entry to edit: "))
    print('')
    matchingEntries = []
    selectedEntry = 'c'
    oldTranslation = ''
    wordCount = 0
    for word in dictionary:
        if searchChoice in word:
            print(str(wordCount) + ") " + bcolors.get_color(bcolors.BLUE, word) + ": " + dictionary[word])
            matchingEntries.append(word)
            wordCount += 1
    if len(matchingEntries) == 0:
        print(bcolors.get_color(bcolors.RED, "No matching entry in dictionary found."))
    else:
        selectedEntry = input(bcolors.get_color(bcolors.BLUE, "\nSelect entry to edit (0 - " + str(len(matchingEntries) - 1) + ") or cancel (c): ")).lower()

    if selectedEntry != 'c':
        selectedEntry = int(selectedEntry)
        editDecision = input(bcolors.get_color(bcolors.BLUE, "Delete (d) or Edit (e) \"" + matchingEntries[selectedEntry] + "\": ")).lower()
        if editDecision == 'd':
            print(bcolors.get_color(bcolors.BLUE, "Deleted '" + dictionary[matchingEntries[selectedEntry]] + "' from dictionary."))
            dictionary.pop(matchingEntries[selectedEntry])
        elif editDecision == 'e':
            oldTranslation = dictionary[matchingEntries[selectedEntry]]
            newTranslation = input(bcolors.get_color(bcolors.BLUE, "New translation or cancel (c): ")).lower()
            if newTranslation != 'c':
                print(bcolors.get_color(bcolors.BLUE, "Changed definition of \"" + matchingEntries[selectedEntry] + "\" from \"" + oldTranslation + "\" to \""
                      + newTranslation + "\""))
                dictionary[matchingEntries[selectedEntry]] = newTranslation
    print('')

def list_names(first_names: Dict[str, str], last_names: Dict[str, str]) -> None:
    print(bcolors.get_color(bcolors.get_bold_color(bcolors.MAGENTA), "\nLast names\n----------------"))
    print(bcolors.get_color(bcolors.get_bold_color(bcolors.MAGENTA), "\n[Job surnames]"))
    for key in sorted(last_names):
        if (key[len(key) - 2] + key[len(key) - 1] == "\u012bt"):
            print(bcolors.get_color(bcolors.MAGENTA, key) + ": " + last_names[key])
    print(bcolors.get_color(bcolors.get_bold_color(bcolors.MAGENTA), "\n[Other]"))
    for key in sorted(last_names):
        if (key[len(key) - 2] + key[len(key) - 1] != "\u012bt"):
            print(bcolors.get_color(bcolors.MAGENTA, key) + ": " + last_names[key])
    print(bcolors.get_color(bcolors.get_bold_color(bcolors.MAGENTA), "\nFirst names\n----------------"))
    for key in sorted(first_names):
        print(bcolors.get_color(bcolors.MAGENTA, key) + ": " + first_names[key])
    print('')

def generate_new_names(dictionary: Dict[str, str], first_names: Dict[str, str], last_names: Dict[str, str]) -> None:
    dictWords = list(dictionary.keys())
 
    print(bcolors.get_color(bcolors.get_bold_color(bcolors.PINK), "\nLast name\n----------------"))
    newLastNames = []
    newLastNameMeanings = []
    for ln in range(10):
        rngLastName = random.randint(0, len(dictionary) - 1)
        while capitalize_first(dictionary[dictWords[rngLastName]]) in last_names:
            rngLastName = random.randint(0, len(dictionary) - 1)

        newLastNames.append(capitalize_first(dictionary[dictWords[rngLastName]]))
        newLastNameMeanings.append(dictWords[rngLastName])
        print(str(ln) + ") " + bcolors.get_color(bcolors.PINK, capitalize_first(dictionary[dictWords[rngLastName]])) + ": " + dictWords[rngLastName])
    saveChoice = input(bcolors.get_color(bcolors.PINK, "Save any last name? (y/n): ")).lower()
    if saveChoice == 'y':
        saveNum = input(bcolors.get_color(bcolors.PINK, "Enter last name num to save: "))
        while int(saveNum) < 0 or int(saveNum) > 9:
            saveNum = input(bcolors.get_color(bcolors.PINK, "Enter last name num to save: "))

        last_names[newLastNames[int(saveNum)]] = newLastNameMeanings[int(saveNum)]
        print(newLastNames[int(saveNum)] + bcolors.get_color(bcolors.PINK, " saved as a last name, meaning ") + newLastNameMeanings[int(saveNum)])

    print(bcolors.get_color(bcolors.get_bold_color(bcolors.PINK), "\nFirst name\n----------------"))
    newFirstNames = []
    for fn1 in range(5):
        rngFirstName1 = random.randint(0, len(dictionary) - 1)
        namePortion1 = dictionary[dictWords[rngFirstName1]]

        rngFirstName2 = random.randint(0, len(dictionary) - 1)
        namePortion2 = dictionary[dictWords[rngFirstName2]]

        firstName = namePortion1 + namePortion2
        newFirstNames.append(capitalize_first(firstName))
        print(str(fn1) + ") " + bcolors.get_color(bcolors.PINK, capitalize_first(firstName)) + ": " + dictWords[rngFirstName1] + bcolors.get_color(bcolors.PINK, " + ") + dictWords[rngFirstName2])

    for fn2 in range(5):
        rngFirstName = random.randint(0, len(dictionary) - 1)
        while capitalize_first(dictionary[dictWords[rngFirstName]]) in first_names:
            rngFirstName = random.randint(0, len(dictionary) - 1)

        firstName = dictionary[dictWords[rngFirstName]]
        newFirstNames.append(capitalize_first(firstName))
        print(str(fn2 + 5) + ") " + bcolors.get_color(bcolors.PINK, capitalize_first(firstName)) + ": " + dictWords[rngFirstName])

    saveChoice = input(bcolors.get_color(bcolors.PINK, "Save any first name? (y/n): ")).lower()
    if saveChoice == 'y':
        saveNum = input(bcolors.get_color(bcolors.PINK, "Enter first name num to save: "))
        while int(saveNum) < 0 or int(saveNum) > 9:
            saveNum = input(bcolors.get_color(bcolors.PINK, "Enter first name num to save: "))

        nameSpelling = input(bcolors.get_color(bcolors.PINK, "Enter the spelling of the name, or blank to save as is: "))
        nameMeaning = input(bcolors.get_color(bcolors.PINK, "Enter the meaning of the name: "))

        if nameSpelling == '':
            first_names[newFirstNames[int(saveNum)]] = nameMeaning
        else:
            first_names[nameSpelling] = nameMeaning
        print(newFirstNames[int(saveNum)] + bcolors.get_color(bcolors.PINK, " saved as a first name, meaning \"") + nameMeaning + bcolors.get_color(bcolors.PINK, "\""))

    print('')

def main():
    dictionary = load_json_file(DICTIONARY_FILE)
    first_names = load_json_file(FIRST_NAMES_FILE)
    last_names = load_json_file(LAST_NAMES_FILE)

    while True:
        view = "View dictionary (v), "
        translate = "Translate (t), "
        add = "Add Translation (a), "
        edit = "Edit Dict (e), "
        list = "List names (n), "
        generate = "Generate new names (nn), "
        quit = "Quit (q)"
        choice = input(bcolors.get_color(bcolors.YELLOW, view) + bcolors.get_color(bcolors.GREEN, translate) + bcolors.get_color(bcolors.CYAN, add) + bcolors.get_color(bcolors.BLUE, edit) + bcolors.get_color(bcolors.MAGENTA, list) + bcolors.get_color(bcolors.PINK, generate) + bcolors.get_color(bcolors.RED, quit) + ": ").lower()

        if choice == 'v':
            view_dictionary(dictionary)
        elif choice == 't':
            translate_sentence(dictionary)
        elif choice == 'a':
            add_translation(dictionary)
        elif choice == 'e':
            edit_dictionary(dictionary)
        elif choice == 'n':
            list_names(first_names, last_names)
        elif choice == 'nn':
            generate_new_names(dictionary, first_names, last_names)
        elif choice == 'q':
            break
        else:
            print(bcolors.get_color(bcolors.RED, "Invalid choice. Please try again."))

        save_json_file(DICTIONARY_FILE, dictionary)
        save_json_file(FIRST_NAMES_FILE, first_names)
        save_json_file(LAST_NAMES_FILE, last_names)

if __name__ == "__main__":
    main()