import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 初始化Pygame字体（支持中文）
pygame.font.init()
font_path = pygame.font.match_font('simhei')  # 使用系统字体 SimHei（黑体）

# 游戏窗口设置（调整窗口变长）
WIDTH, HEIGHT = 800, 700  # 调整宽度和高度
TILE_SIZE = 60
GRID_SIZE = 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("消消乐  -by 埃及猪肉")
clock = pygame.time.Clock()

img = pygame.image.load("logo.ico")
pygame.display.set_icon(img) # 可以填img

# 颜色定义
COLORS = [
    (255, 0, 0),    # 红色
    (0, 255, 0),    # 绿色
    (0, 0, 255),    # 蓝色
    (255, 255, 0),  # 黄色
    (255, 165, 0),  # 橙色
]

# 初始化网格
def create_grid():
    return [[random.randint(0, len(COLORS) - 1) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# 绘制网格（调整位置，水平居中，向下移动更多）
def draw_grid(grid):
    offset_x = (WIDTH - GRID_SIZE * TILE_SIZE) // 2
    offset_y = 150  # 向下移动更多
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color = COLORS[grid[y][x]]
            rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

# 检查是否有匹配的行或列
def find_matches(grid):
    matches = []
    # 检查行
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE - 2):
            if grid[y][x] == grid[y][x + 1] == grid[y][x + 2]:
                matches.append((y, x))
                matches.append((y, x + 1))
                matches.append((y, x + 2))
    # 检查列
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 2):
            if grid[y][x] == grid[y + 1][x] == grid[y + 2][x]:
                matches.append((y, x))
                matches.append((y + 1, x))
                matches.append((y + 2, x))
    return list(set(matches))

# 消除匹配的方块
def remove_matches(grid, matches):
    for y, x in matches:
        grid[y][x] = -1  # 标记为消除

# 下落并填充空白
def drop_tiles(grid):
    for x in range(GRID_SIZE):
        column = [grid[y][x] for y in range(GRID_SIZE) if grid[y][x] != -1]
        while len(column) < GRID_SIZE:
            column.insert(0, random.randint(0, len(COLORS) - 1))
        for y in range(GRID_SIZE):
            grid[y][x] = column[y]

