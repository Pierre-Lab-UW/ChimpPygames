from threading import Thread
import cv2
import numpy as np
import pandas as pd
import time

start_time = time.time()

class ColorObject:
    def __init__(self, lower_bound:list[int], upper_bound: list[int]) -> None:
        self.lower_bound: np.array = np.array(lower_bound, dtype = "uint8")
        self.upper_bound: np.array =  np.array(upper_bound, dtype = "uint8")

    def filter_image(self, image_src:np.array) -> np.array:
        #create a color mask for the cones
        color_mask = self.get_color_mask(image_src)
        color_mask = cv2.erode(color_mask, np.ones((3, 3), np.uint8), iterations = 1)

        #create a new image with a filter
        #frame_filter = cv2.bitwise_or(image_src, image_src, mask = color_mask)
        frame_filter_2 = cv2.bitwise_or(image_src, image_src, mask = color_mask)
        
        #combined = cv2.bitwise_or(frame_filter, frame_filter_2)
        return frame_filter_2

    def get_color_percentage(self, image: np.array) -> float:
        color_mask = self.get_color_mask(image)

        # Calculate the total number of pixels in the image
        total_pixels = image.size // image.itemsize

        # Calculate the number of pixels within the specified color range
        color_pixels = np.sum(color_mask > 0)
        # Calculate the percentage of pixels within the specified color range
        color_percentage = (color_pixels / total_pixels) * 100

        return color_percentage

    def get_color_mask(self, image: np.array):
        frame_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return cv2.inRange(frame_hsv, self.lower_bound, self.upper_bound)
    
class CombinedMask(ColorObject):
    def __init__(self, lower_bound: list[int], upper_bound: list[int], c1: ColorObject, c2: ColorObject) -> None:
        super().__init__(lower_bound, upper_bound)
        self.color1:ColorObject = c1
        self.color2: ColorObject = c2
    
    def get_color_mask(self, image: np.array):
        return cv2.bitwise_or(self.color1.get_color_mask(image), self.color2.get_color_mask(image))

def build_color_dictionary() -> dict[str, ColorObject]:
    df: pd.DataFrame = pd.read_csv('color_config.csv')
    color_dictionary: dict[str, ColorObject] = {}
    color_list = []
    #add all colors in that are not combined colors
    for ind in df.index:
        if df['combined_colors'][ind] == 'Nan':
            color_dictionary[df["Color_name"][ind]] = ColorObject([df['H_min'][ind], df['S_min'][ind], df['V_min'][ind]],
                                                 [df['H_max'][ind], df['S_max'][ind], df['V_max'][ind]])
    #add all the combined colors in
    for ind in df.index: 
        if df['combined_colors'][ind] != 'Nan':
            colors:str = df["combined_colors"][ind]
            colors_split:list[str] = colors.split(',')
            colors_split[0] = colors_split[0].strip()
            colors_split[1] = colors_split[1].strip()
            print(colors_split)
            c1: ColorObject = color_dictionary[colors_split[0]]

            c2: ColorObject = color_dictionary[colors_split[1]]
            color_dictionary[df['Color_name'][ind]] = CombinedMask([],[], c1, c2)
    #delete all colros that are only parts
    for ind in df.index: 
        if (df['is_full_color'][ind] == False):
            print(df['is_full_color'][ind])
            color_dictionary.pop(df['Color_name'][ind])
    return color_dictionary


# color_blue:Color = Color([106,50,50],[114,255,255])
# color_red_1:Color = Color([0,50,80], [4,255,255])
# color_red_2:Color = Color([165,70,80], [178,255,255])
# color_red: Color = CombinedMask([0,80,80], [5,255,255],color_red_1, color_red_2)

#color_dictionary: dict[str, Color] = {'Red':color_red, 'Blue':color_blue}
color_dictionary = build_color_dictionary()

frame_hsv: np.array = None

class State():
    def __init__(self) -> None:
        self.max_color = None

state_color = State()
def color_search() -> None:
    #window callback function
    def mouseClick(event, x, y, flags, params):
        #check if buton pressed is a left mouse button being pressed
        if event == cv2.EVENT_LBUTTONDOWN:
            #get the pixel color in hsv from the x an y position of the mouse click and print it
            hsv = frame_hsv[y,x]
            print("The mouse was clicked at x= ", x, "y = ", y)
            print("Hue = ", hsv[0],  "Sat = ", hsv[1], "Val = ", hsv[2])

    #cv2.namedWindow("Main")
    #cv2.setMouseCallback("Main", mouseClick, param = None)


    # Open the default camera (you can change the parameter to use a different camera)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        # Read a frame from the camera
        ret, frame = cap.read()


        global frame_hsv
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)        

        for index, color_str in enumerate(color_dictionary):
            #cv2.imshow('Color isolation '+str(color_str), color_dictionary[color_str].filter_image(frame))
            percentage_val = color_dictionary[color_str].get_color_percentage(frame)
            #frame = cv2.putText(frame, str(color_str)+':'+str(percentage_val), (50, 100+(50*index)), cv2.FONT_HERSHEY_SIMPLEX,  
                        # 1, (0,0,0), 2, cv2.LINE_AA)

        #cv2.imshow('Main', frame)
        mc = calc_max_color(color_dictionary, frame)
        state_color.max_color = mc
        print("Max color: "+ str(state_color.max_color))
        #print(color_test.get_color_percentage(frame))
        # Check for the 'q' key to exit the loop and terminate the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            

    # Release the camera
    cap.release()
    cv2.destroyAllWindows()
    return calc_max_color(color_dictionary, frame)

    

def calc_max_color(colors:dict[str, ColorObject], image:np.array):
    max_key = None 
    max_value = 0.02
    for str, color in colors.items():
        if color.get_color_percentage(image) > max_value:
            max_value = color.get_color_percentage(image)
            max_key = str
    return max_key

def run():
    t = Thread(target=color_search, args=(), daemon=True)
    t.start()

if __name__ == "__main__":
    color_search(10)
    print("Program terminated.")
