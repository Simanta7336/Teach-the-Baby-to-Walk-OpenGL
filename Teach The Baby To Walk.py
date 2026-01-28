from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Game state
g_mode = "GAME" 
cur_lvl = 1
balance_meter = 100.0
score = 0
khel_khatam = False
lvl_finish = False
g_pause = False
last_time = time.time()

# Camera-related variables
camera_mode = "TPP" 
camera_pos = [0, -800, 600] 
camera_angle = 0 

c_d = 900.0   
c_deg = 270.0 
c_h = 600.0  

# TPP zoom levels
tpp_zoom_level = 0  
tpp_distances = [900.0, 350.0] 
tpp_heights = [600.0, 233.0] 
tpp_height_offset = 0.0  

# Apartment
floor_size = 600
wall_h = 150
hallway_w = 120
room_size = 260
door_w = 80
door_h = 100

# Baby properties
baby_pos = [0, 0, 0] 
baby_angle = 0 
baby_state = "CRAWLING" 
baby_speed = 4.0
baby_fall_timer = 0
baby_is_falling = False
baby_is_moving = False  
baby_radius = 10.0  
show_controls = False

lives_remaining = 3

speed_boost_active = False
speed_boost_collectibles_remaining = 0

# Free mode room tracking
room_collectibles = {1: [], 2: [], 3: [], 4: []} 
last_baby_room = 0 

# Balance tilt mechanic (for level 2+)
baby_tilt = 0.0  # 
tilt_speed = 0.3 
last_tilt_time = time.time()

collision_objects = []

# Collectibles
collectibles = []  #(x, y, type, collected)
COLLECTIBLE_TYPES = {
    "BALL": {"points": 10, "balance": 5},
    "TEDDY": {"points": 15, "balance": 10},
    "RATTLE": {"points": 10, "balance": 5},
    "LEGO": {"points": 20, "balance": 10},
    "CAR": {"points": 15, "balance": 5},
    "HAT": {"points": 10, "balance": 5},
    "DOLL": {"points": 15, "balance": 10},
    "MILK_FEEDER": {"points": 20, "balance": 15},
    "SCISSORS": {"points": -25, "balance": -35},
    "KNIFE": {"points": -30, "balance": -40},
    "KEYS": {"points": -15, "balance": -25},
    "WIRE": {"points": -20, "balance": -30},
    "HARMFUL": {"points": -20, "balance": -30}  
}


def update_cam_pos():
    global camera_pos, c_d, c_deg, c_h, tpp_zoom_level, tpp_distances, tpp_heights, tpp_height_offset
    c_d = tpp_distances[tpp_zoom_level]  
    c_h = tpp_heights[tpp_zoom_level] + \
        tpp_height_offset  
    th = math.radians(c_deg)
    x = c_d * math.cos(th)
    y = c_d * math.sin(th)
    z = c_h
    camera_pos = [x, y, z]


def draw_text(x, y, text, font=None):
    if font is None:
        try:
            font = GLUT_BITMAP_HELVETICA_18  
        except:
            font = 7  
    glColor3f(.19, .5, .19)  
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_floor():
    half_hall = hallway_w / 2

    # Room 1 (top-left) - Bedroom
    glColor3f(0.85, 0.75, 0.65)
    glBegin(GL_QUADS)
    glVertex3f(-floor_size, half_hall, 0)
    glVertex3f(0, half_hall, 0)
    glVertex3f(0, floor_size, 0)
    glVertex3f(-floor_size, floor_size, 0)
    glEnd()

    # Room 2 (top-right) - Playroom
    glColor3f(0.9, 0.85, 0.75)
    glBegin(GL_QUADS)
    glVertex3f(0, half_hall, 0)
    glVertex3f(floor_size, half_hall, 0)
    glVertex3f(floor_size, floor_size, 0)
    glVertex3f(0, floor_size, 0)
    glEnd()

    # Room 3 (bottom-left) - Living room
    glColor3f(0.8, 0.7, 0.6)
    glBegin(GL_QUADS)
    glVertex3f(-floor_size, -floor_size, 0)
    glVertex3f(0, -floor_size, 0)
    glVertex3f(0, -half_hall, 0)
    glVertex3f(-floor_size, -half_hall, 0)
    glEnd()

    # Room 4 (bottom-right) - Dining area
    glColor3f(0.75, 0.65, 0.55)
    glBegin(GL_QUADS)
    glVertex3f(0, -floor_size, 0)
    glVertex3f(floor_size, -floor_size, 0)
    glVertex3f(floor_size, -half_hall, 0)
    glVertex3f(0, -half_hall, 0)
    glEnd()

    # Hallway (horizontal) - lighter color
    glColor3f(0.9, 0.9, 0.85)
    glBegin(GL_QUADS)
    glVertex3f(-floor_size, -half_hall, 0)
    glVertex3f(floor_size, -half_hall, 0)
    glVertex3f(floor_size, half_hall, 0)
    glVertex3f(-floor_size, half_hall, 0)
    glEnd()

    # grid lines
    glColor3f(0.6, 0.55, 0.5)
    glBegin(GL_LINES)
    for i in range(-floor_size, floor_size + 1, 50):
        glVertex3f(i, -floor_size, 0.5)
        glVertex3f(i, floor_size, 0.5)
        glVertex3f(-floor_size, i, 0.5)
        glVertex3f(floor_size, i, 0.5)
    glEnd()


def draw_walls():
    
    glColor3f(0.961, 0.941, 0.894)  

    # Back wall
    glBegin(GL_QUADS)
    glVertex3f(-floor_size, floor_size, 0)
    glVertex3f(floor_size, floor_size, 0)
    glVertex3f(floor_size, floor_size, wall_h)
    glVertex3f(-floor_size, floor_size, wall_h)
    glEnd()
    # Subtle gray outline (darker than wall color to reduce pixelation)
    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-floor_size, floor_size, 0)
    glVertex3f(floor_size, floor_size, 0)
    glVertex3f(floor_size, floor_size, wall_h)
    glVertex3f(-floor_size, floor_size, wall_h)
    glEnd()

    # Left wall
    glColor3f(0.961, 0.941, 0.894)
    glBegin(GL_QUADS)
    glVertex3f(-floor_size, -floor_size, 0)
    glVertex3f(-floor_size, floor_size, 0)
    glVertex3f(-floor_size, floor_size, wall_h)
    glVertex3f(-floor_size, -floor_size, wall_h)
    glEnd()
    # Subtle gray outline
    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-floor_size, -floor_size, 0)
    glVertex3f(-floor_size, floor_size, 0)
    glVertex3f(-floor_size, floor_size, wall_h)
    glVertex3f(-floor_size, -floor_size, wall_h)
    glEnd()

    # Right wall
    glColor3f(0.961, 0.941, 0.894)
    glBegin(GL_QUADS)
    glVertex3f(floor_size, -floor_size, 0)
    glVertex3f(floor_size, floor_size, 0)
    glVertex3f(floor_size, floor_size, wall_h)
    glVertex3f(floor_size, -floor_size, wall_h)
    glEnd()
    # Subtle gray outline
    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINE_LOOP)
    glVertex3f(floor_size, -floor_size, 0)
    glVertex3f(floor_size, floor_size, 0)
    glVertex3f(floor_size, floor_size, wall_h)
    glVertex3f(floor_size, -floor_size, wall_h)
    glEnd()

    # Front wall
    glColor3f(0.961, 0.941, 0.894)
    glBegin(GL_QUADS)
    glVertex3f(-floor_size, -floor_size, 0)
    glVertex3f(floor_size, -floor_size, 0)
    glVertex3f(floor_size, -floor_size, wall_h)
    glVertex3f(-floor_size, -floor_size, wall_h)
    glEnd()
    # Subtle gray outline
    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-floor_size, -floor_size, 0)
    glVertex3f(floor_size, -floor_size, 0)
    glVertex3f(floor_size, -floor_size, wall_h)
    glVertex3f(-floor_size, -floor_size, wall_h)
    glEnd()

    # Fill corner gaps with vertical strips
    glColor3f(0.961, 0.941, 0.894)
    # Back-left corner
    glBegin(GL_QUADS)
    glVertex3f(-floor_size - 1, floor_size, 0)
    glVertex3f(-floor_size + 1, floor_size, 0)
    glVertex3f(-floor_size + 1, floor_size, wall_h)
    glVertex3f(-floor_size - 1, floor_size, wall_h)
    glEnd()
    # Back-right corner
    glBegin(GL_QUADS)
    glVertex3f(floor_size - 1, floor_size, 0)
    glVertex3f(floor_size + 1, floor_size, 0)
    glVertex3f(floor_size + 1, floor_size, wall_h)
    glVertex3f(floor_size - 1, floor_size, wall_h)
    glEnd()
    # Front-left corner
    glBegin(GL_QUADS)
    glVertex3f(-floor_size - 1, -floor_size, 0)
    glVertex3f(-floor_size + 1, -floor_size, 0)
    glVertex3f(-floor_size + 1, -floor_size, wall_h)
    glVertex3f(-floor_size - 1, -floor_size, wall_h)
    glEnd()
    # Front-right corner
    glBegin(GL_QUADS)
    glVertex3f(floor_size - 1, -floor_size, 0)
    glVertex3f(floor_size + 1, -floor_size, 0)
    glVertex3f(floor_size + 1, -floor_size, wall_h)
    glVertex3f(floor_size - 1, -floor_size, wall_h)
    glEnd()



