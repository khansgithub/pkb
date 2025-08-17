from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from app.embed import embed_text_bert
from app.snippets import SnippetSourceFile
from app.vector import SklearnVectorStore

snippet_source = SnippetSourceFile(Path(__file__).parent.parent.absolute()/ "app" / "gist.md")
store = SklearnVectorStore()
from asgiref.sync import async_to_sync

snippets = async_to_sync(snippet_source.get_snippets)()
for i, snippet in enumerate(snippets):
    # print(f"Snippet number: {i}")
    # import ipdb; ipdb.set_trace()
    vec = embed_text_bert(str(snippet))
    # print(vec.ndim)
    store.add(vec, snippet)
# store.fit()

pca = PCA(n_components=2)
emb_2d = pca.fit_transform(store.vectors)

query_emb = embed_text_bert("credential")  # returns a 2D array (1 x embedding_dim)

query_emb_2d = pca.transform(query_emb.reshape(1, -1))  # use same PCA

plt.figure(figsize=(8,6))
plt.scatter(emb_2d[:,0], emb_2d[:,1], color='blue', label='Database')
plt.scatter(query_emb_2d[:,0], query_emb_2d[:,1], color='red', label='Query')

for i in range(len(store.metadata)):
    plt.text(emb_2d[i,0]+0.01, emb_2d[i,1]+0.01, f"#{i}", fontsize=9)

plt.legend()
plt.title("Query vs Database Embeddings")
plt.show()
