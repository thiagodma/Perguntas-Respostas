from perguntas_respostas import *

respostas = Respostas()

stopwords = ['prezado', 'prezados', 'prezada', 'prezadas', 'gereg', 'ggali',
             'usuario', 'usuaria', 'deseja','gostaria', 'boa tarde', 'bom dia',
             'boa noite', 'rdc', 'ins', 'geare', 'resposta', 'link','portaria',
             'anvisa','informamos','perguntas','respostas','intrucao','normativa',
             'portanto','decreto','lei','esclarecemos','produto','resolucao',
             'dispoe','sobre','idr','cada','vigilancia','sanitaria','sanitarias',
             ]

#inicializa o atributo de stopwords
respostas.define_stop_words(user_defined_stopwords=stopwords)

#carrega os textos e os trata
respostas.importa_textos()

#faz o stemming nos textos
#respostas.stem()

#vetoriza e aplica o tfidf
base_tfidf = respostas.vec_tfidf(stem=False)

#reduzindo a dimensionalidade
dim = 2000
base_tfidf_reduced = respostas.SVD(base_tfidf,dim=dim)

#Clustering
print('Começou a clusterização.')
t = time.time()
clusters_por_cosseno = hierarchy.linkage(base_tfidf_reduced,"average", metric="cosine") #pode testar metric="euclidean" também
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)
plt.savefig('dendrogram_respostas.png')
elpsd = time.time() - t
print('Tempo para fazer a clusterização: ' + str(elpsd) + '\n')

limite_dissimilaridade = 0.95
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

#Tentando visualizar os dados e vendo o número de amostras por cluster
info_cluster = respostas.analisa_clusters(base_tfidf, id_clusters)

respostas.generate_csvs(info_cluster, id_clusters)
