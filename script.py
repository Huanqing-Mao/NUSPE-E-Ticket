import pandas as pd
import hashlib
import base64
import code128
from PIL import Image, ImageDraw, ImageFont

NUM_TICKETS = 200
BARCODE_TEXT_PATTERN = lambda x: '20221023' + f'{x:03d}'
BARCODE_VALUE_PATTERN = lambda x: 'PE20221023' + f'{x:03d}' + 'FC'

hashes = {}

for i in range(1, NUM_TICKETS + 1):

    # Get barcode value hash
    m = hashlib.md5()
    m.update(BARCODE_VALUE_PATTERN(i).encode('utf-8'))
    barcode_value = base64.b64encode(m.digest())[:8]

    # Get barcode text
    barcode_text = BARCODE_TEXT_PATTERN(i)

    # Add hash to dictionary
    hashes[barcode_text] = barcode_value.decode('utf-8')

    # Create barcode image
    barcode_image = code128.image(barcode_value, height=100)

    # Make background transparent
    barcode_image = barcode_image.convert('RGBA')
    temp = []
    for item in barcode_image.getdata():
        if item[:3] == (255, 255, 255):
            temp.append((255, 255, 255, 0))
        else:
            temp.append(item)
    barcode_image.putdata(temp)

    # Open image
    image = Image.open('ticket.png')

    # Rotate image
    im_r90 = image.rotate(90, expand=1)

    # Paste barcode
    im_r90.paste(barcode_image, (60, 1835), barcode_image)

    # Write barcode text
    font_type = ImageFont.truetype('arial.ttf', 35)
    draw = ImageDraw.Draw(im_r90)
    draw.text((215,1780), barcode_text, (0,0,0), font_type)

    # Rotate back to original
    im_r0 = im_r90.rotate(-90, expand=1)

    # Save image
    new_file = barcode_text + '.png'
    im_r0.save(new_file, 'PNG')

    # Show in default viewer
    # import webbrowser
    # webbrowser.open(new_file)


# Format text and its hashcode
df = pd.DataFrame(
    data=[
        [int(i) for i in range(1, NUM_TICKETS + 1)],
        [int(key) for key in hashes.keys()],
        hashes.values()],
    index=['TicketNo', 'BarcodeNo', 'HashCode']).T

# Write dataframe to excel
df.to_excel('Hashes.xlsx', index=False) 

'''
Sources
https://stackoverflow.com/questions/65471637/how-to-include-barcode-value-with-actual-barcode-python-code128-module
https://clay-atlas.com/us/blog/2020/11/28/python-en-package-pillow-convert-background-transparent/
https://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil
https://docs.python.org/2/library/hashlib.html
'''