# 动画函数：移动方块（修正闪现到左上角的问题）
def animate_swap(grid, start, end):
    sx, sy = start
    ex, ey = end
    offset_x = (WIDTH - GRID_SIZE * TILE_SIZE) // 2
    offset_y = 150  # 与绘制网格的偏移保持一致
    start_rect = pygame.Rect(offset_x + sx * TILE_SIZE, offset_y + sy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    end_rect = pygame.Rect(offset_x + ex * TILE_SIZE, offset_y + ey * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    steps = 15  # 动画帧数

    for step in range(steps + 1):
        screen.fill((240, 240, 255))  # 背景颜色
        progress = step / steps

        # 计算中间位置
        current_x = start_rect.x + (end_rect.x - start_rect.x) * progress
        current_y = start_rect.y + (end_rect.y - start_rect.y) * progress
        current_rect = pygame.Rect(current_x, current_y, TILE_SIZE, TILE_SIZE)

        # 绘制移动中的方块
        pygame.draw.rect(screen, COLORS[grid[sy][sx]], current_rect)
        pygame.draw.rect(screen, (0, 0, 0), current_rect, 2)

        # 绘制静止的方块
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if (x, y) != (sx, sy) and (x, y) != (ex, ey):
                    color = COLORS[grid[y][x]]
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        pygame.display.flip()
        clock.tick(60)

# 动画函数：优化方块落下动画（修复下方方块错误下落的问题）
def animate_drop(grid, matches):
    offset_x = (WIDTH - GRID_SIZE * TILE_SIZE) // 2
    offset_y = 150  # 与绘制网格的偏移保持一致
    steps = 10  # 动画帧数

    # 记录每列的下落距离
    drop_distances = {x: [0] * GRID_SIZE for x in range(GRID_SIZE)}
    for x in range(GRID_SIZE):
        drop = 0
        for y in range(GRID_SIZE - 1, -1, -1):
            if (y, x) in matches:
                drop += TILE_SIZE
            else:
                drop_distances[x][y] = drop

    for step in range(steps + 1):
        screen.fill((240, 240, 255))
        progress = step / steps

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if (y, x) in matches:
                    continue
                rect = pygame.Rect(
                    offset_x + x * TILE_SIZE,
                    offset_y + y * TILE_SIZE + drop_distances[x][y] * progress,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(screen, COLORS[grid[y][x]], rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        pygame.display.flip()
        clock.tick(60)

# 主菜单界面
def main_menu():
    title_font = pygame.font.Font(font_path, 60)
    button_font = pygame.font.Font(font_path, 40)
    running = True
    while running:
        screen.fill((200, 220, 255))  # 设置背景颜色

        # 绘制标题
        title_text = title_font.render("消消乐游戏", True, (0, 0, 128))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # 绘制按钮
        start_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60)
        about_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 60)
        quit_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60)

        pygame.draw.rect(screen, (0, 128, 0), start_button, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 128), about_button, border_radius=10)
        pygame.draw.rect(screen, (128, 0, 0), quit_button, border_radius=10)

        pygame.draw.rect(screen, (0, 255, 0), start_button, 3, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 255), about_button, 3, border_radius=10)
        pygame.draw.rect(screen, (255, 0, 0), quit_button, 3, border_radius=10)

        screen.blit(button_font.render("开始游戏", True, (255, 255, 255)), (WIDTH // 2 - 80, HEIGHT // 2 - 90))
        screen.blit(button_font.render("关于", True, (255, 255, 255)), (WIDTH // 2 - 40, HEIGHT // 2 + 10))
        screen.blit(button_font.render("退出游戏", True, (255, 255, 255)), (WIDTH // 2 - 80, HEIGHT // 2 + 110))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "start"
                elif about_button.collidepoint(event.pos):
                    return "about"
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# 关于界面（增加可点击超链接）
def about_screen():
    font = pygame.font.Font(font_path, 30)
    running = True
    while running:
        screen.fill((240, 240, 255))

        # 绘制关于信息
        screen.blit(font.render("消消乐游戏 - 由埃及猪肉制作", True, (0, 0, 0)), (50, 100))
        link_rect = pygame.Rect(50, 200, 500, 40)
        pygame.draw.rect(screen, (240, 240, 255), link_rect)
        screen.blit(font.render("访问: https://PatTianFang.Github.io", True, (0, 0, 255)), (50, 200))

        # 绘制确定按钮
        ok_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)
        pygame.draw.rect(screen, (0, 128, 0), ok_button, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 0), ok_button, 3, border_radius=10)
        screen.blit(font.render("确定", True, (255, 255, 255)), (WIDTH // 2 - 30, HEIGHT - 90))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.collidepoint(event.pos):
                    return
                if link_rect.collidepoint(event.pos):
                    import webbrowser
                    webbrowser.open("https://PatTianFang.Github.io")

# 游戏主循环（调用修复后的动画函数）
def main_game():
    grid = create_grid()
    selected = None
    dragging = False
    score = 0
    try:
        with open("highscore.txt", "r") as f:
            high_score = int(f.read())
    except FileNotFoundError:
        high_score = 0

    running = True
    while running:
        screen.fill((240, 240, 255))

        # 绘制返回主菜单按钮
        font = pygame.font.Font(font_path, 30)
        menu_button = pygame.Rect(10, 10, 150, 50)
        pygame.draw.rect(screen, (0, 128, 0), menu_button, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 0), menu_button, 3, border_radius=10)
        screen.blit(font.render("主菜单", True, (255, 255, 255)), (30, 20))

        # 绘制得分和历史最高分
        score_box = pygame.Rect(WIDTH - 200, 10, 180, 50)
        pygame.draw.rect(screen, (0, 0, 128), score_box, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 255), score_box, 3, border_radius=10)
        score_text = font.render(f"得分: {score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH - 190, 20))

        high_score_box = pygame.Rect(WIDTH - 200, 70, 180, 50)
        pygame.draw.rect(screen, (128, 0, 0), high_score_box, border_radius=10)
        pygame.draw.rect(screen, (255, 0, 0), high_score_box, 3, border_radius=10)
        high_score_text = font.render(f"最高分: {high_score}", True, (255, 255, 255))
        screen.blit(high_score_text, (WIDTH - 190, 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    if score > high_score:
                        with open("highscore.txt", "w") as f:
                            f.write(str(score))
                    return "menu"
                x, y = event.pos
                x = (x - (WIDTH - GRID_SIZE * TILE_SIZE) // 2) // TILE_SIZE
                y = (y - 150) // TILE_SIZE  # 与绘制网格的偏移保持一致
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    selected = (x, y)
                    dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                if dragging and selected:
                    x, y = event.pos
                    x = (x - (WIDTH - GRID_SIZE * TILE_SIZE) // 2) // TILE_SIZE
                    y = (y - 150) // TILE_SIZE  # 与绘制网格的偏移保持一致
                    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                        sx, sy = selected
                        if abs(sx - x) + abs(sy - y) == 1:  # 确保是相邻方块
                            # 动画交换
                            animate_swap(grid, (sx, sy), (x, y))
                            grid[sy][sx], grid[y][x] = grid[y][x], grid[sy][sx]
                            matches = find_matches(grid)
                            if matches:
                                score += len(matches) * 10
                                remove_matches(grid, matches)
                                animate_drop(grid, matches)  # 优化方块落下动画
                                drop_tiles(grid)
                            else:
                                # 如果没有匹配，交换回去并动画
                                animate_swap(grid, (x, y), (sx, sy))
                                grid[sy][sx], grid[y][x] = grid[y][x], grid[sy][sx]
                    selected = None
                    dragging = False

        # 检查是否有匹配
        matches = find_matches(grid)
        if matches:
            score += len(matches) * 10
            remove_matches(grid, matches)
            animate_drop(grid, matches)  # 调用修复后的动画函数
            drop_tiles(grid)

        draw_grid(grid)

        pygame.display.flip()
        clock.tick(30)

# 主程序入口
def main():
    while True:
        action = main_menu()
        if action == "start":
            result = main_game()
            if result == "menu":
                continue
        elif action == "about":
            about_screen()

if __name__ == "__main__":
    main()
