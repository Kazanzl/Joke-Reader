from bs4 import BeautifulSoup
import requests
from unicodedata import normalize
import re
from time import sleep
import random
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk, Image
from tkinter import messagebox
from tkinter import filedialog
import csv

class JokeReader:
    def __init__(self):
        self.counter = 0
        self.confirm_filepath = False
        self.saved_jokes = []
        self.joke_types = ['one-liners', 'puns', 'riddles', 'dad', 'computer', 'knock-knock']
        self.saved_jokes_quantity = {joke: 0 for joke in self.joke_types}
        color = {'window-bg':'#191919', 'base-bg':'#272727', 'content-bg':'#1F1F1F', 'bar-bg':'#2A2A2A'}

        self.window = tk.Tk()
        self.window.geometry('960x720')
        self.window.title('Your Daily Dose of Laughter')
        self.window.resizable(False, False)
        self.window['bg'] = color['window-bg']

        self.frm_menu = tk.Frame(self.window, bg=color['base-bg'])
        self.frm_menu.place(width=860, height=660, relx=5/96, rely=1/24)           
        
        types_of_jokes = len(self.joke_types)
        for i in range(types_of_jokes):
            if i < 3:
                self.frm_menu.columnconfigure(i, weight=1)
            self.frm_menu.rowconfigure(i, weight=1)

        lbl_welcome = tk.Label(self.frm_menu, text='Welcome To Your Joke Scraper', font=('Sylfaen', '22'),  bg=color['base-bg'], fg='white')
        lbl_welcome.grid(row=0, column=0, columnspan=3, pady=5, sticky='nsew')
        
        img_x_padding = [(10, 5), (5, 5), (5,10)]
        img_y_padding = [10, 15]
        self.checkbtns = []
        for index, types in enumerate(self.joke_types):
            #open and resize image
            #from https://stackoverflow.com/questions/4066202/resizing-pictures-in-pil-in-tkinter
            img = Image.open('images\\'+ types + '.png').resize((150, 150), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            checkbtn_value = tk.StringVar()
            checkbtn_id = tk.Checkbutton(self.frm_menu, text='\n' + types.capitalize() + '\n', image=img, variable=checkbtn_value, offvalue='', onvalue=types, 
                                      compound='top', font=('Bahnschrift', 11), bg='#343434', fg='white', selectcolor='#242124', 
                                      activebackground=color['base-bg'], activeforeground='white', borderwidth=5, indicatoron=0)
            checkbtn_id.image = img
            checkbtn = {'id':checkbtn_id, 'value':checkbtn_value}
            self.checkbtns.append(checkbtn)
            row = index//3 + 1
            column = index%3
            checkbtn_id.grid(row=row, column=column, padx=img_x_padding[column], pady=img_y_padding[row - 1])

        btn_img = Image.open('images\\button.png').resize((50, 50), Image.ANTIALIAS)
        btn_img = ImageTk.PhotoImage(btn_img)
        self.btn_scraper = tk.Button(self.frm_menu, image=btn_img, text='Click to Start ', font=('Sylfaen', 14), compound='left', command=self.web_scrape,
                                bg=color['base-bg'], fg='white', borderwidth=0, activebackground=color['base-bg'], activeforeground='#FF0266')
        self.btn_scraper.grid(row=3, column=1, ipadx=10, pady=(5,0))

        self.message = tk.StringVar()
        lbl_message_box = tk.Label(self.frm_menu, textvariable=self.message, font='Sylfaen 14', bg=color['base-bg'], fg='white')
        lbl_message_box.grid(row=4, column=0, columnspan=3, pady=5)

        style = ttk.Style()
        style.theme_use('alt')
        style.configure('Horizontal.TProgressbar', orient='horizontal', background='#7A7C79', lightcolor='#9A9B9C', darkcolor='black',troughcolor=color['base-bg'])
        self.progress_bar = ttk.Progressbar(self.frm_menu, length=400, mode='determinate')

        self.frm_container = tk.Frame(self.window, bg=color['base-bg'])
        self.frm_container.place(width=860, height=660, relx=5/96, rely=1/24)  
        self.frm_menu.tkraise()

        self.frm_container.columnconfigure(0, weight=1)
        self.frm_container.columnconfigure(1, weight=1)
        self.frm_container.columnconfigure(2, weight=1)
        self.frm_container.columnconfigure(3, weight=1)
        self.frm_container.rowconfigure(0, weight=1)
        self.frm_container.rowconfigure(1, weight=3)

        self.title = tk.StringVar()
        frm_title = tk.Frame(self.frm_container, bg=color['content-bg'], highlightbackground='slategrey', highlightcolor='slategrey', highlightthickness=5)
        frm_title.grid(row=0, column=1, columnspan=3, padx=(0, 15), pady=18, sticky='nsew')
        lbl_title = tk.Label(frm_title, textvariable=self.title, font=('Comic Sans MS', 18), bg=color['content-bg'], fg='white')
        lbl_title.pack(fill='both', expand=True)

        frm_info = tk.Frame(self.frm_container, bg=color['content-bg'], highlightbackground='slategrey', highlightcolor='slategrey', highlightthickness=5)
        frm_info.grid(row=0, column=0,columnspan=1, rowspan=3, padx=15, pady=(18, 0), sticky='nsew')
        
        frm_info.columnconfigure(0, weight=1)
        frm_info.rowconfigure(1, weight=1)

        lbl_info_title = tk.Label(frm_info, bg=color['content-bg'], fg='white', text='Stats\n&\nInfo', font=('Comic Sans MS', 18))
        lbl_info_title.grid(row=0, column=0, ipady=18, sticky='nsew')

        self.stats_and_info = tk.StringVar()
        lbl_stats_info = tk.Label(frm_info, bg=color['content-bg'], fg='white', textvariable=self.stats_and_info, font=('Comic Sans MS', 16), justify='left', anchor='n')
        lbl_stats_info.grid(row=1, column=0, pady=15, sticky='nsew')

        frm_content = tk.Frame(self.frm_container, bg=color['content-bg'], highlightbackground='slategrey', highlightcolor='slategrey', highlightthickness=5)
        frm_content.grid(row=1, column=1,columnspan=3, padx=(0, 15), sticky='nsew')

        #Text widget with disabled state and copy and paste prevention
        self.txt_content = tk.Text(frm_content, state='disabled', width=1, height=1, bd=0, bg=color['content-bg'], fg='white', wrap=tk.WORD, 
                                   font=('Comic Sans MS', '18'), selectbackground=color['content-bg'], cursor='arrow')
        self.txt_content.pack(fill='both', expand=True, padx=20, pady=20)
        #from https://stackoverflow.com/questions/65456520/how-to-stop-copy-paste-and-backspace-in-text-widget-in-tkinter
        self.txt_content.bind('<Control-v>', lambda _: 'break')
        self.txt_content.bind('<Control-c>', lambda _: 'break')

        btn_types = ['back', 'save', 'next']
        for index, types in enumerate(btn_types):
            img = Image.open('images\\' + types + '.png').resize((50, 50), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            btn = tk.Button(self.frm_container, text= '  ' + types.capitalize(), image=img, compound='left', command= lambda types=types: self.btn_callback(types),
                            font=('Comic Sans MS', 14),bg=color['base-bg'], fg='white', borderwidth=0, activebackground=color['base-bg'], activeforeground='white')
            btn.image = img
            btn.grid(row=2, column=index+1, pady=20)

        self.window.mainloop()

    def web_scrape(self):
        selected_jokes = []
        for btns in self.checkbtns:
            value = btns['value'].get()
            if value == '':
                continue
            selected_jokes.append(value)

        #return if user chose nothing
        if not selected_jokes:
            tk.messagebox.showerror("Error", "Please choose at least one category.")
            return

        #fix the checkbuttons in place 
        for btns in self.checkbtns:
            btns['id']['command'] = lambda btns=btns['id']: self.fixate_btn(btns)

        #remove command of scraping button
        #from https://stackoverflow.com/questions/17130356/remove-command-from-a-button
        self.btn_scraper['command'] = tk.NONE
        self.btn_scraper['activeforeground'] = 'white'
        self.window.update()

        jokes = []
        slices = self.progress_bar['maximum']/len(selected_jokes)
        scraping_wait_time = 5
        sleep_time = 0.1
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

        self.progress_bar.grid(row=5, column=0, columnspan=3, pady=10, ipady=8)
        self.window.update()

        for index, joke in enumerate(selected_jokes):
            url = 'https://www.rd.com/jokes/' + joke
            response = requests.get(url, headers=headers).content
            soup = BeautifulSoup(response, 'html.parser')
            scraped_jokes = soup.find_all('div', class_='card-wrapper fixed-height')
            
            for scraped_joke in scraped_jokes:
                joke_info = {'type' : joke}
                try:
                    joke_info['title'] = scraped_joke.find('h3', class_='entry-title').text
                except AttributeError:
                    continue

                scraped_content = scraped_joke.find('div', class_='content-wrapper hidden')

                scraped_paragraphs = scraped_content.find_all('p')

                #if there is no p tag, the text is in the div tag
                #if there are p tags, the text is formed by concatenating the strings inside all the p tags
                if not scraped_paragraphs:
                    content = scraped_content.text
                else:
                    #get the first string
                    content = scraped_paragraphs[0].text
                    length = len(scraped_paragraphs)
                    #for the rest of the strings, concatenate to the previous string separated by whitespace
                    for i in range(1, length):
                        content = content + ' ' + scraped_paragraphs[i].text
                
                #if the content contains [email\xa0protected], skip the joke
                encrypted = re.search('\[email\xa0protected\]', content)
                if encrypted:
                    continue

                #replace \xa0(non-breaking space) with whitespace ; \u2028(line-separator), \u2029(paragraph separator) with empty string and '?  A:', '?  A.' with '?\nA:'
                #from https://stackoverflow.com/questions/44701267/replacing-more-than-one-character-in-unicode-python
                content = re.sub(u'\xa0 |\xa0', ' ', content, flags=re.UNICODE)
                content = re.sub(u'[\u2028\u2029]', '', content, flags=re.UNICODE)
                content = re.sub('\?  A:|\?  A\.', '?\nA:', content)
                joke_info['content'] = content.strip()
                jokes.append(joke_info)

            slice_num = slices * (index+1)
            while self.progress_bar['value'] < slice_num:
                self.progress_bar['value'] += slices / (scraping_wait_time/sleep_time)
                if self.progress_bar['value'] > 100:
                    self.progress_bar['value'] = 100
                self.message.set(str(int(self.progress_bar['value'])) + ' %')
                self.window.update()
                sleep(sleep_time)
            
        random.shuffle(jokes)
        self.jokes = jokes
        self.set_up()

    def fixate_btn(self, btn):
        btn.toggle()

    def set_up(self):
        self.message.set('Success! Press Enter to Continue')
        self.window.bind('<Return>', self.start)

    def start(self, event):
        self.title.set(self.jokes[0]['title'])
        self.txt_content['state'] = tk.NORMAL
        self.txt_content.insert(1.0, self.jokes[0]['content'])
        self.txt_content['state'] = tk.DISABLED
        self.update_info()
        self.frm_container.tkraise()
        self.window.unbind('<Return>')
    
    def btn_callback(self, function):
        if function == 'back':
            if self.counter == 0:
                return
            self.counter -= 1
            self.title.set(self.jokes[self.counter]['title'])
            self.txt_content['state'] = tk.NORMAL
            #delete all the texts in Text widget first, then insert new text
            #from https://stackoverflow.com/questions/27966626/how-to-clear-delete-the-contents-of-a-tkinter-text-widget
            self.txt_content.delete('1.0', tk.END)
            self.txt_content.insert('1.0', self.jokes[self.counter]['content'])
            self.txt_content['state'] = tk.DISABLED

        elif function == 'next':
            if self.counter == len(self.jokes) - 1:
                self.title.set('Congrats!')
                self.txt_content['state'] = tk.NORMAL
                self.txt_content.delete(1.0, tk.END)
                self.txt_content.insert(1.0, 'You have reached the last joke.')
                self.txt_content['state'] = tk.DISABLED
                return
            self.counter += 1
            self.title.set(self.jokes[self.counter]['title'])
            self.txt_content['state'] = tk.NORMAL
            self.txt_content.delete(1.0, tk.END)
            self.txt_content.insert(1.0, self.jokes[self.counter]['content'])
            self.txt_content['state'] = tk.DISABLED

        else:
            if self.title.get() == 'Congrats!':
                        tk.messagebox.showinfo('End Of Joke', 'Nothing to save.')
                        return

            if not self.confirm_filepath:
                open_existing_file = tk.messagebox.askyesnocancel('Open existing file/New file', 'Saving joke to a CSV file. Press Yes to open existing file, No to save as new file. This operation will only be done once.', icon='info')
                if open_existing_file == None:
                    return
                elif open_existing_file:
                    self.filename = tk.filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
                    if not self.filename:
                        return
                    #read saved jokes from file and store info in memory
                    #get the name from the file object with .name 
                    #from https://stackoverflow.com/questions/28373288/get-file-path-from-askopenfilename-function-in-tkinter/28373515
                    with open(self.filename, 'r', newline='') as joke_file:
                        reader = csv.DictReader(joke_file)
                        for row in reader:
                            self.saved_jokes.append(row)
                            self.saved_jokes_quantity[row['type']] += 1
                else:
                    self.filename = tk.filedialog.asksaveasfilename( defaultextension=[('CSV files', '.csv')], filetypes=[('CSV files', '*.csv')])
                    if not self.filename:
                        return
                    with open(self.filename, 'a+', newline='') as joke_file:
                        #fieldnames = ['type', 'title', 'content']
                        writer = csv.writer(joke_file)
                        writer.writerow(['type', 'title', 'content'])

                self.confirm_filepath = True

            joke = self.jokes[self.counter]
            if joke in self.saved_jokes:
                tk.messagebox.showinfo('Reminder', 'This joke was saved before.')
                return

            with open (self.filename, 'a+', newline='') as joke_file:
                fieldnames = ['type', 'title', 'content']
                writer = csv.DictWriter(joke_file, fieldnames=fieldnames)
                writer.writerow(joke)
                self.saved_jokes.append(joke)
                self.saved_jokes_quantity[joke['type']] += 1
        
        self.update_info()
    
    def update_info(self):
        joke = self.jokes[self.counter]
        quantity = self.saved_jokes_quantity
        total_saved = sum(quantity.values())
   
        joke_types = self.joke_types
        basic_info = 'Category: ' + joke['type'] + '\nCurrent page: ' + str(self.counter+1) + '/' + str(len(self.jokes))
        if self.confirm_filepath:
            saved_quantity = '\n'
            for types in joke_types:
                saved_quantity += types + ': ' + str(quantity[types]) + '\n'
            most_saved_category = '\nMost saved category:'
            #find the most saved type(s) by finding the key(s) with the greatest value
            #from https://stackoverflow.com/questions/25762332/how-to-get-all-the-keys-with-the-same-highest-value
            if total_saved > 0:
                most_saved_quantity = max(quantity.values())
                most_saved_types = [k for k, v in quantity.items() if v == most_saved_quantity]
                for every_type in most_saved_types:
                    most_saved_category += '\n' + every_type 
                most_saved_category += '\n(' + str(round(most_saved_quantity/total_saved*100, 1)) + '%' + ')'

            self.stats_and_info.set(basic_info + saved_quantity + most_saved_category)
            return
        self.stats_and_info.set(basic_info)
        
                    
my_first_scraper = JokeReader()