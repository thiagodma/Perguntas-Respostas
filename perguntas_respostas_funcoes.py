import pandas as pd
import re, unicodedata
from stop_words import get_stop_words
import nltk
nltk.download('stopwords')

#==============================================================================
#Definindo algumas variáveis úteis

# stop-words provisorio
stop_words = get_stop_words('portuguese') + ['','art','dou','secao','pag','pagina', 'in', 'inc', 'obs', 'sob'] + nltk.corpus.stopwords.words('portuguese')
stop_words = list(dict.fromkeys(stop_words))
#==============================================================================

def importa_dados():
    #primeiramente importa os dados de forma bruta
    df = pd.read_excel('GGALI__ago2018_a_mai2019.xlsx', sheet_name='Protocolos')
    df = df[['Pergunta','Histórico']]
    perguntas = df['Pergunta'].values.tolist()
    respostas = df['Histórico'].values.tolist()
    
    perguntas = [trata_textos(pergunta) for pergunta in perguntas]
    
    
    return perguntas, respostas

def trata_textos(texto):
    
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
    
    #Tïra o cabeçalho das perguntas
    texto_sem_cabecalho = re.sub(r'empresa.*cnpj','' , texto_sem_pontuacao)
    
    #Tira despedida
    texto_sem_despedida = re.sub(r'(obrigad|atenciosamente|desde ja).*', '', texto_sem_cabecalho)
    
    #Remove espaços extras
    texto_sem_espacos_extras = re.sub(' +', ' ', texto_sem_despedida)
    
    return texto_sem_espacos_extras


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
                
        
    
        
        
        
        
        











