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

def loadSimilarityModel(uid,img_path):
    model_dir = Path('app/ai_models')
    model_path = str(model_dir.absolute()) + '/' + str(uid)+'_imageSimilarity.model'
    model = tc.load_model(model_path)
    img = tc.Image(img_path)
    query_results = model.query(img, k=1)
    similar_rows = query_results[query_results['query_label'] == 0]['reference_label']
    reference_data = tc.load_sframe(str(uid)+'_similarity.sframe')
    # reference_data.filter_by(similar_rows, 'id')[0]['image'].show()
    similar_img_path = reference_data.filter_by(similar_rows, 'id')[0]['path']
    return similar_img_path

# print(loadClassifyModel('7class.model','skirt_pink.jpeg'))
# print(colorClassify('skirt_pink.jpeg'))
# print(loadSimilarityModel('imageSimilarity.model','test.jpeg'))
# input()
