import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import gc9a01a


BORDER = 20
FONTSIZE = 24
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

class LCD:
    def __init__(self):

        ## Display Setup of 1.28" Neopixel Ring
        #
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D27)
        BAUDRATE = 24000000
        spi = board.SPI()
        self.disp = gc9a01a.GC9A01A(spi, rotation=0,
                               width=240, height=240,
                               x_offset=0, y_offset=0,
                               cs=cs_pin,
                               dc=dc_pin,
                               rst=reset_pin,
                               baudrate=BAUDRATE,
                               )
        self.width = self.disp.width
        self.height = self.disp.height
        self.bold_font = ImageFont.truetype(BOLD, FONTSIZE)

        ######### Chess Board Code ###########
        self.chessback = Image.open("8-bit_chess.png")
        scaled_width = self.width
        scaled_height = self.chessback.height * self.width // self.chessback.width
        self.chessback = self.chessback.resize((scaled_width, scaled_height), Image.BICUBIC)
        x = scaled_width // 2 - self.width // 2
        y = scaled_height // 2 - self.height // 2
        self.chessback = self.chessback.crop((x, y, x + self.width, y + self.height)) 
        ######### Change Alpha Value ################
        self.chessback = self.chessback.convert("RGBA")
        background = Image.new("RGBA", self.chessback.size, (0, 0, 0, 255))
        alpha = 120  
        self.chessback.putalpha(alpha)
        self.chessback = Image.alpha_composite(background, self.chessback)
        self.chessback = self.chessback.convert("RGB")


        ####### Victory Code #######
        self.victory = Image.open("victory.webp")
        self.victory = self.victory.resize((scaled_width, scaled_height), Image.BICUBIC)
        self.victory = self.victory.crop((x, y, x + self.width, y + self.height))
        self.victory_rot = self.victory.rotate(270)  ## Copy for rotation


        ####### Loss Code #######
        self.lose = Image.open("sad_pic.jpg")
        self.lose = self.lose.resize((scaled_width, scaled_height), Image.BICUBIC)
        self.lose = self.lose.crop((x, y, x + self.width, y + self.height))
        self.lose_left_rot = self.lose.rotate(25)
        self.lose_right_rot = self.lose.rotate(-25) 
       

    def get_box(self, draw, text, font):
        bbox = draw.multiline_textbbox((0, 0), text, font=font)
        width  = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height
        
    def draw_centered_text(self, image, text, BOLD, font_size, fill):
        draw = ImageDraw.Draw(image)
        text_width, text_height = self.get_box(draw, text, self.bold_font)

        # Center position
        x = (self.width  - text_width)  // 2
        y = (self.height - text_height) // 2

        draw.text((x,y),text,font=self.bold_font,fill=fill, align="center")


    def game_selection(self):
        self.disp.image(self.chessback)
        self.draw_centered_text(self.chessback, "Waiting for game \n selection...", BOLD, FONTSIZE-1, fill="white")
        time.sleep(3)

    def show_victory(self):
        self.disp.image(self.victory)
        time.sleep(0.05)
        self.disp.image(self.victory_rot)
        time.sleep(0.05)


    def show_lose(self):
        self.disp.image(self.lose_left_rot)
        time.sleep(1)
        self.disp.image(self.lose_right_rot)
        time.sleep(1)

# Create Class for LCD Ring
#
myLCD = LCD()

while True:
    
    # Game Selection screen: Text Displaying Waiting for game selection
    myLCD.game_selection()
    time.sleep(1)
    # Victory 
    myLCD.show_victory()
    time.sleep(1)
    # Game Loss
    myLCD.show_lose()
    time.sleep(1)
    # Active Game: Show Score 
    
