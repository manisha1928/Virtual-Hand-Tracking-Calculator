#importing libraries........
import cv2
import mediapipe as mp
import numpy as np

# Button class
class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value
        
    def draw(self, img, theme):
        bg_color = themes[theme]["bg"]
        text_color = themes[theme]["text"]
        button_color = themes[theme]["button"]
        
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      bg_color, cv2.FILLED)  # Background
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      button_color, 3)  # Border
        cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, text_color, 2)  #Text


    def checkClicking(self, x, y, img):
        if self.pos[0] < x < self.pos[0] + self.width and self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                          (255, 255, 255), cv2.FILLED)  # Highlight the button when clicked
            cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                          (50, 50, 50), 3)  # Border
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 50),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 4)  # Value inside the button
            return True
        else:
            return False

# Initialize components
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

buttonListValue = [["1", "2", "3", "+"],
                   ["4", "5", "6", "-"],
                   ["7", "8", "9", "*"],
                   ["0", "/", ".", "="],
                   ["%", "^", "", "C"]]  

buttonList = []
for x in range(4):
    for y in range(5):  # Adjust for the extra row
        xPos = x * 70 + 350
        yPos = y * 70 + 100
        buttonList.append(Button((xPos, yPos), 70, 70, buttonListValue[y][x]))

equation = "" 
delayCounter = 0
history = []  # To store the history of calculations

#Set the window to full-screen mode
cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

themes = {
    "dark": {"bg": (45, 45, 45), "text": (255, 255, 255), "button": (100, 100, 100)},
    "light": {"bg": (250, 251, 217), "text": (0, 0, 0), "button": (50, 50, 50)}
}

current_theme = "dark"

def display_history(img):
    y_offset = 150
    for item in history[-5:]:  # Display the last 5 calculations
        cv2.putText(img, item, (10, y_offset), cv2.FONT_HERSHEY_PLAIN, 1.5, themes[current_theme]["text"], 2)
        y_offset += 30

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame")
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Display panel
    cv2.rectangle(img, (350, 30), (350 + 280, 100), themes[current_theme]["bg"], cv2.FILLED)
    cv2.rectangle(img, (350, 30), (350 + 280, 100), themes[current_theme]["button"], 3)
    cv2.putText(img, equation, (355, 80), cv2.FONT_HERSHEY_PLAIN, 2, themes[current_theme]["text"], 2)

    for button in buttonList:
        button.draw(img, current_theme)
        
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = [(int(lm.x * img.shape[1]), int(lm.y * img.shape[0])) for lm in hand_landmarks.landmark]
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if len(lmList) >= 12:
                x, y = lmList[8]
                x_thumb, y_thumb = lmList[4]

                distance = np.sqrt((x - x_thumb) ** 2 + (y - y_thumb) ** 2)

                if distance < 50:
                    for button in buttonList:
                        if button.checkClicking(x, y, img) and delayCounter == 0:
                            if button.value == "=":
                                try:
                                    result = str(eval(equation))
                                    history.append(f"{equation} = {result}")
                                    equation = result
                                except:
                                    equation = "Error"
                            elif button.value == "%":
                                try:
                                    equation = str(float(equation) / 100)
                                except:
                                    equation = "Error"
                            elif button.value == "C":
                                equation = ""
                            elif button.value == "sqrt":
                                try:
                                    equation = str(np.sqrt(float(equation)))
                                except:
                                    equation = "Error"
                            elif button.value == "^":
                                equation += "**"
                            else:
                                equation += button.value
                            delayCounter = 1

    if delayCounter != 0:
        delayCounter += 1
        if delayCounter > 10:
            delayCounter = 0

    display_history(img)  # Display the history of calculations
    cv2.imshow("image", img)
    key = cv2.waitKey(1)
    if key == ord("c"):  # Clear equation
        equation = ""
    if key == ord("t"):  # Toggle theme
        current_theme = "dark" if current_theme == "light" else "light"
    if key == ord("h"):  # Clear history
        history.clear()
    if key == ord('q'):  # Quit
        break

cap.release()
cv2.destroyAllWindows()