def draw_interior_walls():
    """Draw interior walls separating rooms with 3D thickness"""
    half_hall = hallway_w / 2
    half_door = door_w / 2
    wall_thickness = 3.0  

    glColor3f(0.961, 0.941, 0.894)  

    def draw_3d_wall_segment(x1, y1, x2, y2, height, is_vertical=True):
        """Draw a 3D wall with thickness"""
        glColor3f(0.961, 0.941, 0.894)

        if is_vertical:
            # Front face
            glBegin(GL_QUADS)
            glVertex3f(x1 + wall_thickness/2, y1, 0)
            glVertex3f(x1 + wall_thickness/2, y2, 0)
            glVertex3f(x1 + wall_thickness/2, y2, height)
            glVertex3f(x1 + wall_thickness/2, y1, height)
            glEnd()

            # Back face
            glBegin(GL_QUADS)
            glVertex3f(x1 - wall_thickness/2, y1, 0)
            glVertex3f(x1 - wall_thickness/2, y2, 0)
            glVertex3f(x1 - wall_thickness/2, y2, height)
            glVertex3f(x1 - wall_thickness/2, y1, height)
            glEnd()

            # Top face
            glBegin(GL_QUADS)
            glVertex3f(x1 - wall_thickness/2, y1, height)
            glVertex3f(x1 + wall_thickness/2, y1, height)
            glVertex3f(x1 + wall_thickness/2, y2, height)
            glVertex3f(x1 - wall_thickness/2, y2, height)
            glEnd()

            # Side faces
            glBegin(GL_QUADS)
            glVertex3f(x1 - wall_thickness/2, y1, 0)
            glVertex3f(x1 + wall_thickness/2, y1, 0)
            glVertex3f(x1 + wall_thickness/2, y1, height)
            glVertex3f(x1 - wall_thickness/2, y1, height)
            glEnd()

            glBegin(GL_QUADS)
            glVertex3f(x1 - wall_thickness/2, y2, 0)
            glVertex3f(x1 + wall_thickness/2, y2, 0)
            glVertex3f(x1 + wall_thickness/2, y2, height)
            glVertex3f(x1 - wall_thickness/2, y2, height)
            glEnd()

            glColor3f(0.7, 0.65, 0.6)
            # Front face edges
            glBegin(GL_LINE_LOOP)
            glVertex3f(x1 + wall_thickness/2, y1, 0)
            glVertex3f(x1 + wall_thickness/2, y2, 0)
            glVertex3f(x1 + wall_thickness/2, y2, height)
            glVertex3f(x1 + wall_thickness/2, y1, height)
            glEnd()
            # Back face edges
            glBegin(GL_LINE_LOOP)
            glVertex3f(x1 - wall_thickness/2, y1, 0)
            glVertex3f(x1 - wall_thickness/2, y2, 0)
            glVertex3f(x1 - wall_thickness/2, y2, height)
            glVertex3f(x1 - wall_thickness/2, y1, height)
            glEnd()
            # Connecting lines between front and back
            glBegin(GL_LINES)
            glVertex3f(x1 - wall_thickness/2, y1, 0)
            glVertex3f(x1 + wall_thickness/2, y1, 0)
            glVertex3f(x1 - wall_thickness/2, y2, 0)
            glVertex3f(x1 + wall_thickness/2, y2, 0)
            glVertex3f(x1 - wall_thickness/2, y1, height)
            glVertex3f(x1 + wall_thickness/2, y1, height)
            glVertex3f(x1 - wall_thickness/2, y2, height)
            glVertex3f(x1 + wall_thickness/2, y2, height)
            glEnd()
        else:
            # Horizontal wall - Front face (facing +y)
            glBegin(GL_QUADS)
            glVertex3f(x1, y1 + wall_thickness/2, 0)
            glVertex3f(x2, y1 + wall_thickness/2, 0)
            glVertex3f(x2, y1 + wall_thickness/2, height)
            glVertex3f(x1, y1 + wall_thickness/2, height)
            glEnd()

            # Back face (facing -y)
            glBegin(GL_QUADS)
            glVertex3f(x1, y1 - wall_thickness/2, 0)
            glVertex3f(x2, y1 - wall_thickness/2, 0)
            glVertex3f(x2, y1 - wall_thickness/2, height)
            glVertex3f(x1, y1 - wall_thickness/2, height)
            glEnd()

            # Top face
            glBegin(GL_QUADS)
            glVertex3f(x1, y1 - wall_thickness/2, height)
            glVertex3f(x2, y1 - wall_thickness/2, height)
            glVertex3f(x2, y1 + wall_thickness/2, height)
            glVertex3f(x1, y1 + wall_thickness/2, height)
            glEnd()

            # Side faces
            glBegin(GL_QUADS)
            glVertex3f(x1, y1 - wall_thickness/2, 0)
            glVertex3f(x1, y1 + wall_thickness/2, 0)
            glVertex3f(x1, y1 + wall_thickness/2, height)
            glVertex3f(x1, y1 - wall_thickness/2, height)
            glEnd()

            glBegin(GL_QUADS)
            glVertex3f(x2, y1 - wall_thickness/2, 0)
            glVertex3f(x2, y1 + wall_thickness/2, 0)
            glVertex3f(x2, y1 + wall_thickness/2, height)
            glVertex3f(x2, y1 - wall_thickness/2, height)
            glEnd()

            glColor3f(0.7, 0.65, 0.6)
            # Front face edges
            glBegin(GL_LINE_LOOP)
            glVertex3f(x1, y1 + wall_thickness/2, 0)
            glVertex3f(x2, y1 + wall_thickness/2, 0)
            glVertex3f(x2, y1 + wall_thickness/2, height)
            glVertex3f(x1, y1 + wall_thickness/2, height)
            glEnd()
            # Back face edges
            glBegin(GL_LINE_LOOP)
            glVertex3f(x1, y1 - wall_thickness/2, 0)
            glVertex3f(x2, y1 - wall_thickness/2, 0)
            glVertex3f(x2, y1 - wall_thickness/2, height)
            glVertex3f(x1, y1 - wall_thickness/2, height)
            glEnd()
            # Connecting lines between front and back
            glBegin(GL_LINES)
            glVertex3f(x1, y1 - wall_thickness/2, 0)
            glVertex3f(x1, y1 + wall_thickness/2, 0)
            glVertex3f(x2, y1 - wall_thickness/2, 0)
            glVertex3f(x2, y1 + wall_thickness/2, 0)
            glVertex3f(x1, y1 - wall_thickness/2, height)
            glVertex3f(x1, y1 + wall_thickness/2, height)
            glVertex3f(x2, y1 - wall_thickness/2, height)
            glVertex3f(x2, y1 + wall_thickness/2, height)
            glEnd()

    top_center_y = (half_hall + floor_size) / 2
    # Top segment
    draw_3d_wall_segment(0, top_center_y + half_door, 0,
                         floor_size, wall_h, True)
    # Bottom segment
    draw_3d_wall_segment(0, half_hall, 0, top_center_y -
                         half_door, wall_h, True)
    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINES)
    glVertex3f(0, top_center_y - half_door, wall_h)
    glVertex3f(0, top_center_y + half_door, wall_h)
    glEnd()

    bottom_center_y = (-floor_size + (-half_hall)) / 2
    # Top segment
    draw_3d_wall_segment(0, bottom_center_y + half_door,
                         0, -half_hall, wall_h, True)
    # Bottom segment
    draw_3d_wall_segment(0, -floor_size, 0, bottom_center_y - half_door, wall_h, True)
    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINES)
    glVertex3f(0, bottom_center_y - half_door, wall_h)
    glVertex3f(0, bottom_center_y + half_door, wall_h)
    glEnd()

    room1_center_x = -floor_size / 2
    room2_center_x = floor_size / 2
    # Left segment (before Room 1 entry)
    draw_3d_wall_segment(-floor_size, half_hall, room1_center_x -
                         half_door, half_hall, wall_h, False)
    # Middle segment (between Room 1 and Room 2 entries)
    draw_3d_wall_segment(room1_center_x + half_door, half_hall,
                         room2_center_x - half_door, half_hall, wall_h, False)
    # Right segment (after Room 2 entry)
    draw_3d_wall_segment(room2_center_x + half_door, half_hall,
                         floor_size, half_hall, wall_h, False)
    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINES)
    glVertex3f(room1_center_x - half_door, half_hall, wall_h)
    glVertex3f(room1_center_x + half_door, half_hall, wall_h)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(room2_center_x - half_door, half_hall, wall_h)
    glVertex3f(room2_center_x + half_door, half_hall, wall_h)
    glEnd()

    room3_center_x = -floor_size / 2
    room4_center_x = floor_size / 2
    # Left segment (before Room 3 entry)
    draw_3d_wall_segment(-floor_size, -half_hall, room3_center_x -
                         half_door, -half_hall, wall_h, False)
    # Middle segment (between Room 3 and Room 4 entries)
    draw_3d_wall_segment(room3_center_x + half_door, -half_hall,
                         room4_center_x - half_door, -half_hall, wall_h, False)
    # Right segment (after Room 4 entry)
    draw_3d_wall_segment(room4_center_x + half_door, -
                         half_hall, floor_size, -half_hall, wall_h, False)

    glColor3f(0.7, 0.65, 0.6)
    glBegin(GL_LINES)
    glVertex3f(room3_center_x - half_door, -half_hall, wall_h)
    glVertex3f(room3_center_x + half_door, -half_hall, wall_h)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(room4_center_x - half_door, -half_hall, wall_h)
    glVertex3f(room4_center_x + half_door, -half_hall, wall_h)
    glEnd()


