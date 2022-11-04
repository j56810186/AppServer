import turicreate as tc
from django.conf import settings
from pathlib import Path

CLASSIFY_MODEL_PATH = str(settings.BASE_DIR / Path('ai_models/7class.model'))

def loadClassifyModel(img_path):
    model = tc.load_model(CLASSIFY_MODEL_PATH)
    # predict image from internet by url
    # imgurl = 'https://fujitiensan.com/wp-content/uploads/2020/04/%E5%AF%8C%E5%A3%AB%E5%B1%B1%E8%A1%A3%E6%9C%8D_FUJI-ROCK-FESTIVAL-1-scaled.jpg'
    # img = tc.Image(imgurl)
    # predict image from local
    img = tc.Image(img_path)
    result = model.predict(img)
    return result

# print(loadClassifyModel('7class.model','skirt_pink.jpeg'))
# print(colorClassify('skirt_pink.jpeg'))
# print(loadSimilarityModel('imageSimilarity.model','test.jpeg'))
# input()
