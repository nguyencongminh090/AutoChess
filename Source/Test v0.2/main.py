#Pour l'export : pyinstaller -w -F -i .\Ressources\DG.ico .\interface_graphique.py
import tkinter as tk
from tkinter.ttk import *
import chessboard_detection
import cv2 #OpenCV
import board_basics
from game_state_classes import *
from tkinter.simpledialog import askstring
from tkinter import scrolledtext as scrtxt

def clear_logs():
    logs_text.delete('1.0', tk.END)

def add_log(log):
    logs_text.insert(tk.END,log + "\n")

def stop_playing():
    clear_logs()
    button_start = tk.Button(text="Start playing - RESTART NOT WORKING YET", command =start_playing)
    button_start.grid(column=0,row =1)

def start_playing():
    # ADD TIME
    if txbox.get() == '':
        game_state = Game_state()
    else:
        game_state = Game_state(int(txbox.get()))
    add_log("Looking for a chessboard...")
    found_chessboard, position  = chessboard_detection.find_chessboard()

    if found_chessboard:
        add_log("Found the chessboard " + position.print_custom())
        game_state.board_position_on_screen = position
    else:
        add_log("Could not find the chessboard")
        add_log("Please try again when the board is open on the screen\n")
        return
    

    button_start = tk.Button(text="Stop playing", command =stop_playing)
    button_start.grid(column=0,row =1)



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
            first_move_string = askstring('First move', 'What was the first move played by white?')
            if len(first_move_string) > 0:
                first_move = chess.Move.from_uci(first_move_string)
                first_move_registered = game_state.register_move(first_move,resized_chessboard)

        add_log("First move played by white :"+ first_move_string)        
    
    while True:
        window.update()
        if game_state.moves_to_detect_before_use_engine == 0:
            #add_log("Our turn to play:")
            game_state.play_next_move()
            #add_log("We are done playing")
        found_move, move = game_state.register_move_if_needed()
        if found_move:
            clear_logs()
            add_log("The board :\n" + str(game_state.board) + "\n")
            add_log("\nAll moves :\n" + str(game_state.executed_moves))
    

# --------------------------------------------------------------------------------------------
# GUI
window = tk.Tk()
#window.geometry("300x300")
window.title("ChessBot by Stanislas Heili")
window.wm_attributes('-topmost', True)
label = Label(window, text='Time:')
label.grid(column=0, row=0, padx=5, pady=5, sticky='W')

txbox = Entry(window, width=43)
txbox.grid(column=1, row=0, columnspan=2, padx=5, pady=5, sticky='WE')

button_start = Button(text="Start playing", command =start_playing)
button_start.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky='WE')

logs_text = scrtxt.ScrolledText(window,width=40,height=25)
logs_text.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky='W')


window.mainloop()
