import pygame
import pymunk
import pymunk.pygame_util
import math
pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 678
BOTTOM_PANEL = 50

#game window
game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
pygame.display.set_caption('Bilard')
draw_options = pymunk.pygame_util.DrawOptions(game_screen)

#pymunk initialization
game_space = pymunk.Space()
static_body = game_space.static_body

diameter = 36
pocket_diameter = 66
taking_shot = True
shoot_force = 0
max_force = 10000
force_direction = 1

powering_up = False
cue_ball_potted = False
potted_balls = []
# clock
clock = pygame.time.Clock()
FPS = 120

# game colors
background = (50, 50, 50)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (34, 134, 216)

# fonts
font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

# load images
cue_img = pygame.image.load('Assets\PoolCue2.png').convert_alpha()
# game_cue = pygame.transform.scale(cue_img, (650, 50))
table_img = pygame.image.load('Assets\PoolTable2.png').convert_alpha()
balls_img = []
for i in range(1, 17):
    ball_img = pygame.image.load(f"Assets/PoolBalls{i}.png").convert_alpha()
    balls_img.append(ball_img)

#function for outputting text onto the screen
def DrawText(text, font, text_col, x, y):
  imagie = font.render(text, True, text_col)
  game_screen.blit(imagie, (x, y))

def CreateBalls(radius, position):
    body = pymunk.Body()
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.mass = 10
    shape.elasticity = 0.8

    #pivot joint for friction
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_force = 100 #emiulate friction
    pivot.max_bias = 0 #disable joint corection
    game_space.add(body, shape, pivot)
    return shape

balls = []
rows = 5
for colum in range(5):
    for row in range(rows):
        ofset = colum * diameter/2
        balls_position = (250 + (colum * (diameter + 1)), 267 + (row * (diameter + 1)) + ofset)
        new_ball = CreateBalls(diameter/2, balls_position)
        balls.append(new_ball)
    rows -= 1

cue_ball_position = (888, SCREEN_HEIGHT / 2)

cue_ball = CreateBalls(diameter / 2, cue_ball_position)
balls.append(cue_ball)


#create six pockets on table
pockets = [
  (55, 63),
  (592, 48),
  (1134, 64),
  (55, 616),
  (592, 629),
  (1134, 616)
]

cushions = [
    [(88, 56), (109, 77), (555, 77), (564, 56)],
    [(621, 56), (630, 77), (1081, 77), (1102, 56)],
    [(89, 621), (110, 600), (556, 600), (564, 621)],
    [(622, 621), (630, 600), (1081, 600), (1102, 621)],
    [(56, 96), (77, 117), (77, 560), (56, 581)],
    [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
]

def CreateCushions(coordinates):
    body = pymunk.Body(body_type = pymunk.Body.STATIC)
    body.position = ((0, 0))
    shape = pymunk.Poly(body, coordinates)
    shape.elasticity = 0.8

    game_space.add(body, shape)

for n in cushions:
    CreateCushions(n)

#create pool cue
class PoolCue():
  def __init__(self, position):
    self.original_image = cue_img
    # self.original_image = game_cue
    self.angle = 0
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = position

  def update(self, angle):
    self.angle = angle

  def draw(self, surface):
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    surface.blit(self.image,
      (self.rect.centerx - self.image.get_width() / 2,
      self.rect.centery - self.image.get_height() / 2)
     )

pool_cue = PoolCue(balls[-1].body.position)

# create power bars to show how hard the cue ball will be hit
power_bar = pygame.Surface((10, 20))
power_bar.fill(BLUE)
# game loop

run_game = True
powering_up = False
lives = 3
def ManageBalls():
    lives = 3

while run_game:

    clock.tick()
    game_space.step(1 / FPS)
    # fill background
    game_screen.fill(background)
    # draw pool table
    game_screen.blit(table_img, (0, 0))

    # check if any balls have been potted
    for i, ball in enumerate(balls):
        for pocket in pockets:
            ball_x_distance = abs(ball.body.position[0] - pocket[0])
            ball_y_distance = abs(ball.body.position[1] - pocket[1])
            ball_distance = math.sqrt((ball_x_distance ** 2) + (ball_y_distance ** 2))
            if ball_distance <= pocket_diameter / 2:
                # check if the potted ball was the cue ball
                if i == len(balls) - 1:
                    lives -= 1
                    cue_ball_potted = True
                    ball.body.position = (-100, -100)
                    ball.body.velocity = (0.0, 0.0)
                else:
                    game_space.remove(ball.body)
                    balls.remove(ball)
                    potted_balls.append(balls_img[i])
                    balls_img.pop(i)
    # draw pool balls
    for i, ball in enumerate(balls):
        # print(balls_img[0])
        # game_screen.blit(balls_img[i], ball.body.position)
        game_screen.blit(balls_img[i], (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))

    taking_shot = True
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
            taking_shot = False

    # draw pool cue
    if taking_shot == True and run_game == True:
        if cue_ball_potted == True:
            # reposition cue ball
            balls[-1].body.position = (888, SCREEN_HEIGHT / 2)
            cue_ball_potted = False
        mouse_position = pygame.mouse.get_pos()
        pool_cue.rect.center = balls[-1].body.position
        x_distance = balls[-1].body.position[0] - mouse_position[0]
        y_distance = -(balls[-1].body.position[1] - mouse_position[1])
        cue_angle = math.degrees(math.atan2( y_distance,  x_distance))
        pool_cue.update(cue_angle)
        pool_cue.draw(game_screen)

    # power up pool cue
    if powering_up == True and run_game == True:
        shoot_force += 100 * force_direction
        if shoot_force >= max_force or shoot_force <= 0:
            force_direction *= -1
        # draw power bars
        for bar in range(math.ceil(shoot_force / 2000)):
            game_screen.blit(power_bar,
                        (balls[-1].body.position[0] - 30 + (bar * 15),
                         balls[-1].body.position[1] + 30))
    elif powering_up == False and taking_shot == True:
        x_impulse = math.cos(math.radians(cue_angle))
        y_impulse = math.sin(math.radians(cue_angle))
        balls[-1].body.apply_impulse_at_local_point((shoot_force * -x_impulse, shoot_force * y_impulse), (0, 0))
        shoot_force = 0
        force_direction = 1


    # draw bottom panel
    pygame.draw.rect(game_screen, background, (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL))
    DrawText("LIVES: " + str(lives), font, WHITE, SCREEN_WIDTH - 200, SCREEN_HEIGHT + 10)

    # draw potted balls in bottom panel
    for i, ball in enumerate(potted_balls):
        game_screen.blit(ball, (10 + (i * 50), SCREEN_HEIGHT + 10))

    # check for game over
    if lives <= 0:
        DrawText("GAME OVER", large_font, WHITE, SCREEN_WIDTH / 2 - 160, SCREEN_HEIGHT / 2 - 100)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                run_game = False

    # check if all balls are potted
    if len(balls) == 1:
        DrawText("YOU WIN!", large_font, WHITE, SCREEN_WIDTH / 2 - 160, SCREEN_HEIGHT / 2 - 100)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                run_game = False

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot == True:
            powering_up = True
        if event.type == pygame.MOUSEBUTTONUP and taking_shot == True:
            powering_up = False
            #balls[-1].body.apply_impulse_at_local_point((shoot_force * - x_impulse, shoot_force * y_impulse), (0, 0))

        if event.type == pygame.QUIT:
            run_game = False
    #game_space.debug_draw(draw_options)
    pygame.display.update()

pygame.quit()

