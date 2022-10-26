import numpy as np
import turicreate as tc
from app.ai_models.tc_loadmodel import *

def refreshSimilarityModel(uid, sourceimgfolder):
    reference_data  = tc.image_analysis.load_images(sourceimgfolder)
    reference_data = reference_data.add_row_number()
    reference_data.save(str(uid)+'_similarity.sframe')
    model = tc.image_similarity.create(reference_data)
    model.save(str(uid)+'_imageSimilarity.model')

if __name__ == '__main__':
    # input outfit image
    refreshSimilarityModel('user1','testuser')
    print(loadSimilarityModel('user1','testuser/1673.jpg'))