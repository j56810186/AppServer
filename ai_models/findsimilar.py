
import argparse
import numpy as np
import turicreate as tc

from pathlib import Path


def loadSimilarityModel(uid, img_path, model_dir):
    model_path = str(Path(model_dir, str(uid)+'_imageSimilarity.model'))
    model = tc.load_model(model_path)
    img = tc.Image(img_path)
    query_results = model.query(img, k=1)
    similar_rows = query_results[query_results['query_label'] == 0]['reference_label']
    sframe_path = str(Path(model_dir, str(uid)+'_similarity.sframe'))
    reference_data = tc.load_sframe(sframe_path)
    # reference_data.filter_by(similar_rows, 'id')[0]['image'].show()
    similar_img_path = reference_data.filter_by(similar_rows, 'id')[0]['path']
    filename = Path(similar_img_path).stem
    # user id and clothe id.
    uid, cid = [int(i) for i in filename.split('_')]
    return uid, cid

def refreshSimilarityModel(uid, sourceimgfolder, result_path):
    reference_data  = tc.image_analysis.load_images(sourceimgfolder)
    reference_data = reference_data.add_row_number()
    reference_data.save(str(Path(result_path, str(uid)+'_similarity.sframe')))
    model = tc.image_similarity.create(reference_data)
    model.save(str(Path(result_path, str(uid) + '_imageSimilarity.model')))

if __name__ == '__main__':
    # input outfit image
    # refreshSimilarityModel('user1','testuser')
    # print(loadSimilarityModel('user1','testuser/1673.jpg'))
    
    # handle arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', type=bool)
    parser.add_argument('uid', type=int)
    parser.add_argument('path', type=str)
    parser.add_argument('model_dir', type=str)
    args = parser.parse_args()

    # use similarity model.
    if args.refresh:
        func = refreshSimilarityModel
    else:
        func = loadSimilarityModel
    result = func(args.uid, args.path, args.model_dir)
    print('model result:', result)
