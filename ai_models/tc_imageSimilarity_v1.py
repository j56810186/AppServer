import turicreate as tc

# Load images from the downloaded data
reference_data  = tc.image_analysis.load_images('images') # 需要被搜尋的圖片們的folder
reference_data = reference_data.add_row_number()

# Save the SFrame for future use
reference_data.save('similarity.sframe')

model = tc.image_similarity.create(reference_data) # 建立相似度model (retrain)
model.save('imageSimilarity.model') # 儲存model，可覆蓋掉舊model，之後load這個新model

# 輸入一張圖片，輸出k張相似的圖片
# query_results = model.query(reference_data[0:10], k=10)
# query_results.head()

# 顯示輸入的那張圖片
# reference_data[9]['image'].show()

# 顯示輸出的k張圖片
# similar_rows = query_results[query_results['query_label'] == 9]['reference_label']
# reference_data.filter_by(similar_rows, 'id').show()

# 顯示相似度的詳細數據
# similarity_graph = model.similarity_graph(k=10)
# similar_images = similarity_graph.edges