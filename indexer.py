import faiss
import numpy as np
from transformers import AutoTokenizer, TFAutoModel
from data_loader import qa_pairs 

# Charger le modèle de transformers
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = TFAutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def create_vector_db(qa_pairs):
    embeddings = []
    metadata = []
    for question, response in qa_pairs:
        inputs = tokenizer(question, return_tensors="tf")
        outputs = model(**inputs)
        question_embedding = outputs.last_hidden_state[:, 0, :].numpy()
        embeddings.append(question_embedding)
        metadata.append({'question': question, 'response': response})
    
    embeddings = np.array(embeddings).astype('float32')
    embeddings = embeddings.reshape((embeddings.shape[0], embeddings.shape[2]))
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    return index, metadata

# Appeler la fonction create_vector_db avec qa_pairs importé
vector_db, metadata = create_vector_db(qa_pairs)
