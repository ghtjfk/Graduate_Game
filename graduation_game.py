import random
import math
import pygame
import sys
import time
from tkinter import messagebox

# 화면 크기 및 맵 크기 설정
screen_BossGame_width = 800
screen_BossGame_height = 800
screen_width = 1000
screen_height = 800
map_width = 4000
map_height = 800

# Fireball 클래스 정의
class Fireball:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        # 181도에서 359도 사이의 랜덤한 각도 설정
        angle = random.randrange(10, 170)
        angle_rad = math.radians(angle)
        self.direction_x = math.cos(angle_rad)
        self.direction_y = math.sin(angle_rad)

    def move(self):
        self.rect.x += self.speed * self.direction_x
        self.rect.y += self.speed * self.direction_y

        # 벽에 닿았을 때 반사
        if self.rect.x <= 0 or self.rect.x >= screen_width - self.rect.width:
            self.direction_x *= -1  # x 방향 반전

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)

class Block:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, camera_x):
        block_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(block_surface, (0, 0, 0, 180), (0, 0, self.rect.width, self.rect.height))
        screen.blit(block_surface, (self.rect.x - camera_x, self.rect.y))

    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
    
class MovingBlock(Block):
    def __init__(self, x, y, width, height, min_y, max_y, speed):
        super().__init__(x, y, width, height)
        self.min_y = min_y
        self.max_y = max_y
        self.speed = speed

    def move(self):
        self.rect.y += self.speed

        # 블록이 최소 높이에 도달하거나 최대 높이에 도달하면 방향을 바꿈
        if self.rect.y <= self.min_y or self.rect.y >= self.max_y:
            self.speed *= -1
    
class Item:
    def __init__(self, x, y, width, height, image_path):
        self.rect = pygame.Rect(x, y, width, height)
        item_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(item_image, (width, height))

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)

def initGame():

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("졸업 게임")

    # 플레이어 이미지 로드
    player_image = pygame.image.load("player_image.png")
    player_image = pygame.transform.scale(player_image, (100, 100))

    # 배경 이미지 로드
    background_stage = pygame.image.load("미래관.png")
    background_stage = pygame.transform.scale(background_stage, (map_width + 1000, map_height))

    # 장애물(과제) 이미지 로드
    assignment_image = pygame.image.load("assignment_image.png")
    assignment_image = pygame.transform.scale(assignment_image, (130, 130))

    # 장애물(가시) 이미지 로드
    thorn_image = pygame.image.load("thorn.png")
    thorn_image = pygame.transform.scale(thorn_image, (1400, 100))

    # HP 이미지 로드
    hp_images = {
        3: pygame.image.load("HP3.png").convert_alpha(),
        2: pygame.image.load("HP2.png").convert_alpha(),
        1: pygame.image.load("HP1.png").convert_alpha(),
    }

    door_image = pygame.image.load("door.png")
    door_image = pygame.transform.scale(door_image, (400, 500))

    # 블록 객체들 생성 및 리스트에 추가
    blocks = [
        Block(300, screen_height - 100, 100, 100),    # 폭탄 왼쪽 벽
        Block(1100, screen_height - 100, 300, 100),   # 폭탄 오른쪽 벽 + 왼쪽 계단
        Block(1400, screen_height - 200, 100, 200),   
        Block(1500, screen_height - 300, 100, 300),
        Block(3000, screen_height - 300, 100, 300),   # 오른쪽 계단
        Block(3100, screen_height - 200, 100, 200),
        Block(3200, screen_height - 100, 100, 100),
        MovingBlock(1800, screen_height - 350, 200, 50, screen_height - 650, screen_height - 250, 5),    # 가시 위 첫번째 발판
        MovingBlock(2200, screen_height - 500, 200, 50, screen_height - 650, screen_height - 250, -15),   # 가시 위 두번째 발판
        MovingBlock(2600, screen_height - 350, 200, 50, screen_height - 650, screen_height - 250, 10),    # 가시 위 세번째 발판
    ]
              
    # 아이템 객체 생성 및 리스트에 추가
    items = [Item(1200, screen_height - 400, 250, 100, "HP1.png")]

    # 점프 시 효과음 로드
    jump_sound = pygame.mixer.Sound("jump.mp3")

    # 피격 시 효과음 로드
    hit_sound = pygame.mixer.Sound("hit.mp3")

    # 아이템 획득 시 효과음 로드
    item_sound = pygame.mixer.Sound("item.mp3")

    # 게임 오버 시 효과음 로드
    gameover_sound = pygame.mixer.Sound("gameover.mp3")

    # 초기 배경 음악 로드 및 재생 (7초짜리)
    pygame.mixer.music.load("initial_music.mp3")
    pygame.mixer.music.play(1, 0.0)

    # 대기하며 초기 음악이 재생 완료되길 기다림
    '''while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(7)  # 대기시간 설정'''

    # 초기 음악이 끝나면 다른 음악으로 교체 및 반복 재생
    pygame.mixer.music.load("main_music.mp3")
    pygame.mixer.music.play(-1)
    
    # 메인 루프
    clock = pygame.time.Clock()
    runGame(
        screen,
        clock,
        player_image,
        background_stage,
        assignment_image,
        thorn_image,
        hp_images,
        door_image,
        blocks,
        items,
        jump_sound,
        hit_sound,
        item_sound,
        gameover_sound
        )

