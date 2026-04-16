class Player:
    def __init__(self, x, y, color):
        self.pos = [x, y]
        self.dir = [1, 0]
        self.hp = 3
        self.color = color
        self.last_move = 0

    @property
    def is_alive(self):
        return self.hp > 0

    def move(self, dx, dy, game_map, current_time, delay):
        if current_time - self.last_move < delay:
            return

        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        if 0 <= new_x < game_map.MAP_COLS and 0 <= new_y < game_map.MAP_ROWS:
            if game_map.map_grid[new_y][new_x] == 0:
                self.pos = [new_x, new_y]
                self.dir = [dx, dy]
                self.last_move = current_time