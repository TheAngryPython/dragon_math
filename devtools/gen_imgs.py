from PIL import Image, ImageDraw, ImageFont
import os

game_folder = os.path.split(os.path.dirname(__file__))[0]
assets_folder = os.path.join(game_folder, 'assets')
fonts_folder = os.path.join(assets_folder, 'fonts')
ex_font = os.path.join(assets_folder, 'ex.ttf')
img_folder = os.path.join(assets_folder, 'img')
size = 75
color = (255, 255, 255)

lst = '0123456789+'

font = ImageFont.truetype(ex_font, size=size)

for text in lst:
    print(f'gen {text}')

    img = Image.new('RGBA', (size, size))    
    idraw = ImageDraw.Draw(img)

    idraw.text((size/5, -(size/2)), text, font=font, fill=color)

    try:
        os.remove(os.path.join(img_folder, 'ex_'+text+'.png'))
        print('deleted')
    except:
        pass
    
    img.save(os.path.join(img_folder, 'ex_'+text+'.png'))
    print('done')
