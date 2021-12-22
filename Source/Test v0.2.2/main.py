#Pour l'export : pyinstaller -w -F -i .\Ressources\DG.ico .\interface_graphique.py
import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
import chessboard_detection
import cv2 #OpenCV
import board_basics
from game_state_classes import *
from tkinter.simpledialog import askstring
from tkinter import scrolledtext as scrtxt
import keyboard
from threading import Thread
import subprocess

def clear_logs():
    logs_text.delete('1.0', tk.END)

def add_log(log):
    logs_text.insert(tk.END,log + "\n")

def start_playing():
    # ADD TIME    
    if txbox.get() == '':
        game_state = Game_state(engine_name=combo.get())
    else:
        game_state = Game_state(time_left=int(txbox.get()), engine_name=combo.get())
    add_log("Looking for a chessboard...")
    found_chessboard, position  = chessboard_detection.find_chessboard()

    while not found_chessboard:
        found_chessboard, position  = chessboard_detection.find_chessboard()
    add_log("Found the chessboard " + position.print_custom())
    game_state.board_position_on_screen = position



    add_log("Checking if we are black or white...")
    resized_chessboard = chessboard_detection.get_chessboard(game_state)
    game_state.previous_chessboard_image = resized_chessboard

    we_are_white = board_basics.is_white_on_bottom(resized_chessboard)
    game_state.we_play_white = we_are_white
    if we_are_white:
        add_log("We are white" )
        game_state.moves_to_detect_before_use_engine = 0
    else:
        add_log("We are black")
        game_state.moves_to_detect_before_use_engine = 1
        first_move_registered = False
        while first_move_registered == False:
            # first_move_string = askstring('First move', 'What was the first move played by white?')
            first_move_string = game_state.find_black_move()
            add_log('MOVE: ' + first_move_string)
            if len(first_move_string) > 0:
                first_move = chess.Move.from_uci(first_move_string)
                first_move_registered = game_state.register_move(first_move,resized_chessboard)

        add_log("First move played by white :" + first_move_string)
    
    while True:
        window.update()
        if game_state.moves_to_detect_before_use_engine == 0:
            ev, depth, nodes = game_state.play_next_move()
            add_log(f'{"-" * 20}')
            add_log(f'Depth: {depth}')
            add_log(f'Eval: {ev}')
            add_log(f'Nodes: {nodes}')
            add_log(f'--> Time left: {game_state.time_left}')
            add_log(f'{"-" * 20}')
            logs_text.see('end')
        found_move, move = game_state.register_move_if_needed()
        if keyboard.is_pressed('alt+s'):
            game_state.kill_engine()
            clear_logs()
            label3.config(text='Status: OFF', foreground='red', font=('Times New Roman', 11, 'bold'))            
            break
        elif game_state.board.is_game_over():
            game_state.kill_engine()
            clear_logs()
            label3.config(text='Status: OFF', foreground='red', font=('Times New Roman', 11, 'bold'))
            break


def control():
    if combo.get() == 'No engine found':
        messagebox.showerror(title='Error', message='No engine found!', default='ok', icon='error')
        return
    button_start.config(state='disabled')
    while True:
        if keyboard.is_pressed('esc'):
            break
        elif keyboard.is_pressed('alt+p'):
            label3.config(text='Status: ON', foreground='green', font=('Times New Roman', 11, 'bold'))
            start_playing()
    button_start.config(state='normal')
def start_bot():
    thread = Thread(target=control)
    thread.start()

# --------------------------------------------------------------------------------------------
# GUI
window = tk.Tk()
window.geometry('')
window.title("AutoChess")
window.wm_attributes('-topmost', True)
window.iconbitmap('icon.ico')

label = Label(window, text='Time match:', font=('Times New Roman', 11))
label.grid(column=0, row=0, sticky='W', padx=5, pady=5)

label2 = Label(window, text='Choose Engine:', font=('Times New Roman', 11))
label2.grid(column=0, row=1, sticky='W', padx=5)

label3 = Label(window, text='Status: OFF', foreground='red', font=('Times New Roman', 11, 'bold'))
label3.grid(column=0, row=3, sticky='W', padx=5)

txbox = Entry(window, width=23)
txbox.grid(column=1, row=0, sticky='W', padx=5, pady=5)

logs_text = scrtxt.ScrolledText(window,width=20,height=7)
logs_text.grid(column=0, row=2, columnspan=4, padx=5, pady=5, sticky='WE')

button_start = Button(text="Start playing", command=start_bot)
button_start.grid(column=2, row=3, sticky='W', padx=5, pady=5)

combo = Combobox(window, width=20)  # Engine
program = subprocess.run('dir Engine\\*.exe /b /s', shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).stdout.decode().split('\n')
try:    
    k = program[0].split('\\').index('Engine')
    program = ['\\'.join(i.split('\\')[k+1:]).split('.exe')[0] for i in program]
except ValueError:
    program = ['No engine found']
    
combo['values'] = program
combo.current(0)
combo.grid(column=1, row=1, sticky='W', padx=5)

window.mainloop()
