from perguntas_respostas import *

#cria um objeto da classe Perguntas
perguntas = Perguntas()

#define as stop words que serão acrescentadas
stopwords = ['prezado', 'prezados', 'prezada', 'prezadas', 'gereg', 'ggali',
             'usuario', 'usuaria', 'deseja','gostaria', 'boa tarde', 'bom dia',
             'boa noite']

#inicializa o atributo de stop words
perguntas.define_stop_words(user_defined_stopwords=stopwords)

#importa as perguntas e as trata
perguntas.importa_textos()

#faz o stemming nas perguntas
#perguntas.stem()

#vetoriza e aplica o tfidf
base_tfidf = perguntas.vec_tfidf(stem=False)

#reduzindo a dimensionalidade
dim = 2000
base_tfidf_reduced = perguntas.SVD(base_tfidf,dim=dim)

#Clustering
print('Começou a clusterização.')
t = time.time()
clusters_por_cosseno = hierarchy.linkage(base_tfidf_reduced,"average", metric="cosine") #pode testar metric="euclidean" também
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)
plt.savefig('dendogram_perguntas.png')
elpsd = time.time() - t
print('Tempo para fazer a clusterização: ' + str(elpsd) + '\n')

limite_dissimilaridade = 0.95
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

#Tentando visualizar os dados e vendo o número de amostras por cluster
info_cluster = perguntas.analisa_clusters(base_tfidf, id_clusters)

perguntas.generate_csvs(info_cluster, id_clusters)