def runGame(
        screen,
        clock,
        player_image,
        background_stage,
        assignment_image,
        thorn_image,
        hp_images,
        door_image,
        blocks,
        items,
        jump_sound,
        hit_sound,
        item_sound,
        gameover_sound
        ):
    
    # 플레이어 설정
    player_width = 100
    player_height = 100
    player_x = 3500
    player_y = screen_height - player_height
    player_speed = 10
    jump_height = 20
    player_hp = 3

    # 플레이어의 초기 속도 및 중력 설정
    player_velocity_y = 0
    gravity = 1.5

    # 장애물(과제) 설정
    assignment_width = 100
    assignment_height = 100
    assignments = [
        {"x": 500, "y": screen_height - assignment_height - 15, "direction": 1},
        {"x": 700, "y": screen_height - assignment_height - 15, "direction": 1},
        {"x": 900, "y": screen_height - assignment_height - 15, "direction": 1}
    ]
    assignment_speed = 7

    thorn_width = 1400

    door_width = 300

    # 플레이어의 초기 무적 상태 및 무적 지속 시간 설정
    invincible = False
    invincible_duration = 0.5  # 무적 지속 시간 (초)
    invincible_start_time = 0  # 무적이 시작된 시간

    # 카메라 위치 설정
    camera_x = 0

    # "시험 기간" 텍스트 설정
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render('Exam Period', False, (255, 255, 255))
    textsurface = pygame.transform.scale(textsurface, (800, 100))

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
            # jump 효과음 재생
            jump_sound.play()
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
        screen.blit(background_stage, (0 - camera_x - 400, 0))

        # 플레이어를 카메라 위치에 따라 그리기
        screen.blit(player_image, (player_x - camera_x, player_y))

        # 장애물(과제) 이동 및 그리기
        for assignment in assignments:
            assignment["x"] += assignment_speed * assignment["direction"]

            # 과제가 경계에 도달하면 방향을 바꿈
            if assignment["x"] <= 400 or assignment["x"] >= 1000:
                assignment["direction"] *= -1

            screen.blit(assignment_image, (assignment["x"] - camera_x, assignment["y"]))

            # 플레이어와 과제 충돌 체크
            if (
                player_x < assignment["x"] + assignment_width - 55 and
                player_x + player_width > assignment["x"] + 55 and
                player_y < assignment["y"] + assignment_height - 55 and
                player_y + player_height > assignment["y"] + 55
            ):
                # 무적 상태인지 확인하고 충돌 시 처리
                if not invincible:
                    # 충돌 시 HP 감소
                    player_hp -= 1
                    # 무적 상태로 설정 및 시작 시간 기록
                    invincible = True
                    invincible_start_time = time.time()
                    # 피격 시 효과음 재생
                    hit_sound.play()

        # 무적 상태인 경우, 1초 동안은 무적을 유지
        if invincible and time.time() - invincible_start_time > invincible_duration:
            invincible = False
        
        # 장애물(가시) 그리기
        screen.blit(thorn_image, (1600 - camera_x, screen_height - 98))

        # thorn_image와 플레이어 간의 충돌 체크
        if (
            player_x < 1600 + thorn_width and
            player_x + player_width > 1600 and
            player_y < screen_height and
            player_y + player_height > screen_height - 100
        ):
            # 충돌 시 HP 감소 및 플레이어 위치 초기화
            hit_sound.play()    # 피격 시 효과음 재생
            player_hp -= 1
            player_x = 1200
            player_y = screen_height - 100

        # 문 그리기
        screen.blit(door_image, (3700 - camera_x, screen_height - 445))

        # door_image와 플레이어 간의 충돌 체크
        if (
            player_x < 3700 + door_width and
            player_x + player_width > 3700 and
            player_y < screen_height and
            player_y + player_height > screen_height - 400
        ):
            # 게임 오버 시 음악 중단
            pygame.mixer.music.stop()

            # 충돌 시 다음 스테이지로
            runBossGame(
                screen,
                clock,
                player_image,
                background_stage,
                assignment_image,
                thorn_image,
                hp_images,
                door_image,
                blocks,
                items,
                jump_sound,
                hit_sound,
                item_sound,
                gameover_sound
            )

        # MovingBlock들의 move 메서드 호출
        for block in blocks:
            if isinstance(block, MovingBlock):
                block.move()

        # 블록 그리기
        for block in blocks:
            block.draw(screen, camera_x)

        # 플레이어와 블록 간의 충돌 체크
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for block in blocks:
            if block.check_collision(player_rect):

                # 플레이어가 블록 위에 있는지 확인하고, 위에 있다면 y 좌표를 조정
                if player_y + player_height <= block.rect.y + 99 and player_x != 1200:
                    player_y = block.rect.y - player_height
                    player_velocity_y = 0
                    # 플레이어가 점프 중이 아니라면 바닥에 닿은 것으로 처리
                    if keys[pygame.K_SPACE]:
                        # 효과음 재생
                        jump_sound.play()
                        player_velocity_y = -jump_height

                # 가시에 닿아 리스폰 될 때 block 속으로 들어가는 오류 해결
                elif player_y + player_height <= block.rect.y + 100 and player_x == 1200:
                    player_y = block.rect.y - player_height
                    player_velocity_y = 0
                    # 플레이어가 점프 중이 아니라면 바닥에 닿은 것으로 처리
                    if keys[pygame.K_SPACE]:
                        # 효과음 재생
                        jump_sound.play()
                        player_velocity_y = -jump_height

                # 좌우 방향으로의 충돌을 확인하여 위치 조정
                else:
                    if player_x + player_width > block.rect.x and player_x < block.rect.x:
                        player_x = block.rect.x - player_width
                    elif player_x < block.rect.x + block.rect.width and player_x > block.rect.x:
                        player_x = block.rect.x + block.rect.width
                 
        # HP 이미지 표시
        if (player_hp >= 1): screen.blit(pygame.transform.scale(hp_images[player_hp], (150, 50)), (10, 10))

        # 아이템 그리기
        items[0].draw(screen, camera_x)

        # 플레이어와 아이템 충돌 체크
        if items[0].check_collision(player_rect) and player_hp <= 2:
            # 아이템 획득 효과음
            item_sound.play()
            # 충돌 시 HP 증가 및 아이템 제거
            player_hp += 1
            items[0].rect.x = -1000  # 아이템을 화면 밖으로 옮겨서 보이지 않게 함

        # "시험 기간" 텍스트 출력
        screen.blit(textsurface,(1900 - camera_x, screen_height - 200))

        # 화면 업데이트
        pygame.display.flip()

        # FPS 설정
        clock.tick(30)

    # 게임 오버 시 음악 중단
    pygame.mixer.music.stop()

    # gameover.mp3 재생
    gameover_sound.play()

    # 메시지 박스 표시
    result = messagebox.askquestion("게임 종료", "다시하시겠습니까?")
    if result == 'yes':
        # gameover.mp3 중단
        gameover_sound.stop()

        # 음악 다시 재생
        pygame.mixer.music.load("main_music.mp3")
        pygame.mixer.music.play(-1)

        # 아이템 위치 재설정
        items[0].rect.x = 1200
        items[0].rect.y = screen_height - 400
        # 게임 재시작
        runGame(
        screen,
        clock,
        player_image,
        background_stage,
        assignment_image,
        thorn_image,
        hp_images,
        door_image,
        blocks,
        items,
        jump_sound,
        hit_sound,
        item_sound,
        gameover_sound
        )
    else:
        pygame.quit()
        sys.exit()

