from imblearn.over_sampling import SMOTE
import pandas as pd

def balancear(dados, coluna_target):
    print(f"> Balanceando dados para a coluna '{coluna_target}'...")
    
    dados_atributos = dados.drop(columns=['Management', 'Severity', 'Diagnosis'])
    dados_classes = dados[coluna_target]

    # Lógica específica para a coluna 'Management'
    if coluna_target == 'Management':
        indices_para_remover = dados[dados['Management'].isin(['secondary surgical', 'simultaneous appendectomy'])].index
        dados_filtrados = dados.drop(indices_para_remover)
        dados_atributos = dados_filtrados.drop(columns=['Management', 'Severity', 'Diagnosis'])
        dados_classes = dados_filtrados['Management']

    resampler = SMOTE(random_state=42)
    dados_atributos_b, dados_classes_b = resampler.fit_resample(dados_atributos, dados_classes)

    dados_final = pd.concat([dados_atributos_b, dados_classes_b], axis=1)
    
    print("> Balanceamento concluído.")
    return dados_final