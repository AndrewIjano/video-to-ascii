import sys
import os
import time
from PIL import Image
from pygame import mixer


def resize_image(img):
    width, height = img.size
    aspect_ratio = height / width
    new_width = 120
    new_height = int(aspect_ratio * new_width * 0.55)
    return img.resize((new_width, new_height))


def image_to_ascii(img):
    img = resize_image(img)

    pixel_types = ['.', ':', '!', '*', '%', '$', '@', '&', '#', 'S', 'B']

    color_codes = [0, 4, 2, 6, 1, 5, 3, 7]

    def is_on(pixel): return pixel > 127

    ascii_pixels = []
    for rgb_pixel, l_pixel in zip(img.convert('RGB').getdata(),
                                  img.convert('L').getdata()):
        r, g, b = rgb_pixel
        color_index = is_on(r) * 4 + is_on(g) * 2 + is_on(b)
        color = f'\033[3{color_codes[color_index]}m'
        pixel = pixel_types[l_pixel // 25]
        ascii_pixels += [color + pixel]

    def lines(pixels, width):
        for i in range(0, len(pixels), width):
            yield pixels[i: i + width]

    width, height = img.size
    ascii_image = '\n'.join(''.join(line)
                            for line in lines(ascii_pixels, width))

    return ascii_image


def frames_to_ascii(directory_name):
    ascii_images = []
    for filename in sorted(os.listdir(directory_name)):
        img = Image.open(directory_name + filename)
        ascii_images += [image_to_ascii(img)]
    return ascii_images


def play_music(video_name):
    mixer.init()
    mixer.music.load(f'.{video_name}.wav')
    mixer.music.play()


def play_video(ascii_frames):
    expected_time = time.time()
    for image in ascii_frames:
        print(image)
        expected_time += 0.1
        time.sleep(max(expected_time - time.time(), 0))
        os.system('clear')


video_name = sys.argv[1]
frames_directory = f'.{video_name}/'
audio_directory = f'.{video_name}.wav'

os.system(f'mkdir {frames_directory}')
os.system(f'ffmpeg -i {video_name} -r 10 {frames_directory}img-%5d.png -loglevel quiet')
os.system(f'ffmpeg -i {video_name} -ac 2 -f wav {audio_directory} -loglevel quiet')

ascii_frames = frames_to_ascii(frames_directory)
play_music(video_name)
play_video(ascii_frames)
