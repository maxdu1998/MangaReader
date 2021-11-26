import cv2
import inline as inline
import numpy as np
import easyocr
import matplotlib.pyplot as plt
import urllib.request
import sys
from googletrans import Translator

def recognize_text(img_path):
    '''loads an image and recognizes text.'''

    reader = easyocr.Reader(['en'])
    return reader.readtext(img_path)


def Traduzir(text):
    translator = Translator()
    translate_channel = translator.translate(text, dest='pt_br')
    return translate_channel.text


def overlay_ocr_text(img_path):
    '''loads an image, recognizes text, and overlays the text on the image.'''

    # loads image
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    dpi = 80
    fig_width, fig_height = int(img.shape[0] / dpi), int(img.shape[1] / dpi)
    plt.figure()
    f, axarr = plt.subplots(1, 2, figsize=(fig_width, fig_height))
    axarr[0].imshow(img)
    # recognize text
    result = recognize_text(img_path)
    # if OCR prob is over 0.5, overlay bounding box and text
    for (bbox, text, prob) in result:
        if prob >= 0.5:
            # display
            print(f'Detected text: {text} (Probability: {prob:.2f})')
            # get top-left and bottom-right bbox vertices
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = (int(top_left[0]), int(top_left[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            # create a rectangle for bbox display
            cv2.rectangle(img=img, pt1=top_left, pt2=bottom_right, color=(255, 0, 0), thickness=3)
            # put recognized text
            cv2.putText(img=img, text=Traduzir(text), org=(top_left[0], top_left[1] - 10),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=3)
            # show and save image
            cv2.imwrite(img_path, img)
            return img_path
            # axarr[1].imshow(img)
            # plt.savefig(f'./output/{save_name}_overlay.jpg', bbox_inches='tight')


def TranslateOCR(imglink):
    myfile = "./static/img/temp/temp.jpg"

    ## If file exists, delete it ##
    try:
        urllib.request.urlretrieve(imglink, myfile)
        print("Imagem salva! =)")
        # result = recognize_text(im_1_path)
        return overlay_ocr_text(myfile)

    except:
        erro = sys.exc_info()
        print("Ocorreu um erro:", erro)




