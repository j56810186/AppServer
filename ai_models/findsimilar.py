
import argparse
import numpy as np
import turicreate as tc


def loadSimilarityModel(uid, img_path):
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

def refreshSimilarityModel(uid, sourceimgfolder):
    reference_data  = tc.image_analysis.load_images(sourceimgfolder)
    reference_data = reference_data.add_row_number()
    reference_data.save(str(uid)+'_similarity.sframe')
    model = tc.image_similarity.create(reference_data)
    model.save(str(uid)+'_imageSimilarity.model')

if __name__ == '__main__':
    # input outfit image
    # refreshSimilarityModel('user1','testuser')
    # print(loadSimilarityModel('user1','testuser/1673.jpg'))
    
    # handle arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', type=bool)
    parser.add_argument('uid', type=int)
    parser.add_argument('path', type=str)
    args = parser.parse_args()

    # use similarity model.
    if args.refresh:
        result = refreshSimilarityModel(args.uid, args.path)
    else:
        result = loadSimilarityModel(args.uid, args.path)

    print(result)
