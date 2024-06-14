import customtkinter as ctk
from customtkinter import CTkImage
import mysql.connector
import tkinter as tk
from tkinter import *
from tkinter import PhotoImage
from tkinter.simpledialog import askstring
import time
import math
import random

canvas1=None
player1=None
player2=None
mycon=mysql.connector.connect(user='root',host='localhost',password='Milkyway16',database='chess')
cursor=mycon.cursor()

white=None

#print(mycon.is_connected())

#cursor.execute('drop table if exists stats')
cursor.execute("create table if not exists stats(username varchar(50),elo float default 400, Number_of_Games int,Games_Won int, Games_Lost int)")
#cursor.execute('select * from stats')
#data=cursor.fetchall()
#for i in data:
#    print(i)

ctk.set_appearance_mode("Dark")        
ctk.set_default_color_theme("blue")    
app=None
    
class Chess(ctk.CTk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.count = 0
        self.title("Chess.com: Python Edition")    
        self.geometry("400x640")    

        pieces = [
            "♜", "♞", "♝", "♚", "♛", "♝", "♞", "♜",
            "♟", "♟", "♟", "♟", "♟", "♟", "♟", "♟",
            " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ",
            " ", " ", " ", " ", " ", " ", " ", " ",
            "♙", "♙", "♙", "♙", "♙", "♙", "♙", "♙",
            "♖", "♘", "♗", "♔", "♕", "♗", "♘", "♖"
        ]
        
        movement=0
        self.total_moves=0
        self.current_turn='#FFFFFF'
        self.buttons={}
        self.frame=ctk.CTkFrame(master=self)
        self.frame.pack()
        self.title_label = ctk.CTkLabel(self.frame, text="PyChess", font=("Arial",80))
        self.title_label.grid(row=0, columnspan=8, pady=20)
        button_width = 50
        button_height = 50
        self.selection_counter = 0
        self.selected_pawn = None
        self.castle=False        

        for i in range(8):
            for j in range(8):
                button_name = f"{chr(ord('a') + i)}{1 + j}"
                if i>3:
                    tc="#000000"
                else:
                    tc="#FFFFFF"

                if (i+j)%2==0:
                    colour='#ebca7c'
                else:
                    colour='#654321'
                button = ctk.CTkButton(self.frame, text=pieces[i*8+j], font=("Arial",30), bg_color=colour, text_color=tc, fg_color='transparent', width=button_width, height=button_height, border_width=1)
                button.grid(row=i+1, column=j, padx=0, pady=0)
                button.bind("<Button-1>", self.create_button_click_handler(button_name))
                self.buttons[button_name]=[button, pieces[i*8+j],tc,movement]

        self.Label=ctk.CTkLabel(master=self.frame, text='{} vs {}'.format(player1,player2),font=('arial',15))
        self.Label.grid(row=9,columnspan=8,pady=5)
        
        if str(white%2+1) in 'player1':
            self.starter=player1
            self.end=player2
        else:
            self.starter=player2
            self.end=player1

        self.Label2=ctk.CTkLabel(master=self.frame,text='White:{}                  Black:{}'.format(self.starter,self.end),font=('arial',15))
        self.Label2.grid(row=10,columnspan=8)
        
        self.butn1=ctk.CTkButton(master=self.frame,text='Resign',command=lambda: self.resign())
        self.butn1.grid(row=11,column=0,columnspan=8,pady=5)
      
    def create_button_click_handler(self, button_name):        
        def on_button_click(event):
            if self.selection_counter == 0:
                self.selected_pawn = button_name
                self.selection_counter = 1
            elif self.selection_counter == 1:
                self.move_pawn(button_name)
                self.selection_counter = 0
        return on_button_click

    def resign(self):
        global app
        if self.starter==player1:
            if self.total_moves%2==1:
                tk.messagebox.showinfo('Victory','Black Resigned\nWhite Wins!')
                outcome1=1
                outcome2=0
            else:
                tk.messagebox.showinfo('Victory','White Resigned\nBlack Wins!')
                outcome1=0
                outcome2=1
        else:
            if self.total_moves%2==1:
                tk.messagebox.showinfo('Victory','Black Resigned\nWhite Wins!')
                outcome1=0
                outcome2=1
            else:
                tk.messagebox.showinfo('Victory','White Resigned\nBlack Wins!')
                outcome1=1
                outcome2=0
        self.afterstuff(outcome1,outcome2)
        app.destroy()
        playtime()
            

    def turn(self,start):
        if self.total_moves!=0:
            if self.total_moves%2==1:
                self.current_turn='#000000'
            else:
                self.current_turn='#FFFFFF'

        if self.current_turn!= self.buttons[start][2]:
            return False
        else:
            return True

    def check(self, start, end):
        
        #print("start:", start, "end:", end)
        moves = []
        tile_list = []
        for letter in 'abcdefgh':
            for number in range(1, 9):
                tile_list.append(letter + str(number))

        if self.buttons[end][1]!=' ' and self.buttons[end][2]==self.buttons[start][2]:
            return False
         
        if self.buttons[start][1] == '♜' or self.buttons[start][1] == '♖':
            move_type = (ord(end[0]) - ord(start[0]), int(end[1]) - int(start[1]))
            if move_type[0] == 0 or move_type[1] == 0:
                directions = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
                              (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                              (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7),
                              (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]
                #print(move_type)
                vertical = []
                horizontal = []
                mid = []
                


                for direction in directions:
                    new_file = chr(ord(start[0]) + direction[0])
                    new_rank = int(start[1]) + direction[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        if direction[0] == 0:
                            vertical.append(new_file + str(new_rank))
                        else:
                            horizontal.append(new_file + str(new_rank))

                
                if move_type[0] == 0:
                    ve=int(math.copysign(1,move_type[1]))
                    poss_move = vertical
                    #print(ve)
                    #print(abs(move_type[1]))
                    for i in range(1,abs(move_type[1])):
                        space=start[0]+str(int(start[1])+(i*ve))
                        #print("space:", space)
                        if space in tile_list:
                            mid.append(space)
                    
                else:
                    ve=int(math.copysign(1,move_type[0]))
                    poss_move = horizontal
                    #print(ve)
                    #print(abs(move_type[0]))
                    for i in range(1,abs(move_type[0])):
                        space=chr(ord(start[0])+int(i*ve))+start[1]
                        #print("space:", space)
                        if space in tile_list:
                            mid.append(space)
                
                #print("mid:", mid)
                #for i in mid:
                #    print(self.buttons[i][1],end='')
                #print("poss_move:", poss_move)
                #print("end:", end)
                #print(all(i==' ' for i in mid))
                count=0
                for i in mid:
                    if self.buttons[i][1]==' ':
                        count+=1
                if end in poss_move and count==len(mid):
                    return True
                else:
                    return False

            else:
                return False
            
        elif self.buttons[start][1] == '♝' or self.buttons[start][1] == '♗':
            move_type = (ord(end[0]) - ord(start[0]), int(end[1]) - int(start[1]))

            if end==start:
                return False

            elif move_type[0] == move_type[1] or move_type[0] == (-1)*(move_type[1]) or (-1)*(move_type[0]) == (move_type[1]):
                directions = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
                              (1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7),
                              (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7),
                              (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]
                #print(move_type)
                upl = []
                upr = []
                downl = []
                downr = []
                mid = []
                


                for direction in directions:
                    new_file = chr(ord(start[0]) + direction[0])
                    new_rank = int(start[1]) + direction[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        if direction[0]>0 and direction[1]>0:
                            downr.append(new_file + str(new_rank))
                        elif direction[0]>0 and direction[1]<0:
                            downl.append(new_file + str(new_rank))
                        elif direction[0]<0 and direction[1]<0:
                            upl.append(new_file + str(new_rank))
                        elif move_type[0]<0 and move_type[1]>0:
                            upr.append(new_file + str(new_rank))
                
                #print(upl,'\n',upr,'\n',downl,'\n',downr)
                
                if move_type[0]>0 and move_type[1]>0:
                    poss_move = downr
                elif move_type[0]>0 and move_type[1]<0:
                    poss_move = downl
                elif move_type[0]<0 and move_type[1]<0:
                    poss_move = upl
                elif move_type[0]<0 and move_type[1]>0:
                    poss_move = upr
                
                vef=int(math.copysign(1,move_type[0]))
                ver=int(math.copysign(1,move_type[1]))
                #print('vef',vef,'ver',ver)
                #print(abs(move_type[0]),abs(move_type[1]))
                for i in range(1,abs(move_type[1])):
                    space=(chr(ord(start[0])+(i*vef)))+str(int(start[1])+(i*ver))
                    #print("space:", space)
                    if space in tile_list:
                        mid.append(space)
                    
                #print("mid:", mid)
                #for i in mid:
                #    print('mid:',self.buttons[i][1],end='')
                #print()
                #print("poss_move:", poss_move)
                #print("end:", end)
                #print(all(i==' ' for i in mid))

                count=0
                for i in mid:
                    if self.buttons[i][1]==' ':
                        count+=1
                    #print()
                if end in poss_move and count==len(mid):
                    return True
                else:
                    return False

            else:
                return False

        elif self.buttons[start][1] == '♛' or self.buttons[start][1] == '♕':
            move_type = (ord(end[0]) - ord(start[0]), int(end[1]) - int(start[1]))
            if end==start:
                return False

            elif move_type[0] == 0 or move_type[1] == 0 or move_type[0] == move_type[1] or move_type[0] == (-1)*(move_type[1]) or (-1)*(move_type[0]) == (move_type[1]):
                directions = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
                              (1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7),
                              (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7),
                              (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7),
                              (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
                              (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                              (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7),
                              (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]
                #print(move_type)
                upl = []
                upr = []
                downl = []
                downr = []
                mid = []
                vertical = []
                horizontal = []
                

                for direction in directions:
                    new_file = chr(ord(start[0]) + direction[0])
                    new_rank = int(start[1]) + direction[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        if direction[0]>0 and direction[1]>0:
                            downr.append(new_file + str(new_rank))
                        elif direction[0]>0 and direction[1]<0:
                            downl.append(new_file + str(new_rank))
                        elif direction[0]<0 and direction[1]<0:
                            upl.append(new_file + str(new_rank))
                        elif move_type[0]<0 and move_type[1]>0:
                            upr.append(new_file + str(new_rank))
                
                for direction in directions:
                    new_file = chr(ord(start[0]) + direction[0])
                    new_rank = int(start[1]) + direction[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        if direction[0] == 0:
                            vertical.append(new_file + str(new_rank))
                        else:
                            horizontal.append(new_file + str(new_rank))
                
                #print(upl,'\n',upr,'\n',downl,'\n',downr,'\n',vertical,'\n',horizontal)

                if 0 not in move_type:
                    if move_type[0]>0 and move_type[1]>0:
                        poss_move = downr
                    elif move_type[0]>0 and move_type[1]<0:
                        poss_move = downl
                    elif move_type[0]<0 and move_type[1]<0:
                        poss_move = upl
                    elif move_type[0]<0 and move_type[1]>0:
                        poss_move = upr
                    
                    vef=int(math.copysign(1,move_type[0]))
                    ver=int(math.copysign(1,move_type[1]))
                    #print('vef',vef,'ver',ver)
                    #print(abs(move_type[0]),abs(move_type[1]))
                    for i in range(1,abs(move_type[1])):
                        space=(chr(ord(start[0])+(i*vef)))+str(int(start[1])+(i*ver))
                        #print("space:", space)
                        if space in tile_list:
                            mid.append(space)
                            
                else:
                    if move_type[0] == 0:
                        ve=int(math.copysign(1,move_type[1]))
                        poss_move = vertical
                        #print(ve)
                        #print(abs(move_type[1]))
                        for i in range(1,abs(move_type[1])):
                            space=start[0]+str(int(start[1])+(i*ve))
                            #print("space:", space)
                            if space in tile_list:
                                mid.append(space)
                        
                    else:
                        ve=int(math.copysign(1,move_type[0]))
                        poss_move = horizontal
                        #print(ve)
                        #print(abs(move_type[0]))
                        for i in range(1,abs(move_type[0])):
                            space=chr(ord(start[0])+int(i*ve))+start[1]
                            #print("space:", space)
                            if space in tile_list:
                                mid.append(space)
                    
                #print("mid:", mid)
                #for i in mid:
                #    print('mid:',self.buttons[i][1],end='')
                #print()
                #print("poss_move:", poss_move)
                #print("end:", end)
                #print(all(i==' ' for i in mid))

                count=0
                for i in mid:
                    if self.buttons[i][1]==' ':
                        count+=1
                    #print()
                if end in poss_move and count==len(mid):
                    return True
                else:
                    return False

            else:
                return False
    
        elif self.buttons[start][1] == '♞' or self.buttons[start][1] == '♘':
            move_type = (ord(end[0]) - ord(start[0]), int(end[1]) - int(start[1]))

            if end==start:
                return False
            
            elif move_type[0] in (1,2,-1,-2) and move_type[1] in (1,2,-1,-2):
                directions = [(1,2),(1,-2),(2,1),(2,-1),(-1,2),(-1,-2),(-2,1),(-2,-1)]
                #print(move_type)

                poss_move=[]

                for direction in directions:
                    new_file = chr(ord(start[0]) + direction[0])
                    new_rank = int(start[1]) + direction[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                         poss_move.append(new_file + str(new_rank))

                if end in poss_move:
                    return True
                else:
                    return False

            else:
                return False

        elif self.buttons[start][1] == '♚' or self.buttons[start][1] == '♔':
            move_type = (ord(end[0]) - ord(start[0]), int(end[1]) - int(start[1]))

            self.castle=None
            
            if end==start:
                return False
            
            elif end in ['a2','h2','a7','h7'] and start in ['a4','h4']:
                self.castle=True
                return True
    
            elif move_type[0] in (1,0,-1) and move_type[1] in (1,0,-1):
                directions = [(1,0),(1,-1),(1,1),(-1,-1),(-1,1),(-1,0),(0,1),(0,-1)]
                #print(move_type)

                poss_move=[]

                for direction in directions:
                    new_file = chr(ord(start[0]) + direction[0])
                    new_rank = int(start[1]) + direction[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                         poss_move.append(new_file + str(new_rank))

                if end in poss_move:
                    return True
                else:
                    return False

            else:
                return False

        elif self.buttons[start][1] == '♟' or self.buttons[start][1] == '♙':
            move_type = (ord(end[0]) - ord(start[0]), int(end[1]) - int(start[1]))

            if end == start:
                return False
            
            elif move_type[0] in (1,0,-1,2,-2) and move_type[1] in (2,-2,1,0,-1):
                white = [(1,0)]
                we = [(1,1),(1,-1)]
                wed = []
                black = [(-1,0)]
                bed = []
                be = [(-1,-1),(-1,1)]
                normal = white+black
                extra = we+be
                #print(move_type)

                poss_move=[]

                for i in we:
                    new_file = chr(ord(start[0]) + i[0])
                    new_rank = int(start[1]) + i[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        wed.append(new_file + str(new_rank))
                #print(wed)

                for i in be:
                    new_file = chr(ord(start[0]) + i[0])
                    new_rank = int(start[1]) + i[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        bed.append(new_file + str(new_rank))
                #print(bed)

                for i in white:
                    new_file = chr(ord(start[0]) + i[0])
                    new_rank = int(start[1]) + i[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        white.append(new_file + str(new_rank))
                        white.pop(0)
                #print(white)

                for i in black:
                    new_file = chr(ord(start[0]) + i[0])
                    new_rank = int(start[1]) + i[1]
                    if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                        black.append(new_file + str(new_rank))
                        black.pop(0)
                #print(black)

                #print(self.buttons[start][2])
                #print(self.buttons[start][2]=='#FFFFFF')
                #print(end==white[0])

                re=None

                if abs(move_type[0])==2 and abs(move_type[1])==0 and self.buttons[end][1]==' ' and start in ['b1','b2','b3','b4','b5','b6','b7','b8'] and self.buttons[start][2]=='#FFFFFF':
                    if self.buttons[start][3] == 0:
                        re = True
                    else:
                        re = False
                elif abs(move_type[0])==2 and abs(move_type[1])==0 and self.buttons[end][1]==' ' and start in ['g1','g2','g3','g4','g5','g6','g7','g8'] and self.buttons[start][2]=='#000000':
                    if self.buttons[start][3]==0:
                        re = True
                    else:
                        re = False
                elif move_type[1] == 0:
                    if self.buttons[start][2] == '#FFFFFF':
                        if end == white[0] and self.buttons[end][1] == ' ':
                            re = True
                        else:
                            re = False
                    elif self.buttons[start][2] == '#000000':
                        if end == black[0] and self.buttons[end][1] == ' ':
                            re = True
                        else:
                            re = False
                else:
                    if self.buttons[start][2] == '#FFFFFF':
                        if end in wed:
                            if self.buttons[end][1] != ' ' and self.buttons[end][2] == '#000000':
                                re = True
                            else:
                                re = False
                        else:
                            re = False
                    elif self.buttons[start][2] == '#000000':
                        if end in bed:
                            if self.buttons[end][1] != ' ' and self.buttons[end][2] == '#FFFFFF':
                                re = True
                            else:
                                re = False
                        else:
                            re = False


                if re:
                    return True
                else:
                    return False

            else:
                return False
        
        else:
            return False

    def promotion(self,end):
        def on_button_click(button_text):
            self.buttons[end][1] = button_text
            self.buttons[end][0].configure(text=button_text)
            popup_window.destroy()

        popup_window = ctk.CTkToplevel()
        popup_window.title("Promotion")
        popup_window.geometry("200x150")

        btn_rook = ctk.CTkButton(popup_window, text="Rook", command=lambda: on_button_click("♜" if self.current_turn == "#FFFFFF" else "♖"))
        btn_rook.pack(pady=5)

        btn_queen = ctk.CTkButton(popup_window, text="Queen", command=lambda: on_button_click("♛" if self.current_turn == "#FFFFFF" else "♕"))
        btn_queen.pack(pady=5)

        btn_bishop = ctk.CTkButton(popup_window, text="Bishop", command=lambda: on_button_click("♝" if self.current_turn == "#FFFFFF" else "♗"))
        btn_bishop.pack(pady=5)

        btn_knight = ctk.CTkButton(popup_window, text="Knight", command=lambda: on_button_click("♞" if self.current_turn == "#FFFFFF" else "♘"))
        btn_knight.pack(pady=5)

        popup_window.grab_set()
        popup_window.mainloop()

    def castle_move(self, start, end):
        start_button = self.buttons[start][0]
        end_button = self.buttons[end][0]
        start_text = self.buttons[start][1]
        start_text_color = self.buttons[start][2]

        if start_text_color is None:
            start_text_color = "#000000"

        start_button.configure(text=" ")
        end_button.configure(text=start_text)
        end_button.configure(text_color=start_text_color)

        self.buttons[start][1] = ' '
        self.buttons[end][1] = start_text
        self.buttons[end][2] = start_text_color

        self.selection_counter = 0
        self.total_moves += 1
        self.buttons[start][3] += 1
        #print('moved')


    def castling(self, start, end):
        global x
        #print(self.buttons[start][3])
        if self.buttons[start][3] == 0 and (self.buttons[(end[0] + str(int(end[1]) - 1))][3] == 0 or self.buttons[(end[0] + str(int(end[1]) + 1))][3] == 0):
            #print('checking')
            if self.buttons[start][2] == '#FFFFFF':
                if start == 'a4' and end == 'a2' and all(self.buttons[i][1] == ' ' for i in ['a2', 'a3']):
                    self.castle_move('a4', 'a2')
                    self.castle_move('a1', 'a3')
                    #print('moving')

                elif start == 'a4' and end == 'a7' and all(self.buttons[i][1] == ' ' for i in ['a5', 'a6', 'a7']):
                    self.castle_move('a4', 'a7')
                    self.castle_move('a8', 'a6')
                    #print('moving')

                self.current_turn='#000000'
                self.total_moves+=1
                self.buttons[start][3]+=1

            else:
                if start == 'h4' and end == 'h2' and all(self.buttons[i][1] == ' ' for i in ['h2', 'h3']):
                    self.castle_move('h4', 'h2')
                    self.castle_move('h1', 'h3')
                    #print('moving')

                elif start == 'h4' and end == 'h7' and all(self.buttons[i][1] == ' ' for i in ['h5', 'h6', 'h7']):
                    self.castle_move('h4', 'h7')
                    self.castle_move('h8', 'h6')
                    #print('moving')
                    

                self.current_turn='#000000'
                self.total_moves+=1
                self.buttons[start][3]+=1
            #print('done')
        else:
            #print('l')
            tk.messagebox.showerror("Warning", "Your King or Rook has moved you cannot Castle")
            x = False
        
    def disable_buttons(self):
        for button_info in self.buttons.values():
            button = button_info[0]
            button.unbind("<Button-1>")

    def afterstuff(self,outcome1,outcome2):
        cursor.execute('select elo from stats where username="{}"'.format(player1))
        data=cursor.fetchall()
        e1=data[0][0]

        cursor.execute('select elo from stats where username="{}"'.format(player2))
        data=cursor.fetchall()
        e2=data[0][0]

        p1=(1/(1+(math.pow(10,((e2-e1)/400)))))
        p2=(1/(1+(math.pow(10,((e1-e2)/400)))))

        #print(p1,'\n',p2)

        k=32

        e1=int(e1+k*(outcome1-p1))
        e2=int(e2+k*(outcome2-p2))

        #print(e1,'\n',e2)
        
        cursor.execute('update stats set elo={},Number_of_games=Number_of_games+1 where username="{}"'.format(e1,player1))
        cursor.execute('update stats set elo={},Number_of_games=Number_of_games+1 where username="{}"'.format(e2,player2))

        if outcome1==1:
            cursor.execute('update stats set Games_won=Games_won+1 where username="{}"'.format(player1))
            cursor.execute('update stats set Games_Lost=Games_Lost+1 where username="{}"'.format(player2))
        elif outcome2==1:
            cursor.execute('update stats set Games_won=Games_won+1 where username="{}"'.format(player2))
            cursor.execute('update stats set Games_Lost=Games_Lost+1 where username="{}"'.format(player1))
            
        mycon.commit()

    def checking(self):
        global checker
        checker=[]
        #print(self.buttons)
        #print('kawalski')
        attackers=[]
        king_pos=None
        #print(king_pos)
        if (self.total_moves)%2==1:

            for i,j in self.buttons.items():
                #print(i,j[1])
                if j[1]=='♔':
                    #print(i)
                    king_pos=i
            #print(king_pos)


            for i,j in self.buttons.items():
                #print(i)
                if j[1] in ["♜", "♞", "♝", "♛", "♟"]:
                    #print('ahh')
                    attackers.append(i)

            #print(attackers)
            #print(king_pos)
            
            for i in attackers:
                if self.check(i,king_pos):
                    king_pos=None
                    checker.append(i)
                    return True

        else:
            for i,j in self.buttons.items():
                #print(i,j[1])
                if j[1]=='♚':
                    king_pos=i
                                
            for i,j in self.buttons.items():
                #print(i)
                if j[1] in ["♖", "♘", "♗", "♕", "♙"]:
                    #print('ahh')
                    attackers.append(i)

            #print(attackers)
                
            for i in attackers:
                if self.check(i,king_pos):
                    king_pos=None
                    checker.append(i)
                    return True

        king_pos=None


            
    def checkmate(self):
        global king_checked
        king_pos=None
        attackers=[]

        x = None
        
        if (self.total_moves)%2==0:
            
            for i,j in self.buttons.items():
                #print(i,j[1])
                if j[1]=='♔':
                    king_pos=i

            king_checked='♔'

            directions = [(1,0),(1,-1),(1,1),(-1,-1),(-1,1),(-1,0),(0,1),(0,-1)]

            poss_move=[]
            for direction in directions:
                new_file = chr(ord(king_pos[0]) + direction[0])
                new_rank = int(king_pos[1]) + direction[1]
                if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                     poss_move.append(new_file + str(new_rank))

            legal_moves=[]+[king_pos]
            
            for i in poss_move:
                if self.check(king_pos,i):
                    legal_moves.append(i)

            #print(legal_moves)
            self.buttons[king_pos][1]=' '

            for i,j in self.buttons.items():
                #print(i)
                if j[1] in ["♜", "♞", "♝", "♛", "♟"]:
                    #print('ahh')
                    attackers.append(i)

            count=0
            
            for i in legal_moves:
                k=self.buttons[i][1]
                self.buttons[i][1]=king_checked
                for j in attackers:
                    if self.check(j,i):
                        count+=1
                self.buttons[i][1]=k

            if count==len(legal_moves):
                x = True

        else:
                        
            for i,j in self.buttons.items():
                #print(i,j[1])
                if j[1]=='♚':
                    king_pos=i
            king_checked='♚'
            
            directions = [(1,0),(1,-1),(1,1),(-1,-1),(-1,1),(-1,0),(0,1),(0,-1)]

            poss_move=[]
            for direction in directions:
                new_file = chr(ord(king_pos[0]) + direction[0])
                new_rank = int(king_pos[1]) + direction[1]
                if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                     poss_move.append(new_file + str(new_rank))

            legal_moves=[]+[king_pos]

            for i in poss_move:
                if self.check(king_pos,i):
                    legal_moves.append(i)

            self.buttons[king_pos][1]=' '
            #print(legal_moves)

            for i,j in self.buttons.items():
                #print(i)
                if j[1] in ["♕", "♗", "♘", "♖", "♙"]:
                    #print('ahh')
                    attackers.append(i)

            count=0
            
            for i in legal_moves:
                k=self.buttons[i][1]
                self.buttons[i][1]=king_checked
                for j in attackers:
                    if self.check(j,i):
                        count+=1
                self.buttons[i][1]=k

            if count==len(legal_moves):
                x = True

        if x == True:
            self.buttons[king_pos][1]=king_checked
            return True
        else:
            self.buttons[king_pos][1]=king_checked

            

    def dont_check_urself(self,start,end):
        #print('recieved')
        king_pos=end
        #print(end)
        attackers=[]
        #print(king_pos)
        rx=None
        
        self.buttons[start][1]=' '
        
        if (self.total_moves%2 == 1):
            for pos, piece in self.buttons.items():
                if piece[1] == '♔':
                    king_pos = pos
                    break
            replace = '♔'
            
        else:
            for pos, piece in self.buttons.items():
                if piece[1] == '♚':
                    king_pos = pos
                    break
            replace = '♚'            

        if (self.total_moves%2 == 1):
            for pos, piece in self.buttons.items():
                if piece[1] in ["♜", "♞", "♝", "♛", "♟"]:
                    attackers.append(pos)
        else:
            for pos, piece in self.buttons.items():
                if piece[1] in ["♖", "♘", "♗", "♕", "♙"]:
                    attackers.append(pos)

        for attacker in attackers:
            k=self.buttons[end][1]
            self.buttons[end][1]=replace
            if self.check(attacker, king_pos):
                rx = True
            self.buttons[end][1]=k

        self.buttons[start][1]=replace
        if rx:
            return True

    def stalemate(self):
        count=0
        
        if (self.total_moves%2 == 1):
            for pos, piece in self.buttons.items():
                if piece[1] == '♔':
                    king_pos = pos
                    break            
        else:
            for pos, piece in self.buttons.items():
                if piece[1] == '♚':
                    king_pos = pos
                    break
                
        directions = [(1,0),(1,-1),(1,1),(-1,-1),(-1,1),(-1,0),(0,1),(0,-1)]

        poss_move=[]

        for direction in directions:
            print(king_pos)
            new_file = chr(ord(king_pos[0]) + direction[0])
            new_rank = int(king_pos[1]) + direction[1]
            if 'a' <= new_file <= 'h' and 1 <= new_rank <= 8:
                 poss_move.append(new_file + str(new_rank))
                 
        legal_moves=[]+[king_pos]

        for i in poss_move:
            if self.check(king_pos,i):
                legal_moves.append(i)

        for i in legal_moves:
            if self.dont_check_urself(king_pos,i):
                count+=1

        if count==len(legal_moves):
            self.afterstuff(0.5,0.5)
            return True
        else:
            return False
        
    def move_pawn(self, end_position):
        global game_over,king_checked,checker
        start=self.selected_pawn
        end=end_position
        game_over=None
        outcome1=None
        outcome2=None
        
        if self.buttons[start][1]==' ':
            tk.messagebox.showerror('Warning','Invalid Move')
        else:
            if self.turn(start):
                if self.check(start,end):

                    #if self.stalemate():
                    #    tk.messagebox.showinfo('Draw','Game ends in Stalemate')
                    #    return

                    if self.buttons[start][1] in ("♚","♔"):
                        if self.dont_check_urself(start,end):
                            tk.messagebox.showerror('Warning','Cannot move Your King into a Check')
                            return

                    print(end)
                    print(checker)
                    
                    if self.checking() and self.buttons[start][1]!=("♚" if self.current_turn == "#FFFFFF" else "♔"):
                        if end not in checker:
                            tk.messagebox.showerror('Warning','King is in Check')
                            return

                    if self.castle:
                        self.castling(start,end)
                        self.castle=False
                        return
                        
                    start_button = self.buttons[self.selected_pawn][0]
                    end_button = self.buttons[end_position][0]
                    start_text = self.buttons[self.selected_pawn][1]
                    start_text_color = self.buttons[self.selected_pawn][2]
                    end_text = self.buttons[end_position][1]
                    end_text_color = self.buttons[end_position][2]
                 

                    if start_text_color is None:
                        start_text_color = "#000000"
                    if end_text_color is None:
                        end_text_color = "#000000"

                    start_button.configure(text=" ")

                    end_button.configure(text=start_text)
                    end_button.configure(text_color=start_text_color)

                    self.buttons[start][1]=' '
                    self.buttons[end][1]=start_text
                    self.buttons[end][2]=start_text_color

                    if self.checkmate():
                        game_over=True
            
                    
                    self.selection_counter = 0
                    self.total_moves+=1
                    self.buttons[start][3]+=1
                    
                    #print('moves of',start,':',self.buttons[start][3])

                    #print(self.castle)

                    if ('h' in end and self.buttons[end][1] == '♟') or ('a' in end and self.buttons[end][1] == '♙'):
                        self.promotion(end)
                        #print("Promotion condition met")

                    else:
                        pass
                        
                    if game_over==True:
                        if king_checked=='♚':
                            self.disable_buttons()
                            tk.messagebox.showinfo('Victory','White King is in Checkmate\nBlack Wins!')

                            if self.starter == player1:
                                outcome1=0
                                outcome2=1
                            else:
                                outcome1=1
                                outcome2=0

                            self.afterstuff(outcome1,outcome2)
                            #response = tk.messagebox.askquestion("Window is destroying itself", "Do you want to extend its life by 15 seconds?")
                            #if response == 'yes':
                            app.destroy()
                            playtime()
                        else:
                            self.disable_buttons()
                            tk.messagebox.showinfo('Victory','Black King is in Checkmate\nWhite Wins!')

                            if self.starter == player1:
                                outcome1=1
                                outcome2=0
                            else:
                                outcome1=0
                                outcome2=1
                                
                            self.afterstuff(outcome1,outcome2)
                            #response = tk.messagebox.askquestion("Window is destroying itself", "Do you want to extend its life by 15 seconds?")
                            #if response == 'yes':
                            app.destroy()
                            playtime()
                            
                    print()
                        
                                
                else:
                    tk.messagebox.showerror("Warning", "Invalid Move")
            else:
                tk.messagebox.showerror('Warning','Not Your Turn')

checker=[]
king_checked=None
game_over=None
users={}
count=0
bg_image_ref = None
bg_image_ref1 = None
bg_image_ref2 = None
bg_image_ref3 = None
x=None

def handler(page,i,btnname):
    global users,player1,player2,count
    #print(users[i][0])
    #print(users[i][0].cget('text'))
        
    if users[i][0].cget('text')!='No One Is Here':
        player=users[i][0].cget('text')
        btnname.configure(text=player)
        page.destroy()
        if player==None:
            pass
        elif count==0:
            count+=1
            player1=player
        elif count==1:
            player2=player
            count=0
        #print(player1)
        #print(player2)
    else:
        tk.messagebox.showerror('Warning','No User in that slot')
    

def stuff(btnname):
    global users,bg_image_ref2
    button_clicked = btnname
    button_width = 250
    button_height = 35
    scroll_width = 260
    scroll_height= 215
    frame_width = 400
    frame_height = 350
    
    page1 = ctk.CTkToplevel()
    page1.geometry("530x530")
    page1.title("List of Users")


    bg_image_ref2 = PhotoImage(file = "bg3.png") 
    canvas1 = ctk.CTkCanvas(page1, width = 530, height = 530,bg='#2B2B2B')
    canvas1.pack(fill = "both", expand = True)
    canvas1.create_image( 0, 0, image = bg_image_ref2,  anchor = "nw")

    scroll=ctk.CTkScrollableFrame(canvas1,width=scroll_width,height=scroll_height)
    scroll.place(x=124,y=180)
    counter=0
    
    for i in range(30):
        counter += 1
        button = ctk.CTkButton(scroll, text='No One Is Here', font=("Arial", 20), text_color='#FFFFFF',
                               bg_color='#242424', width=button_width, height=button_height, border_width=0,
                               command=lambda index=counter: handler(page1, index, button_clicked)) 
        button.grid(row=i, column=0, pady=10)
        users[counter] = [button]

        
    cursor.execute('select * from stats')
    data=cursor.fetchall()
        
    for i in range(len(data)):
        users[i+1][0].configure(text=data[i][0])

    add=ctk.CTkButton(canvas1,text='Add a User',command=lambda: insert(),width=100,height=30,border_width=0,bg_color='#1F6AA5',font=('arial',20))
    add.place(x=209,y=419)
    page1.grab_set()

def insert():
    global users
    #print(users)
    name=askstring('New User','Enter your username')
    if name==None:
        return

    usernames=[]
    cursor.execute('select * from stats')
    data=cursor.fetchall()
    for i in data:
        usernames+=i[0]

    if name in usernames:
        tk.messagebox.showerror('Warning','2 Players cannot have the same name')
        return
    
    cursor.execute('insert into stats values("{}",800,0,0,0)'.format(name))
    cursor.execute('select * from stats')
    data=cursor.fetchall()
    
    for i in range(len(data)):
        users[i+1][0].configure(text=data[i][0])

    mycon.commit()

    #for i in data:
    #   print(i)


def select_players():
    global bg_image_ref1
    page = ctk.CTkToplevel()
    page.geometry("530x530")
    page.title("Users")

    bg_image_ref1 = PhotoImage(file = "bg2.png") 
    canvas1 = ctk.CTkCanvas(page, width = 530, height = 530,bg='#2B2B2B')
    canvas1.pack(fill = "both", expand = True)
    canvas1.create_image( 0, 0, image = bg_image_ref1,  anchor = "nw")
    
    btn1 = ctk.CTkButton(master=canvas1, text="Player 1", font=('arial',20),command=lambda: stuff(btn1), width=100,height=30,border_width=0,bg_color='#1F6AA5')
    btn1.place(x=216,y=268)

    btn2 = ctk.CTkButton(master=canvas1, text="Player 2", font=('arial',20),command=lambda: stuff(btn2), width=100,height=30,border_width=0,bg_color='#1F6AA5')
    btn2.place(x=216,y=313)

    start = ctk.CTkButton(master=canvas1, text='Start', font=('arial',20), width=100,height=30, command=lambda: play(),border_width=0,bg_color='#1F6AA5')
    start.place(x=216,y=379)
    page.grab_set()


app=None

def play():
    global menu,app
    if player1!=None and player2!=None:
        menu.destroy()
        app = Chess()
        app.mainloop()
    else:
        if player1==None:
            tk.messagebox.showerror('Warning','Player 1 Not selected')
        else:
            tk.messagebox.showerror('Warning','Player 2 Not selected')

menu=None
def back(stats):
    stats.destroy()

def stats():
    global bg_image_ref3
    stats = ctk.CTkToplevel()
    stats.geometry("700x700")
    stats.title('Stats')

    bg_image_ref3 = PhotoImage(file="bg4.png")
    canvas1 = ctk.CTkCanvas(stats, width=700, height=700, bg='#2B2B2B')
    canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0, 0, image=bg_image_ref3, anchor="nw")

    frame = ctk.CTkScrollableFrame(stats, width=400)
    frame.place(x=140, y=300)
    
    cursor.execute("select * from stats")
    data = cursor.fetchall()

    name=ctk.CTkLabel(master=frame,text='Name',corner_radius=0,bg_color='#1F6AA5')
    name.grid(row=0,column=0,padx=2,pady=2,sticky="nsew")

    elo=ctk.CTkLabel(master=frame,text='ELO',corner_radius=0,bg_color='#1F6AA5')
    elo.grid(row=0,column=1,padx=2,pady=2,sticky="nsew")

    G=ctk.CTkLabel(master=frame,text='Games Played',corner_radius=0,bg_color='#1F6AA5')
    G.grid(row=0,column=2,padx=2,pady=2,sticky="nsew")

    W=ctk.CTkLabel(master=frame,text='Games Won',corner_radius=0,bg_color='#1F6AA5')
    W.grid(row=0,column=3,padx=2,pady=2,sticky="nsew")

    L=ctk.CTkLabel(master=frame,text='Games Lost',corner_radius=0,bg_color='#1F6AA5')
    L.grid(row=0,column=4,padx=2,pady=2,sticky="nsew")
    counter=1
    
    for i in data:
        n=ctk.CTkLabel(master=frame,text=i[0],corner_radius=0,bg_color='#1F6AA5')
        n.grid(row=counter,column=0,padx=2,pady=2,sticky="nsew")

        e=ctk.CTkLabel(master=frame,text=i[1],corner_radius=0,bg_color='#1F6AA5')
        e.grid(row=counter,column=1,padx=2,pady=2,sticky="nsew")

        g=ctk.CTkLabel(master=frame,text=i[2],corner_radius=0,bg_color='#1F6AA5')
        g.grid(row=counter,column=2,padx=2,pady=2,sticky="nsew")

        w=ctk.CTkLabel(master=frame,text=i[3],corner_radius=0,bg_color='#1F6AA5')
        w.grid(row=counter,column=3,padx=2,pady=2,sticky="nsew")

        l=ctk.CTkLabel(master=frame,text=i[4],corner_radius=0,bg_color='#1F6AA5')
        l.grid(row=counter,column=4,padx=2,pady=2,sticky="nsew")
        counter+=1

def quitpls():
    global menu
    menu.destroy()

def playtime():
    global menu,bg_image_ref,white
    white=random.randint(1,10000)
    #print(white%2+1)        
    menu = ctk.CTk()
    menu.geometry("530x530")
    menu.title("Home")

    bg_image_ref = PhotoImage(file = "bg1.png") 
    canvas1 = ctk.CTkCanvas(menu, width = 530, height = 530,bg='#2B2B2B')
    canvas1.pack(fill = "both", expand = True)
    canvas1.create_image( 0, 0, image = bg_image_ref,  anchor = "nw")
    
    playbtn = ctk.CTkButton(master=canvas1, text="Play", font=('arial',20),width=100,height=30,command=lambda: select_players(),border_width=0,bg_color='#1F6AA5')
    playbtn.place(x=216,y=242)

    statbtn = ctk.CTkButton(master=canvas1, text="Stats", font=('arial',20),width=100,height=30,border_width=0,bg_color='#1F6AA5',command=lambda: stats())
    statbtn.place(x=216,y=300)

    quitbtn = ctk.CTkButton(master=canvas1, text="Quit", font=('arial',20),width=100,height=30,border_width=0,bg_color='#1F6AA5',command=lambda: quitpls())
    quitbtn.place(x=216,y=357)
    
    menu.mainloop()
            
if __name__ == "__main__":
    playtime()
