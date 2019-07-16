import pandas as pd
import re, unicodedata, nltk, time
from stop_words import get_stop_words
nltk.download('stopwords')

#==============================================================================
#Definindo algumas variáveis úteis

# stop-words provisorio
stop_words = get_stop_words('portuguese') + ['','art','dou','secao','pag','pagina', 'in', 'inc', 'obs', 'sob', 'cnpj', 'ltda'] + nltk.corpus.stopwords.words('portuguese')
stop_words = list(dict.fromkeys(stop_words))
#==============================================================================

def importa_dados():
    
    print('\nComeçou a importação dos dados.\n')
    
    #primeiramente importa os dados de forma bruta
    df = pd.read_excel('GGALI__ago2018_a_mai2019.xlsx', sheet_name='Protocolos')
    df = df[['Pergunta','Histórico']]
    perguntas = df['Pergunta'].values.tolist()
    respostas = df['Histórico'].values.tolist()
    
    respostas_1 = [] #respostas que não são E-SIC
    respostas_2 = [] #respostas que são E-SIC
    for resposta in respostas:
        if(re.search('e-sic|E-SIC',resposta) == None):
            respostas_1.append(resposta)
        else:
            respostas_2.append(resposta)
    
    #t = time.time()
    #perguntas = [trata_perguntas(pergunta) for pergunta in perguntas]
    #elpsd = time.time() - t
    #print('Tempo para processar as perguntas: ' + str(elpsd) + '\n')
    
    t = time.time()
    respostas = [trata_respostas(resposta) for resposta in respostas_1]
    elpsd = time.time() - t
    print('Tempo para processar as respostas: ' + str(elpsd) + '\n')
    
    return perguntas, respostas

#Coloca as perguntas no melhor formato para convertê-las para um BOW
def trata_perguntas(texto):
    
    #converte todos caracteres para letra minúscula
    texto_lower = texto.lower()
    texto_lower = re.sub(' +', ' ', texto_lower)
    
    #Remove acentos e pontuação
    texto_sem_acento_pontuacao = limpa_utf8(texto_lower)
    
    #Remove hifens e barras
    texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_acento_pontuacao)
    
    #Troca qualquer tipo de espacamento por espaço
    texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)
    
    #Remove dígitos
    #texto_sem_digitos = re.sub(r'\d','', texto_sem_espacamentos)
    
    #Remove pontuacao e digitos
    texto_sem_pontuacao_digitos = re.sub('[^A-Za-z]', ' ' , texto_sem_espacamentos)
    
    #Tïra o cabeçalho das perguntas
    texto_sem_cabecalho = re.sub(r'empresa.*cnpj','' , texto_sem_pontuacao_digitos)
    
    #Tira despedida
    texto_sem_despedida = re.sub(r'(obrigad|atenciosamente|desde ja).*', '', texto_sem_cabecalho)
    
    #Remove espaços extras
    texto_sem_espacos_extras = re.sub(' +', ' ', texto_sem_despedida)
    
    #Retira stopwords que possam ter reaparecido
    texto_aux = texto_sem_espacos_extras.split()
    texto_limpo = []
    for palavra in texto_aux:
        if (palavra in stop_words) or (len(palavra)==1): 
            texto_limpo.append('')
        else:
            texto_limpo.append(palavra)
    
    texto_limpo = ' '.join(texto_limpo)
    
    return texto_limpo

#Coloca as respostas no melhor formato para convertê-las para um BOW. Retorna os índices das respostas que não estão finalizadas
def trata_respostas(texto):
    
    #converte todos caracteres para letra minúscula
    texto_lower = texto.lower()
    texto_lower = re.sub(' +', ' ', texto_lower)
    
    #Remove acentos e pontuação
    texto_sem_acento_pontuacao = limpa_utf8(texto_lower)
    
    #Remove hifens e barras
    texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_acento_pontuacao)
    
    #Troca qualquer tipo de espacamento por espaço
    texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)
    
    #Remove dígitos
    texto_sem_digitos = re.sub(r'\d','', texto_sem_espacamentos)
    
    #Remove pontuacao
    texto_sem_pontuacao = re.sub('[^A-Za-z]', ' ' , texto_sem_digitos)
    
    #Remove espaços extras
    texto_sem_espacos_extras = re.sub(' +', ' ', texto_sem_pontuacao)
    
    #Pega apenas a resposta final (nem sempre o padrao eh bonitinho)
    m = re.search(r'(prezado a senhor a)? (atencao|resposta|relacao|atendimento)? (contato|solicitacao|questionamento|consulta|preenchimento|questionamentos|\w+)? (.*?) (favor avalie resposta|$)', texto_sem_espacos_extras)
    if m is not None:
        texto_so_resposta_final = m.group(4)
    else:
        
        return ''
    
    #Retira stopwords que possam ter reaparecido
    texto_aux = texto_so_resposta_final.split()
    texto_limpo = []
    for palavra in texto_aux:
        if (palavra in stop_words) or (len(palavra)==1): 
            texto_limpo.append('')
        else:
            texto_limpo.append(palavra)
    
    texto_limpo = ' '.join(texto_limpo)
    
    return texto_limpo


# Recodificacao em utf8, removendo cedilhas acentos e coisas de latin
def limpa_utf8(texto):    

    texto = texto.split()
    texto_tratado = []
    for palavra in texto:
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = unicodedata.normalize('NFKD', palavra)
        palavra_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    
        #remove stopwords
        if palavra_sem_acento in stop_words: 
            texto_tratado.append(' ')
        else:
            texto_tratado.append(palavra_sem_acento)
            
    return ' '.join(texto_tratado)
                
        
    
        
        
        
        
        











