from PIL import Image


image = Image.open('input.jpg')
image = image.convert('RGBA')
# Transparency
newImage = []
for item in image.getdata():
    if item[:3] == (255, 255, 255):
        newImage.append((255, 255, 255, 0))
    else:
        newImage.append(item)

image.putdata(newImage)
image.save('output.png')


print(image.mode, image.size)