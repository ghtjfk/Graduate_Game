import pygame
import sys

# 색깔 정의
white = (255, 255, 255)
black = (0, 0, 0)

# 화면 크기 및 맵 크기 설정
screen_width = 800
screen_height = 600
map_width = 1600
map_height = 600

def runGame(screen, clock, player_image, background_stage1_1, background_stage1_2):
    # 플레이어 설정
    player_width = 50
    player_height = 50
    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height - player_height - 10
    player_speed = 10
    jump_height = 20

    # 플레이어의 초기 속도 및 중력 설정
    player_velocity_y = 0
    gravity = 1.5

    # 카메라 설정
    camera_x = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # 키 입력에 따라 플레이어의 위치 조정
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < map_width - player_width:
            player_x += player_speed
        if keys[pygame.K_SPACE] and player_y == screen_height - player_height - 10:
            player_velocity_y = -jump_height

        # 중력 적용
        player_velocity_y += gravity
        player_y += player_velocity_y

        # 바닥에 닿으면 중력 초기화
        if player_y > screen_height - player_height - 10:
            player_y = screen_height - player_height - 10
            player_velocity_y = 0

        # 카메라 위치 조정
        camera_x = player_x - screen_width // 2.5

        # 배경 그리기 (맵의 배경)
        screen.fill(white)  # 화면을 흰색으로 지우기
        screen.blit(background_stage1_1, (0 - camera_x - screen_width // 2, 0))
        screen.blit(background_stage1_2, (screen_width - camera_x, 0))

        # 맵을 카메라 위치에 따라 그리기
        screen.blit(player_image, (player_x - camera_x, player_y))

        # 화면 업데이트
        pygame.display.flip()

        # FPS 설정
        clock.tick(30)

def initGame():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("플랫폼 게임")
    player_image = pygame.Surface((50, 50))
    player_image.fill(white)
    background_stage1_1 = pygame.image.load("송민학교1.png")
    background_stage1_1 = pygame.transform.scale(background_stage1_1, (map_width, map_height))
    background_stage1_2 = pygame.image.load("송민학교2.png")
    background_stage1_2 = pygame.transform.scale(background_stage1_2, (map_width, map_height))

    # 메인 루프
    clock = pygame.time.Clock()
    runGame(screen, clock, player_image, background_stage1_1, background_stage1_2)

if __name__ == '__main__':
    initGame()