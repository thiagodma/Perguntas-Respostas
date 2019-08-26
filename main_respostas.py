from perguntas_respostas import *
import pandas as pd

respostas = Respostas()

respostas.define_stopwords()

respostas.importa_textos()

#vetoriza e aplica o tfidf
base_tfidf = respostas.vec_tfidf()

#reduzindo a dimensionalidade
dim = 2000
base_tfidf_reduced = respostas.SVD(base_tfidf,dim=dim)

#Clustering
print('Começou a clusterização.')
t = time.time()
clusters_por_cosseno = hierarchy.linkage(base_tfidf_reduced,"average", metric="cosine") #pode testar metric="euclidean" também
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)
elpsd = time.time() - t
print('Tempo para fazer a clusterização: ' + str(elpsd) + '\n')

limite_dissimilaridade = 0.95
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

#Tentando visualizar os dados e vendo o número de amostras por cluster
info_cluster = respostas.analisa_clusters(base_tfidf, id_clusters)

respostas.generate_csvs(info_cluster, id_clusters)