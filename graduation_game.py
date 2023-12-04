import pygame
import sys
import time
from tkinter import messagebox

# 화면 크기 및 맵 크기 설정
screen_width = 1000
screen_height = 800
map_width = 4000
map_height = 800

def runGame(screen, clock, player_image, background_stage1, assignment_image, hp_images):
    # 플레이어 설정
    player_width = 100
    player_height = 100
    player_x = 50
    player_y = screen_height - player_height
    player_speed = 10
    jump_height = 20
    player_hp = 3  # 플레이어의 초기 체력

    # 플레이어의 초기 속도 및 중력 설정
    player_velocity_y = 0
    gravity = 1.5

    # 장애물(과제) 설정
    assignment_width = 100
    assignment_height = 100
    assignment_x = [1000, 2000, 3000]  # 3개의 장애물 생성
    assignment_y = screen_height - assignment_height
    assignment_speed = 20

    # 플레이어의 초기 무적 상태 및 무적 지속 시간 설정
    invincible = False
    invincible_duration = 1  # 무적 지속 시간 (초)
    invincible_start_time = 0  # 무적이 시작된 시간

    # 카메라 위치 설정
    camera_x = 0

    running = True
    
    while running and player_hp > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # 키 입력에 따라 플레이어의 위치 조정
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < map_width - player_width:
            player_x += player_speed
        if keys[pygame.K_SPACE] and player_y == screen_height - 100:
            player_velocity_y = -jump_height

        # 중력 적용
        player_velocity_y += gravity
        player_y += player_velocity_y

        # 바닥에 닿으면 중력 초기화
        if player_y > screen_height - 100:
            player_y = screen_height - 100
            player_velocity_y = 0

        # 카메라 위치 업데이트
        camera_x = player_x - screen_width/2.5

        # 배경 그리기 (맵의 배경)
        screen.blit(background_stage1, (0 - camera_x - 400, 0))

        # 플레이어를 카메라 위치에 따라 그리기
        screen.blit(player_image, (player_x - camera_x, player_y))

        # 장애물 그리기
        for i in range(3):
            screen.blit(assignment_image, (assignment_x[i] - camera_x, assignment_y))

            # 플레이어와 장애물 충돌 체크
            if (
                player_x < assignment_x[i] + assignment_width - 50 and
                player_x + player_width > assignment_x[i] + 50 and
                player_y < assignment_y + assignment_height - 50 and
                player_y + player_height > assignment_y + 50
            ):
                # 무적 상태인지 확인하고 충돌 시 처리
                if not invincible:
                    # 충돌 시 HP 감소
                    player_hp -= 1
                    # 무적 상태로 설정 및 시작 시간 기록
                    invincible = True
                    invincible_start_time = time.time()

        # 무적 상태인 경우, 1초 동안은 무적을 유지
        if invincible and time.time() - invincible_start_time > invincible_duration:
            invincible = False
                 
        # HP 이미지 표시
        if (player_hp >= 1): screen.blit(pygame.transform.scale(hp_images[player_hp], (150, 50)), (10, 10))


        # 화면 업데이트
        pygame.display.flip()

        # FPS 설정
        clock.tick(30)

    # 메시지 박스 표시
    result = messagebox.askquestion("게임 종료", "다시하시겠습니까?")
    if result == 'yes':
        runGame(screen, clock, player_image, background_stage1, assignment_image, hp_images)
    else:
        pygame.quit()
        sys.exit()

def initGame():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("졸업 게임")

    # 플레이어 이미지 로드
    player_image = pygame.image.load("player_image.png")
    player_image = pygame.transform.scale(player_image, (100, 100))

    # 배경 이미지 로드
    background_stage1 = pygame.image.load("송민학교1.png")
    background_stage1 = pygame.transform.scale(background_stage1, (map_width + 1000, map_height))

    # 장애물(과제) 이미지 로드
    assignment_image = pygame.image.load("assignment_image.png")
    assignment_image = pygame.transform.scale(assignment_image, (100, 100))

    # HP 이미지 로드
    hp_images = {
        3: pygame.image.load("hp3.png").convert_alpha(),
        2: pygame.image.load("hp2.png").convert_alpha(),
        1: pygame.image.load("hp1.png").convert_alpha(),
    }

    '''# 초기 배경 음악 로드 및 재생 (7초짜리)
    pygame.mixer.music.load("initial_music.mp3")
    pygame.mixer.music.play(1, 0.0)'''

    # 대기하며 초기 음악이 재생 완료되길 기다림
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(7)  # 대기시간 설정

    # 초기 음악이 끝나면 다른 음악으로 교체 및 반복 재생
    pygame.mixer.music.load("loop_music.mp3")
    pygame.mixer.music.play(-1)
    
    # 메인 루프
    clock = pygame.time.Clock()
    runGame(screen, clock, player_image, background_stage1, assignment_image, hp_images)

if __name__ == '__main__':
    initGame()