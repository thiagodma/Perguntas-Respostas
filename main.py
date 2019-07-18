import perguntas_respostas_funcoes as prf
import matplotlib.pyplot as plt
import pandas as pd
import time
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.cluster import hierarchy

# stop-words
stop_words = prf.define_stop_words()

#Importa os dados e os retorna já tratados
perguntas, respostas = prf.importa_dados(stop_words)

#Define como saber qual pergunta corresponde a qual resposta quando olhando o csv
perguntas_respostas_id = []

for i in range(len(perguntas)):
    perguntas_respostas_id.append('P' + str(i))

for i in range(len(respostas)):
    perguntas_respostas_id.append('R' + str(i))


#Concatena as duas listas
textos = perguntas + respostas

#Faz o stemming
#textos_stem = prf.stem(textos)

#Vetorizando e aplicando o tfidf
vec = CountVectorizer()
bag_palavras = vec.fit_transform(textos)
feature_names = vec.get_feature_names()
base_tfidf = TfidfTransformer().fit_transform(bag_palavras)
base_tfidf = base_tfidf.todense()

#Reduzindo a dimensionalidade
base_tfidf_reduced = prf.SVD(3000, base_tfidf)

#Clustering
print('Começou a clusterização.')
t = time.time()
clusters_por_cosseno = hierarchy.linkage(base_tfidf_reduced,"average", metric="cosine") #pode testar metric="euclidean" também
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)
elpsd = time.time() - t
print('Tempo para fazer a clusterização: ' + str(elpsd) + '\n')

# Separa a que Cluster pertence cada texto, pela ordem na lista de textos,
# dado o parâmetro de limite de dissimilaridade threshold
limite_dissimilaridade = 0.95
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

#Tentando visualizar os dados e vendo o número de amostras por cluster
analise = prf.analisa_clusters(base_tfidf, id_clusters)

#Colocando em dataframes
X = pd.DataFrame(id_clusters,columns=['cluster_id'])
Y = pd.DataFrame(perguntas_respostas_id ,columns=['perguntas_respostas'])
Z = X.join(Y)

print('Foram encontradas ' + str(max(Z['cluster_id'])) + ' clusters\n')

#Exporta as tabelas
Z.to_csv('cluster_perguntas_respostas_cosseno.csv', sep='|', 
                    index=False, encoding='utf-8')