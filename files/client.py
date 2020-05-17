import pygame as pg
from network import Network
from tile_map import TiledMap
from settings import game_settings, box_settings, client_name, maps, mouse_button
from drawing import redraw_window
from menu import Menu
from gui import Gui


pg.init()
pg.font.init()


def main():
    run = True
    gui_start = False
    clock = pg.time.Clock()
    n = Network()
    player = n.get_player()
    player_id = player.player_id
    pg.display.set_caption(client_name[str(player_id)])
    opponent_id = abs(player_id - 1)
    window = pg.display.set_mode((game_settings["GAME_SCREEN_WIDTH"], game_settings["GAME_SCREEN_HEIGHT"]))
    menu = Menu(window, n, player_id)

    while run:
        clock.tick(60)
        if not menu.both_ready():
            try:
                opponent, which_map, menu.opponent_ready = n.send(["get_info", opponent_id])
                try:
                    board = TiledMap(maps[str(which_map)], window)
                except pg.error:
                    break
            except EOFError:
                break
            for event in pg.event.get():
                menu.highlight_buttons(event)
                if event.type == pg.QUIT:
                    run = False
                    pg.quit()
            if menu.player_ready:
                menu.loading_screen()
        else:
            need_to_update = n.send(["was_loaded"])
            if need_to_update[0]:
                if player_id == 0:
                    player, opponent = need_to_update[1]
                else:
                    opponent, player = need_to_update[1]
            if not gui_start:
                board.screen.fill((168, 139, 50))
                width = game_settings["GAME_SCREEN_WIDTH"] + box_settings["BOX_WIDTH"] * 2
                height = game_settings["GAME_SCREEN_HEIGHT"]
                window = pg.display.set_mode((width, height))

                gui = Gui(window, player, player_id, which_map)
                gui_start = True
            try:
                which_player_turn, turns = n.send(["get_turn", player_id])
            except TypeError:
                break
            actual_pos = pg.mouse.get_pos()

            if opponent.last_action:
                player.react_to_event(opponent, n)

            gui.update_gui(actual_pos, player, opponent)
            player.check_result(opponent, n)
            move = redraw_window(window, board, player, opponent, which_player_turn, actual_pos, n)
            try:
                end = n.send(["end", player.player_id])
            except EOFError:
                break
            if end:
                pg.time.delay(3000)

                pg.quit()
                run = False
            else:
                if move:
                    # print("ala")
                    try:
                        n.send(["update", opponent_id])
                    except EOFError:
                        break

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        run = False
                        pg.quit()
                        break
                    if event.type == pg.MOUSEBUTTONUP and event.button == mouse_button["RIGHT"]:
                        player.clicked_hero = None
                    if event.type == pg.MOUSEBUTTONUP and event.button == mouse_button["LEFT"]:
                        if which_player_turn == player_id:
                            gui.click(actual_pos, n, player_id)
                            if not player.clicked_hero:
                                player.check_clicked_hero(actual_pos)
                            else:
                                made_action = player.action(opponent, board.object_tiles, actual_pos, gui)
                                if made_action is not None:
                                    n.send(made_action)
                                    player.clicked_hero = None
                    gui.menu.react(event)
                try:
                    opponent = n.send(["echo", opponent_id])
                except EOFError:
                    break


if __name__ == '__main__':
    main()