def draw_table(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Table legs
    leg_height = 40
    leg_radius = 3
    table_width = 80
    table_depth = 60

    glColor3f(0.4, 0.3, 0.2)  # Brown wood

    # Leg positions
    leg_positions = [
        (-table_width/2 + 10, -table_depth/2 + 10),
        (table_width/2 - 10, -table_depth/2 + 10),
        (-table_width/2 + 10, table_depth/2 - 10),
        (table_width/2 - 10, table_depth/2 - 10)
    ]

    for lx, ly in leg_positions:
        glPushMatrix()
        glTranslatef(lx, ly, 0)
        gluCylinder(gluNewQuadric(), leg_radius, leg_radius, leg_height, 8, 1)
        glPopMatrix()

    # Table top (cube)
    glColor3f(0.5, 0.35, 0.25)
    glTranslatef(0, 0, leg_height)
    glScalef(table_width, table_depth, 5)
    glutSolidCube(1)

    glPopMatrix()


def draw_chair(x, y, rotation=0):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(rotation, 0, 0, 1)

    seat_height = 25

    # Chair legs
    glColor3f(0.3, 0.2, 0.1)
    leg_positions = [(-12, -12), (12, -12), (-12, 12), (12, 12)]

    for lx, ly in leg_positions:
        glPushMatrix()
        glTranslatef(lx, ly, seat_height/2)
        glutSolidCube(4)
        glTranslatef(0, 0, seat_height/2)
        glutSolidCube(4)
        glPopMatrix()

    # Seat (cube)
    glColor3f(0.6, 0.4, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, seat_height)
    glScalef(30, 30, 3)
    glutSolidCube(1)
    glPopMatrix()

    # Backrest
    glPushMatrix()
    glTranslatef(0, -12, seat_height + 15)
    glScalef(30, 3, 30)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_tv(x, y):
    """Draw a TV using cube and cylinder stand"""
    glPushMatrix()
    glTranslatef(x, y, 0)


    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, 3, 0) 
    gluCylinder(gluNewQuadric(), 8, 8, 30, 10, 1)
    glPopMatrix()

    # TV screen
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, -2.5, 30)  
    glScalef(60, 5, 40)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_toy_ball(x, y, z, radius, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    gluSphere(gluNewQuadric(), radius, 12, 12)
    glPopMatrix()


def draw_teddy_bear(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Body
    glColor3f(0.6, 0.4, 0.2)  # Brown
    glPushMatrix()
    glTranslatef(0, 0, 10)
    gluSphere(gluNewQuadric(), 8, 10, 10)
    glPopMatrix()

    # Head
    glPushMatrix()
    glTranslatef(0, 0, 20)
    gluSphere(gluNewQuadric(), 5, 10, 10)
    glPopMatrix()

    # Ears
    glPushMatrix()
    glTranslatef(-4, 0, 23)
    gluSphere(gluNewQuadric(), 2, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(4, 0, 23)
    gluSphere(gluNewQuadric(), 2, 8, 8)
    glPopMatrix()

    glPopMatrix()


def draw_rattle(x, y):
    glPushMatrix()
    glTranslatef(x, y, 8)

    # Handle
    glColor3f(0.8, 0.6, 0.2)  
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2, 2, 15, 8, 1)

    # Rattle head 
    glColor3f(1.0, 0.3, 0.3)  
    glTranslatef(0, 0, 15)
    gluSphere(gluNewQuadric(), 6, 10, 10)

    glPopMatrix()


def draw_lego(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)]

    for i, color in enumerate(colors):
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(0, 0, i * 10 + 5)
        glutSolidCube(10)
        glPopMatrix()

    glPopMatrix()


def draw_harmful_object(x, y):
    glPushMatrix()
    glTranslatef(x, y, 10)

    # Red spiky sphere
    glColor3f(1.0, 0.2, 0.2)
    gluSphere(gluNewQuadric(), 8, 8, 8)

    # Spikes
    glColor3f(0.8, 0.0, 0.0)
    for angle in range(0, 360, 45):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(8, 0, 0)
        gluCylinder(gluNewQuadric(), 2, 0, 8, 6, 1)
        glPopMatrix()

    glPopMatrix()


def draw_toy_car(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Car body 
    glColor3f(1.0, 0.2, 0.2) 
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glScalef(20, 12, 8)
    glutSolidCube(1)
    glPopMatrix()

    # Car cabin 
    glColor3f(0.8, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 14)
    glScalef(12, 10, 8)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels 
    glColor3f(0.1, 0.1, 0.1)  
    wheel_positions = [(-7, -6), (7, -6), (-7, 6), (7, 6)]
    for wx, wy in wheel_positions:
        glPushMatrix()
        glTranslatef(wx, wy, 4)
        gluSphere(gluNewQuadric(), 3, 8, 8)
        glPopMatrix()

    glPopMatrix()


def draw_hat(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Hat brim 
    glColor3f(0.9, 0.7, 0.2)  
    glPushMatrix()
    glTranslatef(0, 0, 5)
    gluCylinder(gluNewQuadric(), 10, 10, 2, 12, 1)
    glPopMatrix()

    # Hat top 
    glColor3f(1.0, 0.8, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 7)
    gluCylinder(gluNewQuadric(), 7, 7, 12, 12, 1)
    glPopMatrix()

    # Hat tip 
    glColor3f(0.8, 0.6, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 19)
    gluSphere(gluNewQuadric(), 3, 10, 10)
    glPopMatrix()

    glPopMatrix()


def draw_doll(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Body
    glColor3f(1.0, 0.6, 0.8)  
    glPushMatrix()
    glTranslatef(0, 0, 5)
    gluCylinder(gluNewQuadric(), 5, 5, 15, 10, 1)
    glPopMatrix()

    # Head
    glColor3f(1.0, 0.85, 0.75)  
    glPushMatrix()
    glTranslatef(0, 0, 25)
    gluSphere(gluNewQuadric(), 6, 12, 12)
    glPopMatrix()

    # Hair 
    glColor3f(0.3, 0.2, 0.1) 
    glPushMatrix()
    glTranslatef(0, 0, 30)
    gluSphere(gluNewQuadric(), 4, 10, 10)
    glPopMatrix()

    # Arms
    glColor3f(1.0, 0.6, 0.8)
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(5 * side, 0, 15)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 2, 2, 5, 8, 1)
        glPopMatrix()

    glPopMatrix()


def draw_milk_feeder(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Bottle body
    glColor3f(0.9, 0.9, 1.0)  
    glPushMatrix()
    glTranslatef(0, 0, 5)
    gluCylinder(gluNewQuadric(), 5, 5, 20, 12, 1)
    glPopMatrix()

    # Bottle bottom
    glColor3f(0.85, 0.85, 0.95)
    glPushMatrix()
    glTranslatef(0, 0, 5)
    gluSphere(gluNewQuadric(), 5, 10, 10)
    glPopMatrix()


    glColor3f(1.0, 0.9, 0.7) 
    glPushMatrix()
    glTranslatef(0, 0, 25)
    gluCylinder(gluNewQuadric(), 3, 1, 6, 10, 1)
    glPopMatrix()

    # Milk
    glColor3f(1.0, 1.0, 0.9) 
    glPushMatrix()
    glTranslatef(0, 0, 6)
    gluCylinder(gluNewQuadric(), 4, 4, 12, 12, 1)
    glPopMatrix()

    glPopMatrix()


def draw_scissors(x, y):
    glPushMatrix()
    glTranslatef(x, y, 5)

    # Left handle and blade
    glPushMatrix()
    glRotatef(-20, 0, 0, 1)  

    glColor3f(0.8, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0, -5, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 1, 10, 1)
    glPopMatrix()
    # Blade
    glColor3f(0.9, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-0.5, -5, 0)
    glVertex3f(-0.5, 8, 0)
    glVertex3f(0.5, 8, 0)
    glVertex3f(0.5, -5, 0)
    glEnd()
    glPopMatrix()

    # Right handle and blade
    glPushMatrix()
    glRotatef(20, 0, 0, 1)  # Rotate right blade
    # Handle (circle)
    glColor3f(0.8, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0, -5, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 1, 10, 1)
    glPopMatrix()
    # Blade
    glColor3f(0.9, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-0.5, -5, 0)
    glVertex3f(-0.5, 8, 0)
    glVertex3f(0.5, 8, 0)
    glVertex3f(0.5, -5, 0)
    glEnd()
    glPopMatrix()

    glPopMatrix()


def draw_knife(x, y):
    
    glPushMatrix()
    glTranslatef(x, y, 3)

    # Handle (cylinder) - dark reddish brown
    glColor3f(0.5, 0.2, 0.2)  # Dark reddish brown
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 2, 2, 8, 10, 1)
    glPopMatrix()

    # Blade (thin quad) - reddish metal
    glColor3f(0.9, 0.5, 0.5)  # Light reddish metal
    glBegin(GL_QUADS)
    glVertex3f(8, -1, 0)
    glVertex3f(8, 1, 0)
    glVertex3f(20, 0.5, 0)
    glVertex3f(20, -0.5, 0)
    glEnd()

    # Blade edge (triangle tip)
    glBegin(GL_TRIANGLES)
    glVertex3f(20, 0.5, 0)
    glVertex3f(20, -0.5, 0)
    glVertex3f(25, 0, 0)
    glEnd()

    glPopMatrix()


def draw_keys(x, y):
    
    glPushMatrix()
    glTranslatef(x, y, 5)

    # Key ring (cylinder) - reddish gold
    glColor3f(0.8, 0.4, 0.2)  # Reddish gold
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 4, 1, 12, 1)
    glPopMatrix()

    # Keys (3 small rectangles) - reddish silver
    glColor3f(0.9, 0.6, 0.6)  # Light reddish silver
    for i, angle in enumerate([0, 120, 240]):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(4, 0, 0)
        # Key shaft
        glBegin(GL_QUADS)
        glVertex3f(0, -1, -1)
        glVertex3f(8, -1, -1)
        glVertex3f(8, 1, -1)
        glVertex3f(0, 1, -1)
        glEnd()
        # Key teeth (small cubes)
        for j in range(3):
            glPushMatrix()
            glTranslatef(2 + j * 2, 0, -1)
            glutSolidCube(1)
            glPopMatrix()
        glPopMatrix()

    glPopMatrix()





def initialize_collectibles():
    global collectibles
    collectibles = []

    def is_position_valid(x, y, min_distance=40):

        for obj in collision_objects:
            ox, oy, ow, oh = obj[0], obj[1], obj[2], obj[3]
            if (abs(x - ox) < ow/2 + min_distance and
                    abs(y - oy) < oh/2 + min_distance):
                return False

        # Check collision with other collectibles
        for cx, cy, _, _ in collectibles:
            if math.sqrt((x - cx)**2 + (y - cy)**2) < min_distance:
                return False

        return True

    def get_valid_position_in_room(room_num, attempts=50):# Toy respawn korbe jekhane oita jate khali jayga hoy
        """Get a valid position in specified room"""
        for _ in range(attempts):
            if room_num == 1:  # Drawing Room (top-left)
                x = random.randint(-520, -150)
                y = random.randint(150, 520)
            elif room_num == 2:  # Bedroom (top-right)
                x = random.randint(150, 520)
                y = random.randint(150, 520)
            elif room_num == 3:  # Guest Room (bottom-left)
                x = random.randint(-520, -150)
                y = random.randint(-520, -150)
            else:  # Dining Room (bottom-right)
                x = random.randint(150, 520)
                y = random.randint(-520, -150)

            if is_position_valid(x, y):
                return x, y


        centers = {1: (-350, 400), 2: (350, 400),
                   3: (-350, -400), 4: (350, -400)}
        return centers[room_num]

    if cur_lvl == 1:
        toy_items = ["BALL", "TEDDY", "RATTLE", "LEGO",
                     "CAR", "HAT", "DOLL"]
        harmful_items = ["SCISSORS", "KNIFE", "KEYS"]

        # Add 10 toys
        for _ in range(10):
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(toy_items)
            collectibles.append((x, y, item_type, False))

        # Add 5 harmful items
        for _ in range(5):
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(harmful_items)
            collectibles.append((x, y, item_type, False))

    elif cur_lvl == 2:
    
        toy_items = ["BALL", "TEDDY", "RATTLE", "LEGO",
                     "CAR", "HAT", "DOLL"]
        harmful_items = ["SCISSORS", "KNIFE", "KEYS"]

        # Add 10 toys
        for _ in range(10):
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(toy_items)
            collectibles.append((x, y, item_type, False))

        # Add 10 harmful items
        for _ in range(10):
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(harmful_items)
            collectibles.append((x, y, item_type, False))

    elif cur_lvl == 3:
        # Level 3: 20 collectibles (13 toys + 7 harmful)
        toy_items = ["BALL", "TEDDY", "RATTLE", "LEGO",
                     "CAR", "HAT", "DOLL", "MILK_FEEDER"]
        toy_items_no_feeder = ["BALL", "TEDDY", "RATTLE", "LEGO",
                                "CAR", "HAT", "DOLL"]
        harmful_items = ["SCISSORS", "KNIFE", "KEYS"]

        # Add 13 toys, ensuring 3-6 MILK_FEEDER items
        num_toys = 13
        num_feeders = random.randint(3, min(6, num_toys))
        toy_list = ["MILK_FEEDER"] * num_feeders + [random.choice(toy_items_no_feeder) for _ in range(num_toys - num_feeders)]
        random.shuffle(toy_list)
        for item_type in toy_list:
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            collectibles.append((x, y, item_type, False))

        # Add 7 harmful items
        for _ in range(7):
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(harmful_items)
            collectibles.append((x, y, item_type, False))

    elif cur_lvl == 4:
        # Level 4: 20 collectibles (15 toys + 5 harmful)
        toy_items = ["BALL", "TEDDY", "RATTLE", "LEGO",
                     "CAR", "HAT", "DOLL", "MILK_FEEDER"]
        toy_items_no_feeder = ["BALL", "TEDDY", "RATTLE", "LEGO",
                                "CAR", "HAT", "DOLL"]
        harmful_items = ["SCISSORS", "KNIFE", "KEYS"]

        # Add 15 toys, ensuring 3-6 MILK_FEEDER items
        num_toys = 15
        num_feeders = random.randint(3, min(6, num_toys))
        toy_list = ["MILK_FEEDER"] * num_feeders + [random.choice(toy_items_no_feeder) for _ in range(num_toys - num_feeders)]
        random.shuffle(toy_list)
        for item_type in toy_list:
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            collectibles.append((x, y, item_type, False))

        # Add 5 harmful items
        for _ in range(5):
            room_num = random.randint(1, 4)
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(harmful_items)
            collectibles.append((x, y, item_type, False))


def get_baby_room():
    
    x, y = baby_pos[0], baby_pos[1]

    # Room 1: Drawing Room (top-left)
    if -floor_size/2 < x < -hallway_w/2 and hallway_w/2 < y < floor_size/2:
        return 1
    # Room 2: Bedroom (top-right)
    elif hallway_w/2 < x < floor_size/2 and hallway_w/2 < y < floor_size/2:
        return 2
    # Room 3: Guest Room (bottom-left)
    elif -floor_size/2 < x < -hallway_w/2 and -floor_size/2 < y < -hallway_w/2:
        return 3
    # Room 4: Dining Room (bottom-right)
    elif hallway_w/2 < x < floor_size/2 and -floor_size/2 < y < -hallway_w/2:
        return 4
    else:
        return 0  # In hallway


def initialize_free_mode_collectibles():
    global collectibles, room_collectibles
    collectibles = []
    room_collectibles = {1: [], 2: [], 3: [], 4: []}

    def is_position_valid(x, y, min_distance=40):
        # Check collision with furniture
        for obj in collision_objects:
            ox, oy, ow, oh = obj[0], obj[1], obj[2], obj[3]
            if (abs(x - ox) < ow/2 + min_distance and
                    abs(y - oy) < oh/2 + min_distance):
                return False

        # Check collision with other collectibles
        for cx, cy, _, _ in collectibles:
            if math.sqrt((x - cx)**2 + (y - cy)**2) < min_distance:
                return False

        return True

    def get_valid_position_in_room(room_num, attempts=50):

        for _ in range(attempts):
            if room_num == 1:  # Drawing Room (top-left)
                x = random.randint(-520, -150)
                y = random.randint(150, 520)
            elif room_num == 2:  # Bedroom (top-right)
                x = random.randint(150, 520)
                y = random.randint(150, 520)
            elif room_num == 3:  # Guest Room (bottom-left)
                x = random.randint(-520, -150)
                y = random.randint(-520, -150)
            else:  # Dining Room (bottom-right)
                x = random.randint(150, 520)
                y = random.randint(-520, -150)

            if is_position_valid(x, y):
                return x, y

        # Fallback to center of room if no valid position found
        centers = {1: (-350, 400), 2: (350, 400),
                   3: (-350, -400), 4: (350, -400)}
        return centers[room_num]

    toy_items = ["BALL", "TEDDY", "RATTLE", "LEGO",
                 "CAR", "HAT", "DOLL"]  # No milk feeder
    harmful_items = ["SCISSORS", "KNIFE", "KEYS"]

    # Distribute collectibles across all 4 rooms
    for room_num in range(1, 5):
        room_collectibles[room_num] = []

        # Add 15 toys per room
        for _ in range(15):
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(toy_items)
            collectible = (x, y, item_type, False)
            collectibles.append(collectible)
            room_collectibles[room_num].append(
                len(collectibles) - 1)  # Store index

        # Add 5 harmful items per room
        for _ in range(5):
            x, y = get_valid_position_in_room(room_num)
            item_type = random.choice(harmful_items)
            collectible = (x, y, item_type, False)
            collectibles.append(collectible)
            room_collectibles[room_num].append(
                len(collectibles) - 1)  # Store index


def respawn_room_collectibles(room_num):
    
    global collectibles

    def is_position_valid(x, y, min_distance=40):

        for obj in collision_objects:
            ox, oy, ow, oh = obj[0], obj[1], obj[2], obj[3]
            if (abs(x - ox) < ow/2 + min_distance and
                    abs(y - oy) < oh/2 + min_distance):
                return False
        return True

    def get_valid_position_in_room(room_num, attempts=50):
        for _ in range(attempts):
            if room_num == 1:
                x = random.randint(-520, -150)
                y = random.randint(150, 520)
            elif room_num == 2:
                x = random.randint(150, 520)
                y = random.randint(150, 520)
            elif room_num == 3:
                x = random.randint(-520, -150)
                y = random.randint(-520, -150)
            else:
                x = random.randint(150, 520)
                y = random.randint(-520, -150)

            if is_position_valid(x, y):
                return x, y

        centers = {1: (-350, 400), 2: (350, 400),
                   3: (-350, -400), 4: (350, -400)}
        return centers[room_num]

    # Respawn all collected items in this room
    for idx in room_collectibles[room_num]:
        x, y, item_type, collected = collectibles[idx]
        if collected:
            # Get new position and respawn
            new_x, new_y = get_valid_position_in_room(room_num)
            collectibles[idx] = (new_x, new_y, item_type, False)


def draw_bed(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Bed frame (wooden)
    glColor3f(0.4, 0.25, 0.15)
    glPushMatrix()
    glTranslatef(0, 0, 12)
    glScalef(90, 120, 24)
    glutSolidCube(1)
    glPopMatrix()

    # Mattress
    glColor3f(0.9, 0.9, 0.95)
    glPushMatrix()
    glTranslatef(0, 0, 28)
    glScalef(85, 115, 8)
    glutSolidCube(1)
    glPopMatrix()

    # Pillow
    glColor3f(0.95, 0.95, 1.0)
    glPushMatrix()
    glTranslatef(0, 40, 34)
    glScalef(60, 30, 10)
    glutSolidCube(1)
    glPopMatrix()

    # Headboard
    glColor3f(0.35, 0.22, 0.12)
    glPushMatrix()
    glTranslatef(0, 55, 35)
    glScalef(90, 8, 45)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_desk(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Desk legs
    glColor3f(0.3, 0.2, 0.1)
    leg_positions = [(-35, -25), (35, -25), (-35, 25), (35, 25)]
    for lx, ly in leg_positions:
        glPushMatrix()
        glTranslatef(lx, ly, 25)
        glScalef(5, 5, 50)
        glutSolidCube(1)
        glPopMatrix()

    # Desktop
    glColor3f(0.45, 0.3, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 50)
    glScalef(90, 60, 4)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_lamp(x, y, z=0):
    glPushMatrix()
    glTranslatef(x, y, z)

    # Base (small cylinder)
    glColor3f(0.3, 0.3, 0.3)
    gluCylinder(gluNewQuadric(), 6, 6, 3, 10, 1)

    # Pole
    glPushMatrix()
    glTranslatef(0, 0, 3)
    gluCylinder(gluNewQuadric(), 1.5, 1.5, 35, 8, 1)
    glPopMatrix()

    # Lampshade (inverted cone)
    glPushMatrix()
    glTranslatef(0, 0, 38)
    glRotatef(180, 1, 0, 0)
    glColor3f(0.9, 0.85, 0.7)
    gluCylinder(gluNewQuadric(), 8, 3, 12, 12, 1)
    glPopMatrix()

    # Bulb
    glColor3f(1.0, 1.0, 0.8)
    glPushMatrix()
    glTranslatef(0, 0, 32)
    gluSphere(gluNewQuadric(), 3, 10, 10)
    glPopMatrix()

    glPopMatrix()


def draw_sofa(x, y, rotation=0):
    """Draw a simple sofa using cubes"""
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(rotation, 0, 0, 1)

    glColor3f(0.3, 0.4, 0.6)
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glScalef(100, 50, 30)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -20, 35)
    glScalef(100, 10, 40)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-45, 0, 25)
    glScalef(10, 50, 20)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(45, 0, 25)
    glScalef(10, 50, 20)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_showcase(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(180, 0, 0, 1)  # Always faces forward into room

    # Base/frame
    glColor3f(0.3, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 35)
    glScalef(80, 25, 70)
    glutSolidCube(1)
    glPopMatrix()

    # Glass shelves (lighter color)
    glColor3f(0.7, 0.8, 0.85)
    for z in [15, 35, 55]:
        glPushMatrix()
        glTranslatef(0, 0, z)
        glScalef(75, 20, 2)
        glutSolidCube(1)
        glPopMatrix()

    glPopMatrix()


def draw_wardrobe(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(270, 0, 0, 1)  # Always faces into room

    # Main body
    glColor3f(0.35, 0.25, 0.15)
    glPushMatrix()
    glTranslatef(0, 0, 50)
    glScalef(90, 40, 100)
    glutSolidCube(1)
    glPopMatrix()

    # Doors (slightly lighter)
    glColor3f(0.4, 0.3, 0.2)
    glPushMatrix()
    glTranslatef(-22, -21, 50)
    glScalef(40, 2, 95)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(22, -21, 50)
    glScalef(40, 2, 95)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_kitchen_oven(x, y):

    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(225, 0, 0, 1)  # Always faces into room

    # Oven body
    glColor3f(0.8, 0.8, 0.85)
    glPushMatrix()
    glTranslatef(0, 0, 35)
    glScalef(50, 50, 70)
    glutSolidCube(1)
    glPopMatrix()

    # Oven door (darker)
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, -26, 25)
    glScalef(40, 2, 40)
    glutSolidCube(1)
    glPopMatrix()

    # Stovetop
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 71)
    glScalef(48, 48, 2)
    glutSolidCube(1)
    glPopMatrix()

    # Burners (4 small circles)
    glColor3f(0.3, 0.3, 0.3)
    for bx, by in [(-12, -12), (12, -12), (-12, 12), (12, 12)]:
        glPushMatrix()
        glTranslatef(bx, by, 73)
        gluCylinder(gluNewQuadric(), 5, 5, 1, 8, 1)
        glPopMatrix()

    glPopMatrix()


def draw_fridge(x, y):

    glPushMatrix()
    glTranslatef(x, y, 0)

    # Main body
    glColor3f(0.9, 0.9, 0.95)
    glPushMatrix()
    glTranslatef(0, 0, 50)
    glScalef(50, 50, 100)
    glutSolidCube(1)
    glPopMatrix()

    # Upper door
    glColor3f(0.85, 0.85, 0.9)
    glPushMatrix()
    glTranslatef(0, -26, 65)
    glScalef(48, 2, 60)
    glutSolidCube(1)
    glPopMatrix()

    # Lower door
    glPushMatrix()
    glTranslatef(0, -26, 25)
    glScalef(48, 2, 40)
    glutSolidCube(1)
    glPopMatrix()

    # Handles
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(15, -28, 65)
    glScalef(3, 2, 15)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(15, -28, 25)
    glScalef(3, 2, 10)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


def draw_plant(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    # Vase (cube)
    glColor3f(0.6, 0.4, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glScalef(15, 15, 16)
    glutSolidCube(1)
    glPopMatrix()

    # Plant (cone/triangle)
    glColor3f(0.2, 0.6, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 16)
    gluCylinder(gluNewQuadric(), 12, 0, 25, 8, 1)
    glPopMatrix()

    glPopMatrix()


def draw_room_labels():
    glColor3f(0.1, 0.1, 0.1)

    # Room 1 - Drawing Room (top-left, label on back wall)
    draw_text_3d("DRAWING ROOM", -300, 598, 100, wall='back')

    # Room 2 - Bedroom (top-right, label on back wall)
    draw_text_3d("BEDROOM", 200, 598, 100, wall='back')

    # Room 3 - Guest Room (bottom-left, label on front wall)
    draw_text_3d("GUEST ROOM", -200, -598, 100, wall='front')

    # Room 4 - Dining Room (bottom-right, label on front wall)
    draw_text_3d("DINING ROOM", 200, -598, 100, wall='front')


def draw_text_3d(text, x, y, z, wall=None):
    glPushMatrix()
    glTranslatef(x, y, z)

    # Apply rotations for wall mounting
    if wall == 'back':
        glRotatef(90, 1, 0, 0)   # Rotate to be horizontal on wall
        glScalef(1, 1, 1)
    elif wall == 'front':
        # Rotate to be horizontal on wall (facing inward)
        glRotatef(-90, 1, 0, 0)
        glRotatef(180, 0, 0, 1)
        glScalef(1, 1, 1)

    glScalef(0.2, 0.2, 0.2)

    for char in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))

    glPopMatrix()


def check_collision_with_objects(x, y):

    for obj in collision_objects:
        ox, oy, ow, oh = obj[0], obj[1], obj[2], obj[3]
        if (x + baby_radius > ox - ow/2 and x - baby_radius < ox + ow/2 and
                y + baby_radius > oy - oh/2 and y - baby_radius < oy + oh/2):
            return True
    return False


def check_wall_collision(x, y):
    half_hall = hallway_w / 2
    half_door = door_w / 2

    # Outer walls
    if (x - baby_radius < -floor_size or x + baby_radius > floor_size or
            y - baby_radius < -floor_size or y + baby_radius > floor_size):
        return True

    # Vertical wall between Room 1 and Room 2 (at x=0, from y=half_hall to floor_size)
    # with door at center
    top_center_y = (half_hall + floor_size) / 2
    if abs(x) < baby_radius and y > half_hall:
        # Check if in door area
        if top_center_y - half_door < y < top_center_y + half_door:
            pass 
        else:
            return True


    bottom_center_y = (-floor_size + (-half_hall)) / 2
    if abs(x) < baby_radius and y < -half_hall:
        # Check if in door area
        if bottom_center_y - half_door < y < bottom_center_y + half_door:
            pass  # Door is open
        else:
            return True

    # Top hallway boundary with doors to Room 1 and Room 2
    room1_center_x = -floor_size / 2
    room2_center_x = floor_size / 2
    if abs(y - half_hall) < baby_radius:
        # Check if in Room 1 door area or Room 2 door area
        if (room1_center_x - half_door < x < room1_center_x + half_door) or \
           (room2_center_x - half_door < x < room2_center_x + half_door):
            pass  # Door is open
        else:
            return True

    # Bottom hallway boundary with doors to Room 3 and Room 4
    room3_center_x = -floor_size / 2
    room4_center_x = floor_size / 2
    if abs(y - (-half_hall)) < baby_radius:
        # Check if in Room 3 door area or Room 4 door area
        if (room3_center_x - half_door < x < room3_center_x + half_door) or \
           (room4_center_x - half_door < x < room4_center_x + half_door):
            pass  # Door is open
        else:
            return True

    return False


def initialize_collision_objects():
    global collision_objects
    collision_objects = []

    # Room 1 (top-left) - Drawing Room
    collision_objects.append((-550, 550, 100, 50))  # sofa 1 (back wall corner)
    collision_objects.append((-550, 150, 100, 50))  # sofa 2 (left wall corner)
    collision_objects.append((-350, 580, 60, 10))   # tv
    collision_objects.append((-280, 560, 15, 15))   # lamp
    collision_objects.append((-450, 580, 80, 25))   # showcase (back wall)
    collision_objects.append((-350, 350, 80, 60))   # table (middle)
    collision_objects.append((-150, 550, 15, 15))   # plant

    # Room 2 (top-right) - Bedroom
    collision_objects.append((300, 350, 90, 120))   # bed
    collision_objects.append((530, 350, 90, 40))    # wardrobe
    collision_objects.append((200, 250, 80, 60))    # table
    collision_objects.append((200, 350, 15, 15))    # lamp
    collision_objects.append((550, 550, 15, 15))    # plant

    # Room 3 (bottom-left) - Guest Room
    collision_objects.append((-500, -250, 90, 60))  # study table/desk
    collision_objects.append((-300, -350, 90, 120))  # bed
    collision_objects.append((-200, -450, 80, 60))  # table
    collision_objects.append((-450, -150, 15, 15))  # lamp
    collision_objects.append((-550, -550, 15, 15))  # plant

    # Room 4 (bottom-right) - Dining Room
    collision_objects.append((350, -300, 80, 60))   # dining table
    collision_objects.append((300, -300, 30, 30))   # chair 1
    collision_objects.append((400, -300, 30, 30))   # chair 2
    collision_objects.append((350, -250, 30, 30))   # chair 3
    collision_objects.append((350, -350, 30, 30))   # chair 4
    collision_objects.append((500, -500, 50, 50))   # kitchen oven
    collision_objects.append((530, -150, 50, 50))   # fridge
    collision_objects.append((550, -550, 15, 15))   # plant


def draw_furniture():

    draw_sofa(-550, 550, 180)
    # Corner sofa against left wall (facing right into room)
    draw_sofa(-550, 150, 270)
    # TV
    draw_tv(-350, 580)
    # Lamp beside TV
    draw_lamp(-280, 560, 0)
    # Showcase on back wall
    draw_showcase(-450, 580)
    # Small table in middle
    draw_table(-350, 350)
    # Plant in corner
    draw_plant(-150, 550)

    # Room 2 (top-right) - Bedroom
    # Bed in middle
    draw_bed(300, 350)
    # Wardrobe wall side
    draw_wardrobe(530, 350)
    # Small table beside bed
    draw_table(200, 250)
    # Lamp beside bed
    draw_lamp(200, 350, 0)
    # Plant in corner
    draw_plant(550, 550)

    # Room 3 (bottom-left) - Guest Room
    # Study table wall side (desk)
    draw_desk(-500, -250)
    # Bed in middle
    draw_bed(-300, -350)
    # Small table beside bed
    draw_table(-200, -450)
    # Lamp beside study table
    draw_lamp(-450, -150, 0)
    # Plant in corner
    draw_plant(-550, -550)

    # Room 4 (bottom-right) - Dining Room
    # Round table with 4 chairs in middle
    draw_table(350, -300)
    draw_chair(300, -300, -90)    # Left chair facing table
    draw_chair(400, -300, 90)  # Right chair facing table
    draw_chair(350, -250, 180)  # Top chair facing table
    draw_chair(350, -350, 0)   # Bottom chair facing table
    # Kitchen oven in corner
    draw_kitchen_oven(500, -500)
    # Fridge in corner
    draw_fridge(530, -150)
    # Plant in corner
    draw_plant(550, -550)


def draw_collectibles():
    for x, y, item_type, collected in collectibles:
        if not collected:
            if item_type == "BALL":
                color = (1.0, 0.2, 0.2)  # Red ball
                draw_toy_ball(x, y, 10, 10, color)
            elif item_type == "TEDDY":
                draw_teddy_bear(x, y)
            elif item_type == "RATTLE":
                draw_rattle(x, y)
            elif item_type == "LEGO":
                draw_lego(x, y)
            elif item_type == "CAR":
                draw_toy_car(x, y)
            elif item_type == "HAT":
                draw_hat(x, y)
            elif item_type == "DOLL":
                draw_doll(x, y)
            elif item_type == "MILK_FEEDER":
                draw_milk_feeder(x, y)
            elif item_type == "SCISSORS":
                draw_scissors(x, y)
            elif item_type == "KNIFE":
                draw_knife(x, y)
            elif item_type == "KEYS":
                draw_keys(x, y)
            # elif item_type == "WIRE":
            #     # Draw wire from collectible position to nearest wall
            #     draw_wire(x, y, x, y - 50, 30)


def draw_baby():
    """Draw a smaller baby character - crawling in level 1, walking in level 2+"""
    glPushMatrix()
    glTranslatef(baby_pos[0], baby_pos[1], 0)
    glRotatef(-baby_angle, 0, 0, 1)

    # Visual tilt (lean) based on `baby_tilt` (-1..1). Apply only when
    # baby is not currently in falling animation so lean is visible.
    if not baby_is_falling:
        max_tilt_deg = 30.0
        glRotatef(baby_tilt * max_tilt_deg, 0, 1, 0)

    if baby_is_falling:
        glRotatef(90, 1, 0, 0)

    quad = gluNewQuadric()

    # Color definitions
    skin = (1.0, 0.88, 0.78)
    onesie = (0.5, 0.7, 1.0)
    diaper = (1.0, 1.0, 1.0)

    # Level 1: Crawling baby (closer to ground, horizontal orientation)
    if cur_lvl == 1:
        # Lower position - baby is close to ground
        glTranslatef(0, 0, 15)

        # Body (smaller) - oriented horizontally along Y-axis
        glColor3f(*diaper)
        glPushMatrix()
        glTranslatef(0, -2, 0)
        glScalef(1.2, 1.1, 0.9)
        gluSphere(quad, 8.5, 10, 10)
        glPopMatrix()

        # Torso
        glColor3f(*onesie)
        glPushMatrix()
        glTranslatef(0, 6, 0)
        glScalef(1.0, 1.2, 0.95)
        gluSphere(quad, 9.0, 10, 10)
        glPopMatrix()

        # Head - looking forward
        glColor3f(*skin)
        glPushMatrix()
        glTranslatef(0, 14, 2)
        glRotatef(-25, 1, 0, 0)  # Tilt head slightly up to look forward
        gluSphere(quad, 8.5, 12, 12)

        # Eyes
        glColor3f(0.15, 0.1, 0.05)
        glPushMatrix()
        glTranslatef(-2.8, 7.5, 2.0)
        gluSphere(quad, 1.1, 8, 8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(2.8, 7.5, 2.0)
        gluSphere(quad, 1.1, 8, 8)
        glPopMatrix()

        # Nose
        glColor3f(0.98, 0.82, 0.72)
        glPushMatrix()
        glTranslatef(0.0, 8.5, 0.4)
        gluSphere(quad, 0.85, 8, 8)
        glPopMatrix()
        glPopMatrix()  # end head

        # Crawling limbs (arms and legs on ground)
        glColor3f(*skin)
        # Shoulders (joint spheres) to visually attach arms to torso
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(9.5 * side, 6.0, 2.0)
            gluSphere(quad, 1.7, 8, 8)
            glPopMatrix()

        # Front arms - anchored at shoulders, reaching forward
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(9.5 * side, 6.0, 2.0)
            glRotatef(170, 1, 0, 0)  # 180 + (-50) = 130, pointing downward
            gluCylinder(quad, 2.5, 2.1, 12, 8, 1)
            glTranslatef(0, 0, 12)
            gluSphere(quad, 2.2, 8, 8)
            glPopMatrix()

        # Hips (joint spheres) to visually attach legs to body
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(7.0 * side, -2.0, 0.0)
            gluSphere(quad, 1.8, 8, 8)
            glPopMatrix()

        # Back legs - two cylinder segments forming kneeling pose
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(7.0 * side, -2.0, 0.0)

            # Upper leg (thigh) - straight down from body
            glRotatef(180, 1, 0, 0)  # Point directly downward
            gluCylinder(quad, 2.8, 2.5, 10, 8, 1)
            glTranslatef(0, 0, 10)

            # Lower leg (calf) - horizontal to ground (90-degree bend)
            glRotatef(270, 1, 0, 0)  # Bend 90 degrees to horizontal
            gluCylinder(quad, 2.4, 2.0, 8, 8, 1)
            glPopMatrix()

    # Level 2+: Walking baby (upright, smaller with tiny limbs)
    else:
        # Body (smaller)
        glColor3f(*diaper)
        glPushMatrix()
        glTranslatef(0, 0, 10)
        glScalef(1.2, 1.0, 0.9)
        gluSphere(quad, 8.5, 10, 10)
        glPopMatrix()

        # Torso
        glColor3f(*onesie)
        glPushMatrix()
        glTranslatef(0, 0, 18)
        glScalef(1.0, 0.9, 1.1)
        gluSphere(quad, 9.0, 10, 10)
        glPopMatrix()

        # Head
        glColor3f(*skin)
        glPushMatrix()
        glTranslatef(0, 0, 28)
        gluSphere(quad, 8.5, 12, 12)

        # Eyes
        glColor3f(0.15, 0.1, 0.05)
        glPushMatrix()
        glTranslatef(-2.8, 7.5, 2.0)
        gluSphere(quad, 1.1, 8, 8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(2.8, 7.5, 2.0)
        gluSphere(quad, 1.1, 8, 8)
        glPopMatrix()

        # Nose
        glColor3f(0.98, 0.82, 0.72)
        glPushMatrix()
        glTranslatef(0.0, 8.5, 0.4)
        gluSphere(quad, 0.85, 8, 8)
        glPopMatrix()
        glPopMatrix()  # end head

        # Tiny walking limbs
        if baby_state == "STANDING":
            wobble = math.sin(time.time() * 3) * 2
            glRotatef(wobble, 1, 0, 0)

        # Only animate legs when baby is actually moving
        leg_swing = math.sin(time.time() * 5) * \
            12 if (baby_state == "WALKING" and baby_is_moving) else 0

        # Two-cylinder arms (like legs) - both sides visible
        glColor3f(*skin)
        for side, swing in [(-1, -leg_swing * 0.3), (1, leg_swing * 0.3)]:
            glPushMatrix()
            # Position at shoulder
            glTranslatef(9.5 * side, 0.0, 18.0)

            # Upper arm - extends outward and down
            glRotatef(180 + swing, 1, 0, 0)  # Point downward with swing
            gluCylinder(quad, 2.0, 1.8, 8, 8, 1)
            glTranslatef(0, 0, 8)

            # Elbow joint
            gluSphere(quad, 1.9, 8, 8)
            glPopMatrix()

        # Tiny legs
        for side, swing in [(-1, leg_swing), (1, -leg_swing)]:
            glPushMatrix()
            glTranslatef(5.0 * side, 0.0, 10.0)
            glRotatef(180 + swing, 1, 0, 0)  # Flip legs downward
            gluCylinder(quad, 2.8, 2.4, 14, 8, 1)
            glTranslatef(0, 0, 14)
            gluSphere(quad, 2.5, 8, 8)
            glPopMatrix()

    glPopMatrix()


def keyboardListener(key, x, y):
    """Handle keyboard inputs"""
    global camera_mode, tpp_zoom_level
    global baby_pos, baby_angle, baby_state, g_mode, cur_lvl, khel_khatam, lvl_finish, baby_tilt
    global speed_boost_active, balance_meter, lives_remaining, g_pause, baby_is_moving
    global baby_is_falling, baby_fall_timer

    # ESC key to pause/unpause
    if key == b'\x1b':  # ESC 
        g_pause = not g_pause
        if g_pause:
            print("Game Paused! Press ESC to continue.")
        else:
            print("Game Resumed!")
        return

    if g_pause:
        return

    if khel_khatam:
        if key == b'r':
            reset_game()
        return

    # Handle Enter key for free mode (when level 4 is complete)
    if key == b'\r':  # Enter key
        if cur_lvl == 4 and lvl_finish:
            g_mode = "FREE"
            baby_state = "WALKING"
            lvl_finish = False  # Clear completion flag to remove celebration message
            print("Entering Free Mode! Explore freely with no consequences.")
            initialize_free_mode_collectibles()
            return

    # Optional: keep 'c' toggle (does not use mouse-motion)
    if key == b'c':
        camera_mode = "FPP" if camera_mode == "TPP" else "TPP"
        print("Switched to", camera_mode)

    # Toggle help overlay with 'h' or 'H'
    if key in (b'h', b'H'):
        global show_controls
        show_controls = not show_controls
        glutPostRedisplay()
        return

    # Toggle TPP zoom level (Z key)
    if key == b'z':
        if camera_mode == "TPP":
            tpp_zoom_level = 1 - tpp_zoom_level  # Toggle between 0 and 1
            zoom_names = ["Far View", "Close View"]
            print(f"TPP Zoom: {zoom_names[tpp_zoom_level]}")

    # Reset game (R key)
    if key == b'r':
        reset_game()


    if key == b'f':
        if cur_lvl >= 5:
            g_mode = "FREE" if g_mode == "GAME" else "GAME"
            print(f"Game mode: {g_mode}")


    base_speed = baby_speed
    if g_mode == "FREE":
        move_speed = base_speed * 2.0 
    else:
        move_speed = base_speed * 2.0 if speed_boost_active else base_speed

    if key == b'w':  # Move forward
        new_x = baby_pos[0] + move_speed * math.sin(math.radians(baby_angle))
        new_y = baby_pos[1] + move_speed * math.cos(math.radians(baby_angle))
        if not check_wall_collision(new_x, new_y) and not check_collision_with_objects(new_x, new_y):
            baby_pos[0] = new_x
            baby_pos[1] = new_y
            baby_is_moving = True
        else:
            # Collision detected - balance penalty based on level (not in free mode)
            if g_mode != "FREE":
                if cur_lvl == 1:
                    balance_meter -= 5
                    print("Baby hit something.")
                elif cur_lvl == 2:
                    balance_meter -= 15# check korbo pore
                    print("Bump! Baby hit something. -15% balance!")
                elif cur_lvl == 3:
                    balance_meter -= 20
                    print("Bump! Baby hit something. -20% balance!")
                elif cur_lvl == 4:
                    balance_meter -= 10
                    print("Bump! Baby hit something. -10% balance!")

                # Check if balance reached 0% - baby falls and loses a life
                if cur_lvl >= 2 and balance_meter <= 0:#check korbo pore
                    baby_is_falling = True
                    baby_fall_timer = time.time()
                    lives_remaining -= 1
                    if lives_remaining > 0:
                        print(
                            f"Baby fell from hitting object! Lives remaining: {lives_remaining}")
                        # Respawn slightly behind current position (away from obstacle)
                        baby_pos[0] -= 30 * math.sin(math.radians(baby_angle))
                        baby_pos[1] -= 30 * math.cos(math.radians(baby_angle))
                        baby_tilt = 0.0
                        balance_meter = 100
                    else:
                        khel_khatam = True
                        print(
                            "Game Over! No lives remaining! Press R to restart from Level 1.")
                    return

    if key == b's':  # Move backward
        new_x = baby_pos[0] - move_speed * math.sin(math.radians(baby_angle))
        new_y = baby_pos[1] - move_speed * math.cos(math.radians(baby_angle))
        if not check_wall_collision(new_x, new_y) and not check_collision_with_objects(new_x, new_y):
            baby_pos[0] = new_x
            baby_pos[1] = new_y
            baby_is_moving = True
        else:
            # Collision detected - balance penalty based on level (not in free mode)
            if g_mode != "FREE":
                if cur_lvl == 1:
                    balance_meter -= 5
                    print("Bump! Baby hit something.")
                elif cur_lvl == 2:
                    balance_meter -= 15
                    print("Bump! Baby hit something. -15% balance!")
                elif cur_lvl == 3:
                    balance_meter -= 20
                    print("Bump! Baby hit something. -20% balance!")
                elif cur_lvl == 4:
                    balance_meter -= 10
                    print("Bump! Baby hit something. -10% balance!")

                # Check if balance reached 0% - baby falls and loses a life
                if cur_lvl >= 2 and balance_meter <= 0:
                    baby_is_falling = True
                    baby_fall_timer = time.time()
                    lives_remaining -= 1
                    if lives_remaining > 0:
                        print(
                            f"Baby fell from hitting object! Lives remaining: {lives_remaining}")
                        # Respawn slightly forward from current position (away from obstacle)
                        baby_pos[0] += 30 * math.sin(math.radians(baby_angle))
                        baby_pos[1] += 30 * math.cos(math.radians(baby_angle))
                        baby_tilt = 0.0
                        balance_meter = 100
                    else:
                        khel_khatam = True
                        print(
                            "Game Over! No lives remaining! Press R to restart from Level 1.")
                    return

    if key == b'd':  # Rotate left
        # Always rotate when 'd' is pressed;wwa
        baby_angle += 5

    if key == b'a':  # Rotate right
        # Always rotate when 'a' is pressed;
        baby_angle -= 5

    # Balance controls: Q (counter-right -> tilt left), E (counter-left -> tilt right)
    if key == b'q':
        if cur_lvl >= 2 and g_mode != "FREE":
            correction = 0.12
            baby_tilt -= correction
            baby_tilt = max(-1.0, min(1.0, baby_tilt))
            print(f"Balance input Q: Tilt now {baby_tilt:.2f}")

    if key == b'e':
        if cur_lvl >= 2 and g_mode != "FREE":
            correction = 0.12
            baby_tilt += correction
            baby_tilt = max(-1.0, min(1.0, baby_tilt))
            print(f"Balance input E: Tilt now {baby_tilt:.2f}")

    if key == b' ':
        if lvl_finish:
            next_level()
        elif cur_lvl == 1 and baby_state == "CRAWLING":
            print("You must crawl in Level 1!")
        elif cur_lvl == 2 and baby_state == "CRAWLING":
            baby_state = "STANDING"
            print("Baby is trying to stand!")
        elif cur_lvl >= 3 and baby_state != "WALKING":
            baby_state = "WALKING"
            print("Baby is walking!")

    # Admin key: Shift+> to skip to next level
    # if key == b'>':
    #     print(f"Admin: Skipping level {cur_lvl}")
    #     lvl_finish = True  # Set to true so next_level() works
    #     next_level()

    # Manual skip: press 'x' to advance to next level immediately
    if key == b'x':
        # Skip to next level when allowed; on level 4, enter Free Mode
        if not khel_khatam and g_mode != "FREE":
            if cur_lvl < 4:
                print(f"User: Skipping level {cur_lvl} via 'x' key")
                lvl_finish = True
                next_level()
                return
            elif cur_lvl == 4:
                # Directly enter free mode from level 4 when user presses 'x'
                g_mode = "FREE"
                baby_state = "WALKING"
                lvl_finish = False
                print("Entering Free Mode! Explore freely with no consequences.")
                initialize_free_mode_collectibles()
                return
        return

    # Reset movement flag (will be set again if movement keys are pressed next frame)
    baby_is_moving = False

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    """A3-style arrow controls (TPP orbit only)."""
    global c_deg, tpp_height_offset, show_controls

    # F1 handling removed; help overlay toggled via 'h' key (keyboardListener)

    if camera_mode != "TPP":
        # In FPP we follow baby automatically; no arrow-based camera changes needed.
        glutPostRedisplay()
        return

    rotatn = 3.0
    h_stp = 20.0

    if key == GLUT_KEY_LEFT:
        c_deg -= rotatn
    elif key == GLUT_KEY_RIGHT:
        c_deg += rotatn
    elif key == GLUT_KEY_UP:
        tpp_height_offset += h_stp
    elif key == GLUT_KEY_DOWN:
        tpp_height_offset -= h_stp

    glutPostRedisplay()


def mouseListener(button, state, x, y):
    """A3-style: Right click toggles TPP/FPP (no mouse-motion camera)."""
    global camera_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = "FPP" if camera_mode == "TPP" else "TPP"
        print("Switched to", camera_mode)
        glutPostRedisplay()


def setupCamera():
    """Configure camera projection and view"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, 1.25, 0.5, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "TPP":
        update_cam_pos()
        x, y, z = camera_pos
        gluLookAt(x, y, z,
                  0, 0, 0,
                  0, 0, 1)
    else:
        # FPP follow (baby clearly visible), camera moves+rotates with baby
        yaw = baby_angle

        follow_dist = 120.0
        cam_height = 130.0

        cam_x = baby_pos[0] - follow_dist * math.sin(math.radians(yaw))
        cam_y = baby_pos[1] - follow_dist * math.cos(math.radians(yaw))
        cam_z = cam_height

        look_dist = 160.0
        look_x = baby_pos[0] + look_dist * math.sin(math.radians(yaw))
        look_y = baby_pos[1] + look_dist * math.cos(math.radians(yaw))
        look_z = 70.0

        camera_pos[0], camera_pos[1], camera_pos[2] = cam_x, cam_y, cam_z

        gluLookAt(cam_x, cam_y, cam_z,
                  look_x, look_y, look_z,
                  0, 0, 1)


def update_game():
    """Update game logic"""
    global balance_meter, score, baby_is_falling, baby_fall_timer
    global collectibles, lvl_finish, cur_lvl, khel_khatam, last_time
    global baby_tilt, last_tilt_time, tilt_speed, lives_remaining
    global room_collectibles, last_baby_room

    if g_pause:
        return

    if khel_khatam:
        return

    # Free mode logic
    if g_mode == "FREE":
        balance_meter = 100  # Always keep balance at 100%

        # Track room changes and respawn collectibles
        current_room = get_baby_room()
        if current_room != last_baby_room and current_room != 0:
            # Baby changed rooms - respawn collectibles in the previous room
            if last_baby_room != 0:
                respawn_room_collectibles(last_baby_room)
            last_baby_room = current_room

        # Handle collectible collection in free mode
        for i, (x, y, item_type, collected) in enumerate(collectibles):
            if not collected:
                distance = math.sqrt(
                    (baby_pos[0] - x)**2 + (baby_pos[1] - y)**2)
                if distance < 40:
                    collectibles[i] = (x, y, item_type, True)
                    # Only toys give points in free mode (harmful items don't affect baby)
                    if item_type not in ["SCISSORS", "KNIFE", "KEYS", "WIRE", "HARMFUL"]:
                        points = COLLECTIBLE_TYPES[item_type]["points"]
                        score += points
                        print(f"Collected {item_type}! +{points} points")
                    else:
                        # Harmful items collected but no effect in free mode
                        print(
                            f"Collected {item_type} (no effect in free mode)")
        return

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Level 1: Normal balance (crawling)
    if cur_lvl == 1:
        if baby_state == "CRAWLING":
            balance_meter += 2 * dt
        balance_meter = max(0, min(100, balance_meter))

        if balance_meter <= 0 and not baby_is_falling:
            baby_is_falling = True
            baby_fall_timer = time.time()
            score -= 10
            print("Baby fell! Balance lost.")

    # Level 2+: Tilt-based balance mechanic with progressive difficulty
    elif cur_lvl >= 2:
        # Level 2: deterministic slow drift to the RIGHT (positive tilt)
        # The player uses A/D to apply corrective tilt inputs. This model
        # produces a smooth gradual drift and allows discrete key presses
        # to nudge the tilt back toward zero (or beyond).
        if cur_lvl == 2:
            # Drift direction depends on baby's facing angle so tilt can go both
            # left and right. Use the yaw's sine as a signed bias (-1..1).
            drift_rate = 0.10  # base units per second
            rad = math.radians(baby_angle)
            # negative = leftward bias, positive = rightward
            bias = math.sin(rad)

            # Apply drift scaled by bias (signed). If bias near zero, use a small
            # random nudge to avoid deadlock when facing straight.
            if abs(bias) < 0.05:
                baby_tilt += drift_rate * dt * random.uniform(-0.4, 0.4)
            else:
                baby_tilt += drift_rate * dt * bias

            # occasional small random perturbations to keep behavior organic
            if random.random() < 0.02:
                baby_tilt += random.uniform(-0.03, 0.03)

            # clamp tilt
            baby_tilt = max(-1.0, min(1.0, baby_tilt))

            # Convert tilt to balance meter (0 tilt = 100 balance, ±1 tilt = 0 balance)
            # But implement slow recovery - balance can only increase gradually
            target_balance = 100 * (1.0 - abs(baby_tilt))

            # Slow balance recovery rate (3% per second for level 2)
            max_recovery_rate = 3.0 * dt

            if target_balance > balance_meter:
                # Slowly recover balance
                balance_meter += min(max_recovery_rate,
                                     target_balance - balance_meter)
            else:
                # Balance can drop immediately
                balance_meter = target_balance

            # Early warnings
            if abs(baby_tilt) > 0.4 and abs(baby_tilt) < 0.6:
                if baby_tilt > 0:
                    print("Tilting right...")
                else:
                    print("Tilting left...")

            # Baby falls immediately when tilt reaches critical threshold
            if abs(baby_tilt) >= 0.6:
                baby_is_falling = True
                baby_fall_timer = time.time()
                lives_remaining -= 1
                if lives_remaining > 0:
                    print(
                        f"Baby fell from tilting too much! Lives remaining: {lives_remaining}")
                    # Respawn slightly away from current position to avoid immediate re-collision
                    # Move baby slightly backward from their facing direction
                    baby_pos[0] -= 20 * math.sin(math.radians(baby_angle))
                    baby_pos[1] -= 20 * math.cos(math.radians(baby_angle))
                    baby_tilt = 0.0
                    balance_meter = 100
                else:
                    khel_khatam = True
                    print(
                        "Game Over! No lives remaining! Press R to restart from Level 1.")
                return
        else:
            # For levels 3 and 4: easier balance (baby is learning to walk)
            # Reduced drift rate = easier to maintain balance
            if cur_lvl == 3:
                drift_rate = 0.07  # 30% slower than level 2
            elif cur_lvl == 4:
                drift_rate = 0.05  # 50% slower than level 2
            else:
                drift_rate = 0.10

            rad = math.radians(baby_angle)
            bias = math.sin(rad)

            if abs(bias) < 0.05:
                baby_tilt += drift_rate * dt * random.uniform(-0.4, 0.4)
            else:
                baby_tilt += drift_rate * dt * bias

            if random.random() < 0.02:
                baby_tilt += random.uniform(-0.03, 0.03)

            baby_tilt = max(-1.0, min(1.0, baby_tilt))

            # Convert tilt to balance meter with slow recovery
            target_balance = 100 * (1.0 - abs(baby_tilt))

            # Progressive recovery rates: Level 3 slightly faster, Level 4 even faster
            if cur_lvl == 3:
                max_recovery_rate = 7.0 * dt  # 7% per second
            else:  # Level 4
                max_recovery_rate = 10.0 * dt  # 10% per second

            if target_balance > balance_meter:
                # Slowly recover balance
                balance_meter += min(max_recovery_rate,
                                     target_balance - balance_meter)
            else:
                # Balance can drop immediately
                balance_meter = target_balance

            # Early warnings
            if abs(baby_tilt) > 0.4 and abs(baby_tilt) < 0.6:
                if baby_tilt > 0:
                    print("Tilting right...")
                else:
                    print("Tilting left...")

            # Baby falls immediately 
            if abs(baby_tilt) >= 0.6:
                baby_is_falling = True
                baby_fall_timer = time.time()
                lives_remaining -= 1
                if lives_remaining > 0:
                    print(
                        f"Baby fell from tilting too much! Lives remaining: {lives_remaining}")
                    baby_pos[0] -= 20 * math.sin(math.radians(baby_angle))
                    baby_pos[1] -= 20 * math.cos(math.radians(baby_angle))
                    baby_tilt = 0.0
                    balance_meter = 100
                else:
                    khel_khatam = True
                    print(
                        "Game Over! No lives remaining! Press R to restart from Level 1.")
                return

    balance_meter = max(0, min(100, balance_meter))

    if baby_is_falling and time.time() - baby_fall_timer > 2:
        baby_is_falling = False
        balance_meter = 50
        print("Baby got back up!")

    for i, (x, y, item_type, collected) in enumerate(collectibles):
        if not collected:
            distance = math.sqrt((baby_pos[0] - x)**2 + (baby_pos[1] - y)**2)
            if distance < 40:  # Increased from 30 to make collection easier
                collectibles[i] = (x, y, item_type, True)
                points = COLLECTIBLE_TYPES[item_type]["points"]
                balance_change = COLLECTIBLE_TYPES[item_type]["balance"]
                score += points
                balance_meter += balance_change
                balance_meter = max(0, min(100, balance_meter))

                # Handle speed boost feature
                global speed_boost_active, speed_boost_collectibles_remaining

                if item_type == "MILK_FEEDER":
                    if cur_lvl in (3, 4):
                        speed_boost_active = True
                        speed_boost_collectibles_remaining = 5
                        print(f"Speed Boost Activated! 2x speed for next 5 collectibles!")
                    else:
                        print("Milk feeder collected (no effect in this level)")
                elif item_type in ["SCISSORS", "KNIFE", "KEYS"]:
                    # Harmful item cancels speed boost
                    if speed_boost_active:
                        speed_boost_active = False
                        speed_boost_collectibles_remaining = 0
                        print(
                            f"Ouch! Speed boost lost! {points} points, {balance_change} balance")
                    else:
                        print(
                            f"Ouch! Collected harmful object! {points} points, {balance_change} balance")
                else:
                    # Regular collectible - decrement boost counter
                    if speed_boost_active:
                        speed_boost_collectibles_remaining -= 1
                        if speed_boost_collectibles_remaining <= 0:
                            speed_boost_active = False
                            speed_boost_collectibles_remaining = 0
                            print(f"Speed boost ended. Back to normal speed.")
                        else:
                            print(
                                f"Collected {item_type}! +{points} points | Boost: {speed_boost_collectibles_remaining} left")
                    else:
                        print(
                            f"Collected {item_type}! +{points} points, +{balance_change} balance")

    all_good_collected = all(collected or item_type in ["SCISSORS", "KNIFE", "KEYS", "WIRE"]
                             for _, _, item_type, collected in collectibles)

    if all_good_collected and not lvl_finish:
        lvl_finish = True
        print(f"Level {cur_lvl} Complete! Moving to next level...")
        # Auto-advance to next level after a short delay
        import threading
        threading.Timer(2.0, next_level).start()

    if score < -50:
        khel_khatam = True
        print("Game Over! Too many mistakes. Press R to restart.")


def reset_game():
    """Reset the game to initial state"""
    global baby_pos, baby_angle, baby_state, score, balance_meter
    global cur_lvl, khel_khatam, lvl_finish, baby_is_falling
    global camera_mode, c_d, c_deg, c_h
    global baby_tilt, last_tilt_time
    global tpp_zoom_level
    global speed_boost_active, speed_boost_collectibles_remaining
    global lives_remaining, g_pause, g_mode

    baby_pos = [0, 0, 0]
    baby_angle = 0
    baby_state = "CRAWLING"
    baby_tilt = 0.0
    last_tilt_time = time.time()
    score = 0
    balance_meter = 100
    cur_lvl = 1
    khel_khatam = False
    lvl_finish = False
    baby_is_falling = False
    speed_boost_active = False
    speed_boost_collectibles_remaining = 0
    lives_remaining = 3
    g_pause = False
    g_mode = "GAME"

    camera_mode = "TPP"
    tpp_zoom_level = 0  # Reset to far view
    tpp_height_offset = 0.0  # Reset height adjustment
    c_d = 900.0
    c_deg = 270.0
    c_h = 600.0

    initialize_collision_objects()
    initialize_collectibles()
    print("Game reset! Level 1 - Crawling Stage")


def next_level():
    """Advance to next level"""
    global cur_lvl, lvl_finish, baby_state, balance_meter
    global speed_boost_active, speed_boost_collectibles_remaining
    global lives_remaining

    if not lvl_finish:
        return

    # Cap level at 4 - don't increment beyond level 4
    if cur_lvl >= 4:
        print("The Baby Can Walk Now!")
        return

    cur_lvl += 1
    lvl_finish = False
    balance_meter = 100
    speed_boost_active = False
    speed_boost_collectibles_remaining = 0
    lives_remaining = 3  # Reset lives for new level

    global baby_tilt, last_tilt_time
    baby_tilt = 0.0
    last_tilt_time = time.time()

    if cur_lvl == 2:
        baby_state = "STANDING"
        print("Level 2 - Standing with Balance! Press A/D to keep balance when tilting!")
    elif cur_lvl == 3:
        baby_state = "STANDING"
        print("Level 3 - Standing Challenge! Keep your balance!")
    elif cur_lvl == 4:
        baby_state = "WALKING"
        print("Level 4 - Walking with Balance! Use W/S to move, A/D to balance!")

    initialize_collectibles()


def idle():
    """Idle function for continuous updates"""
    update_game()
    glutPostRedisplay()


def showScreen():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_floor()
    draw_walls()
    draw_interior_walls()
    draw_room_labels()
    draw_furniture()
    draw_collectibles()
    draw_baby()

    draw_text(
        580, 110, f"Baby Steps - Level {cur_lvl} - {g_mode} Mode")
    if cur_lvl >= 2:
        draw_text(
            580, 80, f"Score: {score} | Balance: {int(balance_meter)}% | Lives: {lives_remaining} | State: {baby_state}")
    else:
        draw_text(
            580, 80, f"Score: {score} | Balance: {int(balance_meter)}% | State: {baby_state}")
    draw_text(580, 50, f"Camera: {camera_mode}")

    if cur_lvl == 4 and lvl_finish:
        # Draw celebration text when level 4 is complete
        glColor3f(1.0, 0.85, 0.0)  # Gold color
        draw_text(230, 450, "The Baby Can Walk Now!",
                  GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(0.4, 1.0, 0.6)  # Bright green
        draw_text(330, 400, "Congratulations!", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1.0, 1.0, 1.0)  # White
        draw_text(300, 350, "Press R to restart")
        glColor3f(0.7, 0.9, 1.0)  # Light blue
        draw_text(270, 320, "Press Enter for Free Mode")
    elif lvl_finish:
        draw_text(300, 400, "LEVEL COMPLETE! Press SPACE for next level")

    if khel_khatam:
        draw_text(350, 400, "GAME OVER! Press R to restart")

    if g_pause:
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        draw_text(350, 450, "GAME PAUSED")
        draw_text(320, 400, "Press ESC to continue")

    if baby_is_falling:
        draw_text(400, 450, "Baby Fell!")

    draw_text(10, 50, "WASD: Move Baby | A/D: Rotate | SPACE: Stand/Walk")
    draw_text(10, 30, "Right Click: Toggle Camera | Arrow Keys: Orbit Camera (TPP)")

    # Draw help overlay on left when toggled with F1
    if show_controls:
        help_lines = [
            "Controls:",
            "W/S: Move forward/back",
            "A/D: Rotate left/right",
            "Q/E: Balance left/right",
            "SPACE: Stand/Walk",
            "Z: Toggle TPP zoom",
            "C: Toggle camera TPP/FPP",
            "R: Reset game",
            "F: Toggle Free Mode (after level 4)",
            "X: Skip level",
            "ESC: Pause/Unpause",
            "F1: Toggle this help"
        ]
        y = 740
        for line in help_lines:
            draw_text(10, y, line)
            y -= 24

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 10)
    wind = glutCreateWindow(b"Teach the baby to walk")

    glEnable(GL_DEPTH_TEST)

    glClearColor(0.7, 0.7, 0.7, 1.0)

    initialize_collision_objects()
    initialize_collectibles()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    print("=" * 60)
    print("BABY STEPS - Learning to Walk Game")
    print("=" * 60)
    print("Controls:")
    print("  WASD       : Move Baby")
    print("  A/D        : Rotate Baby")
    print("  SPACE      : Stand/Walk (level-dependent)")
    print("  Right Click: Toggle Camera Mode (TPP/FPP)")
    print("  Arrow Keys : Camera orbit (TPP only)")
    print("  R          : Reset Game")
    print("  F          : Free Mode (after level 4)")
    print("=" * 60)

    glutMainLoop()


if __name__ == "__main__":
    main()
