import picamera
import picamera.array
import png
import RPi.GPIO as gpio
import time
import numpy as np

def step(direction, steps):
    if direction:
        gpio.output(8, True)
    else:
        gpio.output(8, False)
    
    stepcounter = 0
    while stepcounter < steps:
        gpio.output(7, 1)
        gpio.output(7, 0)
        time.sleep(0.0005)
        stepcounter += 1

def zero():
    while gpio.input(4):
        print(gpio.input(4))
        step(0, 1)
        time.sleep(0.001)

def mono(array):
    '''from stackoverflow - CIE? color to mono conversion'''
    return (0.2125 * array[:,:,0]) + (0.7154 * array[:,:,1]) + (0.0721 * array[:,:,2])


if __name__ == '__main__':
    gpio.setmode(gpio.BCM)
    gpio.setup(7, gpio.OUT)
    gpio.setup(8, gpio.OUT)
    gpio.setup(4, gpio.IN)

    zero()

    x = 1024
    y = 768
    print('setting up camera')
    camera = picamera.PiCamera()
    camera.vflip = True
    print('setting res')
    camera.resolution = (x, y)
    print('building array')
    output = picamera.array.PiYUVArray(camera)



    print('making array')
    image = np.ones((y, x*2), dtype=np.float32)

    n = 10
    locs = []
    for img in range(n):
        print('capturing')
        camera.capture(output, 'yuv')
        xoff = img * int(300/n)
        image[:,xoff:xoff+x] *= (output.array[:,:,0] / output.array[:,:,0].max()) 
        output.truncate(0)
        step(1, int(1700/n))
        time.sleep(0.5) # wait for camera to stabilise

    print('type coearce')
    print(image, image.min(), image.max())
    print( (image*255).astype(np.uint8) )
    print('save')
    png.from_array((np.power(image/image.max(), 1/8)*255).astype(np.uint8), 'L;8').save('output.png')