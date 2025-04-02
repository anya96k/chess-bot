import chess
import chess.engine
import tkinter as tk
from tkinter import messagebox, scrolledtext, Entry, Button
from PIL import Image, ImageTk
import os

STOCKFISH_PATH = r"D:\Chess Bot\stockfish\stockfish-windows-x86-64-avx2.exe"
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chess Chatbot")
        self.board = chess.Board()

        # Layout
        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack(side=tk.LEFT)

        self.chatbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=20)
        self.chatbox.pack(pady=10, padx=10)
        self.chatbox.insert(tk.END, "AI: Welcome to AI Chess Bot! Type 'help' for instructions.\n")

        self.user_input = Entry(root, width=50)
        self.user_input.pack(pady=5)
        self.user_input.bind("<Return>", self.process_query)

        self.send_button = Button(root, text="Send", command=self.process_query)
        self.send_button.pack()

        self.images = {}  
        self.selected_square = None
        self.load_images()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def load_images(self):
        """Load chess piece images."""
        pieces = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        for piece in pieces:
            white_img = Image.open(os.path.join("pieces", f"w_{piece}.png")).resize((50, 50), Image.Resampling.LANCZOS)
            black_img = Image.open(os.path.join("pieces", f"b_{piece}.png")).resize((50, 50), Image.Resampling.LANCZOS)
            self.images[f"w_{piece}"] = ImageTk.PhotoImage(white_img)
            self.images[f"b_{piece}"] = ImageTk.PhotoImage(black_img)

    def draw_board(self):
        """Draw the chessboard and pieces."""
        self.canvas.delete("all")
        colors = ["#eeeed2", "#769656"]
        for row in range(8):
            for col in range(8):
                x0, y0 = col * 50, row * 50
                x1, y1 = x0 + 50, y0 + 50
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors[(row + col) % 2])
        self.draw_pieces()

    def draw_pieces(self):
        """Draw chess pieces on the board."""
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                piece = self.board.piece_at(square)
                if piece:
                    color_prefix = "w_" if piece.color == chess.WHITE else "b_"
                    piece_map = {chess.PAWN: "pawn", chess.ROOK: "rook", chess.KNIGHT: "knight",
                                 chess.BISHOP: "bishop", chess.QUEEN: "queen", chess.KING: "king"}
                    image_key = color_prefix + piece_map[piece.piece_type]
                    self.canvas.create_image(col * 50 + 25, row * 50 + 25, image=self.images[image_key])

    def on_click(self, event):
        """Handle piece selection and moves."""
        col, row = event.x // 50, event.y // 50
        square = chess.square(col, 7 - row)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.draw_board()
                self.selected_square = None
                self.ai_move()
            else:
                self.selected_square = None


    def process_query(self, event=None):
        query = self.user_input.get().strip().lower()
        self.display_message("You", query) 
        self.user_input.delete(0, tk.END)

        if query in ["help", "commands"]:
            response = "Commands: 'best move', 'evaluate', 'resign', 'history', 'review'"
        elif query == "best move":
            response = f"Best move: {engine.play(self.board, chess.engine.Limit(time=0.5)).move}"
        elif query == "evaluate":
            info = engine.analyse(self.board, chess.engine.Limit(time=0.5))
            score = info['score'].relative.score(mate_score=10000)
            response = f"Current evaluation: {score}"
        elif query == "history":
        # History of moves command
            move_list = [self.board.san(move) for move in self.board.move_stack]
            if move_list:
                response = "Moves so far:\n" + "\n".join(move_list)
            else:
                response = "No moves yet."
        elif query == "review":
        # Review of the game
            self.review_game()
            return  # Return early to prevent the response from being added to the chat.
        elif query == "resign":
            self.resign()
            return  # Return early to prevent the response from being added to the chat.
        else:
            response = "I don't understand. Try 'help' for commands."

        self.display_message("AI", response)

    def ai_move(self):
        """Make AI move using Stockfish and display chatbot messages."""
        if not self.board.is_game_over():
            result = engine.play(self.board, chess.engine.Limit(time=0.5))
            self.board.push(result.move)
            self.draw_board()

            # Get evaluation score for AI response
            info = engine.analyse(self.board, chess.engine.Limit(time=0.5))
            score = info["score"].relative.score(mate_score=10000)

            # AI message
            advice = self.get_chatbot_advice(score)
            self.display_message("AI", f"I played {self.board.san(result.move)}. {advice}")
        else:
            result = self.board.result()
            self.display_message("AI", f"Game Over! Result: {result}")
            self.review_game()
            self.predict_rating()

    def ai_move(self):
        """Make AI move using Stockfish and display chatbot messages."""
        if not self.board.is_game_over():
            result = engine.play(self.board, chess.engine.Limit(time=0.5))
            self.board.push(result.move)
            self.draw_board()

        # Get evaluation score for AI response
            info = engine.analyse(self.board, chess.engine.Limit(time=0.5))
            score = info["score"].relative

        # Check if score is None or checkmate
            if score is None:
                advice = "It's a complex position! Think carefully."
            elif score.is_mate():
                mate_in = score.mate()  # Check if it's mate
                advice = f"Checkmate in {mate_in} moves! Be careful!"
            else:
            # Ensure score is numeric before passing it to get_chatbot_advice
                score_value = score.score(mate_score=10000)
                advice = self.get_chatbot_advice(score_value)

        # AI message
            self.display_message("AI", f"I played {self.board.san(result.move)}. {advice}")
        else:
            result = self.board.result()
            self.display_message("AI", f"Game Over! Result: {result}")
            self.review_game()
            self.predict_rating()

    def review_game(self):
        """Summarizes the game, listing all moves and evaluating key positions."""
        summary = "Game Review:\n"
        moves = list(self.board.move_stack)
        temp_board = chess.Board()
    
        if not moves:
            summary = "No moves played yet. The game is still in its initial state."
        else:
            for i, move in enumerate(moves, start=1):
                temp_board.push(move)
                if i % 5 == 0 or i == len(moves):  # Evaluate every 5 moves or last move
                    info = engine.analyse(temp_board, chess.engine.Limit(time=0.5))
                    score = info['score']
            
                    if score.is_mate():  # If a checkmate is near
                        eval_text = f"Mate in {score.mate()}"
                    else:
                        eval_text = f"Eval: {score.relative.score(mate_score=10000)}"
            
                    summary += f"Move {i}: {temp_board.san(move)} - {eval_text}\n"

        self.display_message("AI", summary)


   


    def display_message(self, sender, message):
        """Display messages in chat format."""
        self.chatbox.insert(tk.END, f"{sender}: {message}\n")
        self.chatbox.see(tk.END)

    def resign(self):
        """Handle player resignation."""
        if messagebox.askyesno("Resign", "Are you sure you want to resign?"):
            self.display_message("AI", "You resigned. Better luck next time!")
            self.review_game()
            self.predict_rating()
            self.root.quit()

root = tk.Tk()
app = ChessApp(root)
root.mainloop()
engine.quit()
