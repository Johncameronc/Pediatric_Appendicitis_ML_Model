# normalization.py

import pandas as pd
from sklearn import preprocessing
from pickle import dump, load
from pathlib import Path

# --- CAMINHOS E CONSTANTES ---
NORMALIZER_MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "modelo_normalizador.pkl"

# Lista de colunas numéricas definida como uma constante para ser reutilizada
COLUNAS_NUMERICAS = [
    'Age', 'BMI', 'Height', 'Weight', 'Length_of_Stay', 'Appendix_Diameter', 'Body_Temperature', 
    'WBC_Count', 'Neutrophil_Percentage', 'RBC_Count', 'Hemoglobin', 'RDW', 'Thrombocyte_Count',
    'CRP', 'Alvarado_Score', 'Paedriatic_Appendicitis_Score'
]

def normalizar_dados(dados):
    colunas_numericas_df = dados[COLUNAS_NUMERICAS]

    # Remover colunas numéricas e target do dataframe original
    colunas_categoricas = dados.drop(columns=colunas_numericas_df.columns)
    colunas_categoricas = colunas_categoricas.drop(columns=['Severity', 'Diagnosis', 'Management'])
    colunas_target = dados[['Severity', 'Diagnosis', 'Management']]

    # Cria e treina o normalizador
    normalizador = preprocessing.MinMaxScaler()
    modelo_normalizador = normalizador.fit(colunas_numericas_df)

    # Normaliza os dados
    dados_num_normalizados = modelo_normalizador.transform(colunas_numericas_df)
    dados_num_normalizados = pd.DataFrame(dados_num_normalizados, columns=COLUNAS_NUMERICAS)

    # Processa colunas categóricas (One-Hot Encoding)
    dados_cat_normalizados = pd.get_dummies(colunas_categoricas, dtype='int')
    
    # Reseta o índice para garantir a concatenação correta
    dados_num_normalizados.reset_index(drop=True, inplace=True)
    dados_cat_normalizados.reset_index(drop=True, inplace=True)
    colunas_target.reset_index(drop=True, inplace=True)
    
    # Junta tudo
    dados_normalizados = pd.concat([dados_num_normalizados, dados_cat_normalizados, colunas_target], axis=1)

    # Salva o modelo normalizador
    with open(NORMALIZER_MODEL_PATH, "wb") as f:
        dump(modelo_normalizador, f)

    return dados_normalizados

def normalizar_paciente(paciente):
    try:
        print(NORMALIZER_MODEL_PATH)
        with open(NORMALIZER_MODEL_PATH, "rb") as f:
            modelo_normalizador = load(f)
    except FileNotFoundError:
        print(f"ERRO: Modelo normalizador '{NORMALIZER_MODEL_PATH.name}' não encontrado!")
        return None

    # Separa colunas numéricas e categóricas
    colunas_numericas_df = paciente[COLUNAS_NUMERICAS]
    colunas_categoricas = paciente.drop(columns=COLUNAS_NUMERICAS)

    # Normaliza dados numéricos
    paciente_num_normalizados = modelo_normalizador.transform(colunas_numericas_df)
    paciente_num_normalizados = pd.DataFrame(paciente_num_normalizados, columns=COLUNAS_NUMERICAS)

    # Aplica One-Hot Encoding nos dados categóricos
    paciente_cat_normalizados = pd.get_dummies(colunas_categoricas, dtype='int')
    
    # Junta os dataframes
    paciente_normalizado = pd.concat([paciente_num_normalizados, paciente_cat_normalizados], axis=1)

    # Garante que todas as colunas do modelo estejam presentes
    from app.inference import ENCODED_FEATURES_NAMES # Importa a lista de colunas esperada pelo modelo
    paciente_final = pd.DataFrame(columns=ENCODED_FEATURES_NAMES)
    paciente_final = pd.concat([paciente_final, paciente_normalizado], ignore_index=True).fillna(0)

    return paciente_final[ENCODED_FEATURES_NAMES] # Retorna na ordem correta e com todas as colunas

# --- NOVA FUNÇÃO ---
def desnormalizar_paciente(paciente_normalizado):
    try:
        with open(NORMALIZER_MODEL_PATH, "rb") as f:
            modelo_normalizador = load(f)
    except FileNotFoundError:
        print(f"ERRO: Modelo normalizador '{NORMALIZER_MODEL_PATH.name}' não encontrado!")
        print("Execute o treinamento para gerar o modelo primeiro.")
        return None

    # Seleciona apenas as colunas numéricas do dataframe de entrada
    dados_numericos_para_reverter = paciente_normalizado[COLUNAS_NUMERICAS]

    # Aplica a transformação inversa
    dados_desnormalizados = modelo_normalizador.inverse_transform(dados_numericos_para_reverter)

    # Converte o resultado de volta para um DataFrame com as colunas corretas
    paciente_desnormalizado_df = pd.DataFrame(dados_desnormalizados, columns=COLUNAS_NUMERICAS, index=paciente_normalizado.index)

    return paciente_desnormalizado_df