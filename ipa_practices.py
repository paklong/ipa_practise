import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
from PyDictionary import PyDictionary
from random_word import RandomWords
import pyperclip
import pandas as pd
from datetime import datetime
import os
import json  


class Game:
    
    def __init__(self):
        # self.difficulty_to = 9999999 # >= 2000000 is easy, <= 100 is rare
        self.difficulty_from = 5000
        self.r = RandomWords()
        self.d = PyDictionary()
        self.correct = 0
        self.incorrect = 0
        self.scope = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.file_name = 'learnenglish-322106-cc3db3c569e4.json'
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.file_name, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open('learning_log').sheet1



    def get_excel(self):
        df = pd.read_excel('learning_log.xlsx',engine='openpyxl')
        return df

    def write_excel(self, df, text, phoneme, meaning, message, link):
        di = {
            'Date':[datetime.now().strftime('%Y-%m-%d')],
            'Text':[text],
            'Phoneme':[phoneme],
            'Meaning':[meaning],
            'Message':[message],
            'Link':[link]
        }
        df2 = pd.DataFrame(di)
        df3 = df.append(df2)
        df3.to_excel('learning_log.xlsx', index=False, engine='openpyxl')
        return f'Written {text} to excel.'

    def write_google_sheet(self, text, phoneme, meaning, message, link):
        row = [
            datetime.now().strftime('%Y-%m-%d'),
            text, phoneme, json.dumps(meaning), message, link
        ]
        self.sheet.append_row(row, value_input_option='USER_ENTERED')
        return f'Written {text} to google.'

    def get_phoneme(self, text):
        
        url = f'https://dictionary.cambridge.org/dictionary/english/{text}'
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
            }
        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        ph = soup.find('span', class_='us dpron-i').find('span', class_='ipa dipa lpr-2 lpl-1').text
        return ph

    def get_dict_text(self, text):

        url = f'https://dictionary.cambridge.org/dictionary/english/{text}'
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
            }
        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        ph = soup.find_all('span', class_='hw dhw')[-1].text

        return ph       
    
    def generate_new(self, check):
        
        good_to_go = False
        while not good_to_go:
            try:
                text = self.r.get_random_word(hasDictionaryDef ="true", \
                    minCorpusCount=self.difficulty_from,)
                    # maxCorpusCount=self.difficulty_to)
                # text = 'indulgence'
                # text = 'depleting'
                if check:
                    text = check

                text = self.get_dict_text(text)

                phoneme = self.get_phoneme(text)

                meaning = self.d.meaning(text)
                assert meaning
                good_to_go = True
                
            except:
                check = ''
        
        return text, phoneme, meaning

    def play(self):

        def tips(meaning):
            
            for key in meaning.keys():
                print (f'>>> {key} : {"; ".join(meaning[key])}')

        again = 'y'
        again = dict(zip(range(len(again.split())), again.split()))

        while again.get(0) == 'y':

            text, phoneme, meaning = self.generate_new(again.get(1))
            
            correct = False


            while not correct:

                print (f'>>> {phoneme}')
                answer = input("Enter answer (? for tip, ! for give up, * for skip): ")

                if answer == text.lower():
                    message = 'Correct'
                    self.correct += 1
                    correct = True

                elif answer == '?':
                    os.system('clear')
                    tips(meaning)
                    

                elif answer == '!':
                    message = 'It\'s ok.'
                    self.incorrect += 1
                    correct = True
                
                elif answer == '*':
                    message = 'Skipped'
                    correct = True

                else:
                    os.system('clear')
                    print (f'>>> Incorrect, try again.')

            os.system('clear')
            print (f'>>> {message}.')
            print (f'>>> {text}')
            print (f'>>> {phoneme}')
            tips(meaning)
            pyperclip.copy(text)
            link = f'https://dictionary.cambridge.org/dictionary/english/{text}'
            print (f'>>> Learn more here: {link}')
            # df = self.get_excel()
            # self.write_excel(df, text, phoneme, meaning, message, link)
            self.write_google_sheet(text, phoneme, meaning, message, link)
            again = input("Again? (y/n): ")
            again = dict(zip(range(len(again.split())), again.split()))
            os.system('clear')



        end_message = (
            '>>> Thanks for playing\n'
            f'Total words: {self.correct+self.incorrect}\n'
            f'Correct: {self.correct}\n'
            f'Incorrect: {self.incorrect}\n'
            f'Marks: {int(100*self.correct/(self.correct+self.incorrect))}'
        )    
        print (end_message)

os.system('clear')

game = Game()
game.play()

    

