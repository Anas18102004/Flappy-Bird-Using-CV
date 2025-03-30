import cv2
import mediapipe as mp
import pygame
import random

# Initialize MediaPipe Hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load and scale background image to fit the screen
background_image = pygame.image.load("bkg.png").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_rect = background_image.get_rect()


# Load and scale bird image
bird_image = pygame.image.load("blue.png").convert_alpha()
bird_radius = 20
bird_image = pygame.transform.scale(bird_image, (3* bird_radius, 3* bird_radius))

# Game variables
bird_x = 100
bird_y = SCREEN_HEIGHT // 2
bird_velocity = 0
gravity = 0.5
flap_strength = -10

# Obstacle variables
obstacle_width = 70
obstacle_height = random.randint(150, 450)
obstacle_gap = 200
obstacle_x = SCREEN_WIDTH
obstacle_speed = 5  # Initial obstacle speed

# Scoring
score = 0
font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

# Initialize webcam
cap = cv2.VideoCapture(0)

def recognize_hand_gesture(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks for debugging
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Get the coordinates of the index finger tip (landmark 8)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            # Convert the normalized coordinates to pixel coordinates
            hand_x = int(index_finger_tip.x * frame.shape[1])
            hand_y = int(index_finger_tip.y * frame.shape[0])
            return hand_x, hand_y
    return None, None

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True

def update_bird(hand_y):
    global bird_y
    if hand_y is not None:
        bird_y = int(hand_y * SCREEN_HEIGHT / cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # print(f"Bird Position: ({bird_x}, {bird_y})")  # Debugging

def update_obstacles():
    global obstacle_x, obstacle_height, score, obstacle_speed
    
    obstacle_x -= obstacle_speed

    if obstacle_x < -obstacle_width:
        obstacle_x = SCREEN_WIDTH
        obstacle_height = random.randint(150, 450)
        score += 1

        # Increase speed every 5 points
        if score % 3 == 0:
            obstacle_speed += 4

def check_collision():
    if (bird_x + bird_radius > obstacle_x and bird_x - bird_radius < obstacle_x + obstacle_width) and (bird_y - bird_radius < obstacle_height or bird_y + bird_radius > obstacle_height + obstacle_gap):
        return True
    if bird_y - bird_radius <= 0 or bird_y + bird_radius >= SCREEN_HEIGHT:
        return True
    return False

def draw_game():
    screen.blit(background_image, background_rect)  # Draw the background image
    
    # Draw the bird image
    bird_rect = bird_image.get_rect(center=(bird_x, bird_y))
    screen.blit(bird_image, bird_rect)
    
    # Draw the obstacles
    pygame.draw.rect(screen, (0, 255, 0), (obstacle_x, 0, obstacle_width, obstacle_height))  # Draw top obstacle
    pygame.draw.rect(screen, (0, 255, 0), (obstacle_x, obstacle_height + obstacle_gap, obstacle_width, SCREEN_HEIGHT))  # Draw bottom obstacle

    # Display score
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()  # Update the display

def main():
    running = True
    try:
        while running:
            running = handle_events()

            # Capture frame from webcam
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame from webcam")
                break

            # Hand gesture recognition
            hand_x, hand_y = recognize_hand_gesture(frame)

            # Update game state
            update_bird(hand_y)
            update_obstacles()

            # Check for collisions
            if check_collision():
                print("High Score: " + str(score))
                print("Game Over!")
                break

            # Draw the game
            draw_game()

            # Display the frame in OpenCV window
            cv2.imshow('Hand Gesture Recognition', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            clock.tick(30)  # Control the frame rate
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        pygame.quit()
        hands.close()

if __name__ == "__main__":
    main()
