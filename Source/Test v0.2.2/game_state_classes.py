import chess #This is used to deal with the advancement in the game
import chess.engine#This is used to transform uci notations: for instance the uci "e2e4" corresponds to the san : "1. e4"
import numpy as np
from board_basics import *
import chessboard_detection
import os
import json
import pyautogui
import cv2 #OpenCV
import mss #Used to get superfast screenshots
import time #Used to time the executions
from time import perf_counter as clock


class Board_position:
    def __init__(self,minX,minY,maxX,maxY):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY

    def print_custom(self):
        return ("from " + str(self.minX) + "," + str(self.minY) + " to " + str(self.maxX) + ","+ str(self.maxY))

class Game_state:

    def __init__(self, engine_name, time_left=60):
        self.we_play_white = True #This store the player color, it will be changed later
        self.moves_to_detect_before_use_engine = -1 #The program uses the engine to play move every time that this variable is 0
        self.expected_move_to_detect = "" #This variable stores the move we should see next, if we don't see the right one in the next iteration, we wait and try again. This solves the slow transition problem: for instance, starting with e2e4, the screenshot can happen when the pawn is on e3, that is a possible position. We always have to double check that the move is done.
        self.previous_chessboard_image = [] #Storing the chessboard image from previous iteration
        self.executed_moves = [] #Store the move detected on san format
        self.engine = chess.engine.SimpleEngine.popen_uci('Engine\\' + engine_name + '.exe')#The engine used is stockfish. It requires to have the command stockfish working on the shell
        try:
            with open('config.json') as f:
                data = json.load(f)
            self.engine.configure(data)
        except:    
            pass
        self.board = chess.Board() #This object comes from the "chess" package, the moves are stored inside it (and it has other cool features such as showing all the "legal moves")
        self.board_position_on_screen = []
        self.sct = mss.mss()
        self.time_left = time_left
    
    #This function checks if the chessboard image we see fits the moves we stored
    #The only check done right now is squares have the right emptiness.
    def can_image_correspond_to_chessboard(self, move, current_chessboard_image):
        self.board.push(move)
        squares = chess.SquareSet(chess.BB_ALL)
        for square in squares:
            row = chess.square_rank(square)
            column = chess.square_file(square)
            piece = self.board.piece_at(square)
            shouldBeEmpty = (piece == None)
                
            if self.we_play_white == True:
                #print("White on bottom",row,column,piece)
                rowOnImage = 7-row
                columnOnImage = column
            else:
                #print("White on top",row,7 - column,piece)
                rowOnImage = row
                columnOnImage = 7-column

            squareImage = get_square_image(rowOnImage,columnOnImage,current_chessboard_image)
            if is_square_empty(squareImage) != shouldBeEmpty:
                self.board.pop()
##                print('Note:', is_square_empty(squareImage, 1))
##                print('Is_empty:', is_square_empty(squareImage))
##                print('Should be empty:', shouldBeEmpty)
##                print( "Problem with : ", self.board.uci(move) ," the square ", rowOnImage, columnOnImage, "should ",'be empty' if shouldBeEmpty else 'contain a piece')
                return False
        self.board.pop()
        return True


    def get_valid_move(self, potential_starts, potential_arrivals, current_chessboard_image):
##        print('****>', potential_starts, potential_arrivals)
        valid_move_string = ""
        for start in potential_starts:
            for arrival in potential_arrivals:
                # IMPORTANT
                if start == arrival:
                    continue
                uci_move = start+arrival
                
                move = chess.Move.from_uci(uci_move)
                if move in self.board.legal_moves:
                    if self.can_image_correspond_to_chessboard(move,current_chessboard_image):#We only keep the move if the current image looks like this move happenned
                        valid_move_string = uci_move
                else:
                    uci_move_promoted = uci_move + 'q'
                    promoted_move = chess.Move.from_uci(uci_move_promoted)
                    if promoted_move in self.board.legal_moves:
                        if self.can_image_correspond_to_chessboard(move,current_chessboard_image):#We only keep the move if the current image looks like this move happenned
                            valid_move_string = uci_move_promoted
                            print("There has been a promotion to queen")
                    
        #Detect castling king side with white
        if ("e1" in potential_starts) and ("h1" in potential_starts) and ("f1" in potential_arrivals) and ("g1" in potential_arrivals):
            valid_move_string = "e1g1"

        #Detect castling queen side with white
        if ("e1" in potential_starts) and ("a1" in potential_starts) and ("c1" in potential_arrivals) and ("d1" in potential_arrivals):
            valid_move_string = "e1c1"

        #Detect castling king side with black
        if ("e8" in potential_starts) and ("h8" in potential_starts) and ("f8" in potential_arrivals) and ("g8" in potential_arrivals):
            valid_move_string = "e8g8"

        #Detect castling queen side with black
        if ("e8" in potential_starts) and ("a8" in potential_starts) and ("c8" in potential_arrivals) and ("d8" in potential_arrivals):
            valid_move_string = "e8c8"
        
        return valid_move_string

    def register_move_if_needed(self):
        #cv2.imshow('old_image',self.previous_chessboard_image)
        #k = cv2.waitKey(10000)                
        new_board = chessboard_detection.get_chessboard(self)
        potential_starts, potential_arrivals = get_potential_moves(self.previous_chessboard_image,new_board,self.we_play_white)
        valid_move_string1 = self.get_valid_move(potential_starts,potential_arrivals,new_board)

        if len(valid_move_string1) > 0:
            time.sleep(0.1)    
            'Check that we were not in the middle of a move animation'
            new_board = chessboard_detection.get_chessboard(self)
            potential_starts, potential_arrivals = get_potential_moves(self.previous_chessboard_image,new_board,self.we_play_white)
            valid_move_string2 = self.get_valid_move(potential_starts,potential_arrivals,new_board)
            if valid_move_string2 != valid_move_string1:
                return False, "The move has changed"
            valid_move_UCI = chess.Move.from_uci(valid_move_string1)
            valid_move_registered = self.register_move(valid_move_UCI,new_board) 
