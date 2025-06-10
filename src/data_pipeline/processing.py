import pandas as pd
from ucimlrepo import fetch_ucirepo 

def importar_dataset():
    print("> Buscando dataset do repositório UCI...")
    regensburg_pediatric_appendicitis = fetch_ucirepo(id=938) 
    
    X = regensburg_pediatric_appendicitis.data.features 
    y = regensburg_pediatric_appendicitis.data.targets 
    
    df = pd.concat([X, y], axis=1)
    print("> Dataset importado com sucesso.")
    return df

def preencher_moda(dados, coluna):
    moda = dados[coluna].mode()[0]
    dados[coluna] = dados[coluna].fillna(moda)

def preencher_mediana(dados, coluna):
    mediana = dados[coluna].median()
    dados[coluna] = dados[coluna].fillna(mediana)

def preprocessar_dados(dados):
    print("> Iniciando pré-processamento dos dados...")
    # Listas de colunas definidas diretamente na função
    colunas_para_remover = [
        'Segmented_Neutrophils', 'Appendix_Wall_Layers', 'Target_Sign', 'Appendicolith',
        'Perfusion', 'Perforation', 'Surrounding_Tissue_Reaction', 'Appendicular_Abscess',
        'Abscess_Location', 'Pathological_Lymph_Nodes', 'Lymph_Nodes_Location',
        'Bowel_Wall_Thickening', 'Conglomerate_of_Bowel_Loops', 'Ileus', 'Coprostasis',
        'Meteorism', 'Enteritis', 'Gynecological_Findings'
    ]
    
    colunas_categoricas_moda = [
        'Sex', 'Management', 'Severity', 'Neutrophilia', 'Ketones_in_Urine', 'Stool', 
        'Contralateral_Rebound_Tenderness', 'Coughing_Pain', 'Nausea', 'Loss_of_Appetite', 
        'RBC_in_Urine', 'WBC_in_Urine', 'Dysuria', 'Peritonitis', 'Psoas_Sign', 
        'Ipsilateral_Rebound_Tenderness', 'US_Performed', 'Free_Fluids', 'Diagnosis', 
        'Appendix_on_US', 'Migratory_Pain', 'Lower_Right_Abd_Pain'
    ]
    
    colunas_numericas_mediana = [
        'Age', 'BMI', 'Height', 'Weight', 'Length_of_Stay', 'Appendix_Diameter', 
        'Body_Temperature', 'WBC_Count', 'Neutrophil_Percentage', 'RBC_Count', 
        'Hemoglobin', 'RDW', 'Thrombocyte_Count', 'CRP'
    ]
    
    colunas_score_moda = ['Alvarado_Score', 'Paedriatic_Appendicitis_Score']

    dados = dados.drop(columns=colunas_para_remover)

    for coluna in colunas_categoricas_moda:
        preencher_moda(dados, coluna)

    for coluna in colunas_numericas_mediana:
        preencher_mediana(dados, coluna)

    for coluna in colunas_score_moda:
        preencher_moda(dados, coluna)

    print("> Pré-processamento concluído.")
    input("Pressione ENTER para continuar...")
    return dados