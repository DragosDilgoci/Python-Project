import socket
import threading

class XsiO:
#Mai jos este constructorul de initializare
    def __init__(self):
        self.board = [[" "," "," "], [" "," "," "], [" "," "," "]]
        self.turn = "X"
        self.you = "X"
        self.opponent = "O"
        self.winner = None
        self.game_over = False

        self.counter = 0
#In cadrul host_joc se stabileste o singura conexiune cu socket TCP, hostul fiind unul local.
    def host_joc(self, host, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host,port))
        server.listen(1)
        client, addr = server.accept()
#server.accept indica faptul ca hostul accepta o conexiune de la un client TCP.
        self.you = "X"
        self.opponent="O"
        threading.Thread(target=self.conexiune, args=(client,)).start()
        server.close()
#In cadrul conectare_la_joc, se realizeaza conexiunea la hostul creat mai sus.
    def conectare_la_joc(self, host, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,port))
#client.connect transmite cererea clientului de a se conecta la host, aceasta fiind acceptata cu server.accept
        self.you="O"
        self.opponent="X"
        threading.Thread(target=self.conexiune, args=(client,)).start()
#In cadrul conexiune se realizeaza logica jocului (daca este randul meu, spun unde vreau sa mut
#daca mutarea este posibila, mutarea se realizeaza, dupa care vine randul jucatorului 2).
    def conexiune(self, client):
        while not self.game_over:
            if self.turn == self.you:
                move = input("Introduceti o mutare (linie, coloana): ")
                if self.verifica_mutare(move.split(',')):
                    client.send(move.encode('utf-8'))
                    self.aplica_mutare(move.split(','), self.you)
                    self.turn = self.opponent
                else:
                    print("Mutare indisponibila!")
            else:
                data = client.recv(1024)
                if not data:
                    break
                else:
                    self.aplica_mutare(data.decode('utf-8').split(','), self.opponent)
                    self.turn = self.you
        client.close()
#Functia aplica_mutare pune simbolurile jucatorilor in pozitiile cerute daca jocul nu este terminat.
#Daca este terminat, verifica cine a castigat si afiseaza mesajul,
#iar daca s-au terminat toate cele 9 mutari si nu avem castigator se considera remiza.
    def aplica_mutare(self, move, player):
        if self.game_over:
            return
        self.counter += 1
        self.board[int(move[0])][int(move[1])] = player
        self.print_board()
        if self.verifica_castig():
            if self.winner == self.you:
                print("Ai castigat!")
                exit()
            elif self.winner == self.opponent:
                print("Ai pierdut!")
                exit()
        else:
            if self.counter == 9:
                print("Remiza!")
                exit()
#Mutarea este valida daca zona este goala.
    def verifica_mutare(self, move):
        return self.board[int(move[0])][int(move[1])] == " "
#Verifica toate variantele de castig, daca avem linie, coloana sau diagonala.
    def verifica_castig(self):
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != " ":
                self.winner = self.board[row][0]
                self.game_over = True
                return True
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                self.winner = self.board[0][col]
                self.game_over = True
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            self.winner = self.board[0][0]
            self.game_over = True
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            self.winner = self.board[0][2]
            self.game_over = True
            return True
        return False
#Printeaza tabla.
    def print_board(self):
        for row in range(3):
            print(" | ".join(self.board[row]))
            if row != 2:
                print("---------")
#Rularea jocului. In cazul acesta, jucatorul este client.
game = XsiO()
game.conectare_la_joc("localhost", 4123)