##            print('Receive:', valid_move_string1)
            return True, valid_move_string1
        return False, "No move found"
        
        

    def register_move(self,move,board_image):
        if move in self.board.legal_moves:
            self.executed_moves= np.append(self.executed_moves,self.board.san(move))
            self.board.push(move)
            self.moves_to_detect_before_use_engine = self.moves_to_detect_before_use_engine - 1
            self.previous_chessboard_image = board_image
##            print('Register:', move)
            return True
        else:
            return False

    def get_square_center(self,square_name):
        row,column = convert_square_name_to_row_column(square_name,self.we_play_white)
        position = self.board_position_on_screen
        centerX = int(position.minX + (column + 0.5) *(position.maxX-position.minX)/8)
        centerY = int(position.minY + (row + 0.5) *(position.maxY-position.minY)/8)
        return centerX,centerY

    def find_black_move(self):        
        return fblack_move(self.previous_chessboard_image)

    def play_next_move(self):
        def solve_num(a):
            a = a[::-1]
            k = len(a)//3 if len(a)%3 != 0 else len(a)//3 - 1
            for i in range(1, k+1):
                a = a[:3*i + i - 1] + '.' + a[3*i + i - 1:]
            a = a[::-1]
            return a
        
        t1 = clock()
        if self.we_play_white:
            engine_process = self.engine.play(self.board, chess.engine.Limit(white_clock=self.time_left),
                                              info=chess.engine.INFO_SCORE, ponder=True)
            try:                
                evaluate = engine_process.info['score'].white()
            except:
                evaluate = ''
        else:
            engine_process = self.engine.play(self.board, chess.engine.Limit(black_clock=self.time_left),
                                              info=chess.engine.INFO_SCORE, ponder=True)
            try: 
                evaluate = engine_process.info['score'].black()
            except:
                evaluate = ''
##        print(engine_process)
        try:
            if evaluate.is_mate() and evaluate != '':
                if evaluate.score(mate_score=100000) >= 0:
                    evaluate = f'Win in {(100000 - evaluate.score(mate_score=100000))}'
                else:
                    evaluate = f'Lose in {(100000 - evaluate.score(mate_score=100000))}'
            else:
                evaluate = str(evaluate.score(mate_score=100000))
            depth = str(engine_process.info['depth']) + '-' + str(engine_process.info['seldepth'])
            nodes = solve_num(str(engine_process.info['nodes']))
        except:
            evaluate = ''
            depth = ''
            nodes = ''

        

        best_move = engine_process.move
        best_move_string = best_move.uci()
        
        origin_square = best_move_string[0:2]
        destination_square = best_move_string[2:4]
        

        #From the move we get the positions:
        centerXOrigin, centerYOrigin = self.get_square_center(origin_square)
        centerXDest, centerYDest = self.get_square_center(destination_square)

        #Having the positions we can drag the piece:
        pyautogui.moveTo(centerXOrigin, centerYOrigin)
        pyautogui.dragTo(centerXOrigin, centerYOrigin + 1, button='left') #This small click is used to get the focus back on the browser window
        pyautogui.dragTo(centerXDest, centerYDest, button='left')

        if best_move.promotion != None:
            #Deal with queen promotion:
            cv2.waitKey(100)
            pyautogui.dragTo(centerXDest, centerYDest + 1, button='left', duration=0.1) #Always promoting to a queen
        t2 = clock()
        self.time_left -= round(t2 - t1, 3)
##        print('--[Output]>', best_move_string)
##        print('Time left:', self.time_left, 'seconds')
        self.moves_to_detect_before_use_engine = 2
        return evaluate, depth, nodes

    def kill_engine(self):
        self.engine.quit()