def runBossGame(
        screen,
        clock,
        player_image,
        background_stage,
        assignment_image,
        thorn_image,
        hp_images,
        door_image,
        blocks,
        items,
        jump_sound,
        hit_sound,
        item_sound,
        gameover_sound
        ):

    # 초기 음악이 끝나면 다른 음악으로 교체 및 반복 재생
    pygame.mixer.music.load("boss_music.mp3")
    pygame.mixer.music.play(-1)

    # 보스 이미지 로드
    boss_image = pygame.image.load("boss_image.png")
    boss_image = pygame.transform.scale(boss_image, (800, 150))

    # fireball 이미지 로드
    fireball_image = pygame.image.load("fireball.png").convert_alpha()
    fireballs = []

    # 배경 이미지 로드
    boss_background_stage = pygame.image.load("코딩화면.png")
    boss_background_stage = pygame.transform.scale(boss_background_stage, (1000, 800))

    # 플레이어 설정
    player_width = 100
    player_height = 100
    player_x = 50
    player_y = screen_height - player_height
    player_speed = 10
    jump_height = 20
    player_hp = 3

    # 플레이어의 초기 속도 및 중력 설정
    player_velocity_y = 0
    gravity = 1.5

    # 플레이어의 초기 무적 상태 및 무적 지속 시간 설정
    invincible = False
    invincible_duration = 0.5  # 무적 지속 시간 (초)
    invincible_start_time = 0  # 무적이 시작된 시간

    running = True

    fireball_timer = 0
    fireball_interval = 1000

    while running and player_hp > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # 키 입력에 따라 플레이어의 위치 조정
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_BossGame_width + player_width:
            player_x += player_speed
        if keys[pygame.K_SPACE] and player_y == screen_BossGame_height - 100:
            # jump 효과음 재생
            jump_sound.play()
            player_velocity_y = -jump_height

        # 중력 적용
        player_velocity_y += gravity
        player_y += player_velocity_y

        # 바닥에 닿으면 중력 초기화
        if player_y > screen_BossGame_height - 100:
            player_y = screen_BossGame_height - 100
            player_velocity_y = 0

        # 배경 그리기 (맵의 배경)
        screen.blit(boss_background_stage, (0, 0))

        # 플레이어를 카메라 위치에 따라 그리기
        screen.blit(player_image, (player_x, player_y))

        # 보스 그리기
        screen.blit(boss_image, (100, 0))

        # Fireball 구현
        current_time = pygame.time.get_ticks()
        if current_time - fireball_timer > fireball_interval:
            fireball_timer = current_time
            # 보스 위치에서 Fireball 생성
            fireballs.append(Fireball(500, 100, fireball_image))

        for fireball in fireballs[:]:
            fireball.move()
            fireball.draw(screen)
            # 화면 아래로 넘어가면 제거
            if fireball.rect.y >= screen_height:
                fireballs.remove(fireball)

        # 플레이어와 Fireball 충돌 검사
            if fireball.check_collision(pygame.Rect(player_x, player_y, player_width, player_height)):
                if not invincible:
                    player_hp -= 1
                    fireballs.remove(fireball)
                    invincible = True
                    invincible_start_time = time.time()
                    hit_sound.play()

        # 무적 상태인 경우, 1초 동안은 무적을 유지
        if invincible and time.time() - invincible_start_time > invincible_duration:
            invincible = False
                 
        # HP 이미지 표시
        if (player_hp >= 1): screen.blit(pygame.transform.scale(hp_images[player_hp], (150, 50)), (10, 10))

        # 화면 업데이트
        pygame.display.flip()

        # FPS 설정
        clock.tick(30)

    # 게임 오버 시 음악 중단
    pygame.mixer.music.stop()

    # 메시지 박스 표시
    result = messagebox.askquestion("게임 종료", "다시하시겠습니까?")
    if result == 'yes':
        # 음악 다시 재생
        pygame.mixer.music.load("main_music.mp3")
        pygame.mixer.music.play(-1)

        # 아이템 위치 재설정
        items[0].rect.x = 1200
        items[0].rect.y = screen_BossGame_height - 400
        # 게임 재시작
        runGame(
        screen,
        clock,
        player_image,
        background_stage,
        assignment_image,
        thorn_image,
        hp_images,
        door_image,
        blocks,
        items,
        jump_sound,
        hit_sound,
        item_sound,
        gameover_sound
        )
    else:
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    initGame()