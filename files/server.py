import socket
import pickle
from game import Game
from player import Player
from _thread import start_new_thread


port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(('', port))
except socket.error as e:
    str(e)

s.listen(5)
print("Waiting for a connection, Server Started")
games = {}
id_count = 0


def threaded_client(connection, p_id, g_id):
    global id_count
    games[g_id].players[p_id] = Player(name="df", player_id=p_id)
    connection.send(pickle.dumps(games[g_id].players[p_id]))
    reply = []

    while True:
        try:
            data = pickle.loads(connection.recv(2048))

            if g_id in games:
                game = games[g_id]

                if not data:
                    break
                else:
                    which_player_take_action = data[1]
                    if data[0] == "get_info":
                        opponent_ready = game.is_ready[abs(which_player_take_action-1)]
                        reply = [game.players[which_player_take_action], game.which_map, opponent_ready]
                    if data[0] == "move":
                        moved_hero = data[2]
                        game.players[which_player_take_action].heroes[moved_hero.hero_id] = moved_hero
                        game.players[which_player_take_action].moved_hero = moved_hero
                        game.players[which_player_take_action].path = data[3]
                        game.player_turn = abs(game.player_turn - 1)
                        game.turns += 1
                        reply = game.players[which_player_take_action]
                    if data[0] == "echo":
                        reply = game.players[which_player_take_action]
                    if data[0] == "is_ready":
                        game.is_ready[abs(which_player_take_action-1)] = data[2]
                        reply = game.is_ready[which_player_take_action]
                    if data == "get_turn":
                        reply = [game.player_turn, game.turns]
                    if data[0] == "update":
                        game.players[which_player_take_action].moved_hero = None
                    print("received: ", data)
                    print("Sending: ", reply)
                    connection.sendall(pickle.dumps(reply))
            else:
                break
        except EOFError:
            break

    print("Lost connection")
    try:
        del games[game_id]
        print("Closing Game", game_id)
    except KeyError:
        pass
    id_count -= 1
    connection.close()


player_id = 0

while True:
    conn, adr = s.accept()
    print("Connected to:", adr)
    id_count += 1
    player_id = 0
    game_id = (id_count - 1) // 2
    if id_count % 2 == 1:
        games[game_id] = Game(game_id)

        print("Creating a new game...")
    else:
        player_id = 1

    start_new_thread(threaded_client, (conn, player_id, game_id))
