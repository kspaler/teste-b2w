# Bibliotecas
from datetime import datetime, timedelta  
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
import json 
import pandas as pd 
from pandas.io.json import json_normalize #package for flattening json in pandas df
import os

home_dir='~/Documents/teste-b2w'

stream = os.popen('echo ~/Documents/teste-b2w')
output = stream.read()
dir_home=output.split('\n')[0]
dir_input=dir_home+'/input'
dir_work=dir_home+'/work'
dir_output=dir_home+'/output'
dir_done=dir_home+'/done'
file_output='abandoned-carts.json'
file_input='page-views.json'


def processa_arquivos():
    with open(dir_work+'/'+file_input,'r', encoding='utf8', errors='ignore') as f:
        data = [json.loads(line) for line in f]

    #estrutura o JSON em colunas
    df = json_normalize(data)

    #ordena os dados caso não estejam
    df_sorted=df.sort_values(by=['customer', 'timestamp'])

    arq = open(dir_work+'/'+file_output, "w")
    cliente_atual=''
    timestamp_atual=datetime.now()
    entrou_carrinho=False
    finalizou_compra=False
    last_row=''

    type(timestamp_atual)

    #itera em todas as linhas do dataframe
    for index,row in df_sorted.iterrows():
        #print(row)
        # verifica se mudou o cliente ou a compra foi finalizada ou passaram mais de 10 minutos
        if(cliente_atual != row.customer or finalizou_compra==True or datetime.strptime(row.timestamp, '%Y-%m-%d %H:%M:%S')-timestamp_atual>timedelta(seconds=600)):
            # primeira linha não entra aqui
            if(cliente_atual!=''):
                if (entrou_carrinho==True and finalizou_compra==False):
                    #print('escreveu')
                    arq.write(last_row.drop('page').to_json()+'\n')
                entrou_carrinho=False
                finalizou_compra=False
            cliente_atual = row.customer
        #realiza as marcações de entrou no carrinho ou no checkout
        if(row.page=='checkout'):
            finalizou_compra=True
        elif(row.page=='basket'):
            entrou_carrinho=True  
        timestamp_atual=datetime.strptime(row.timestamp, '%Y-%m-%d %H:%M:%S')
        last_row=row
    # tratamento da última linha  
    if(cliente_atual!=''and entrou_carrinho==True and finalizou_compra==False):
        #print('escreveu')
        arq.write(last_row.drop('page').to_json()+'\n')  
    arq.close()

    



# Parâmetros default do DAG

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    # Exemplo: Inicia em 01 de Janeiro de 2021
    'start_date': datetime(2021, 1, 1,9,0,0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    # Em caso de erros, tente rodar novamente apenas 1 vez
    'retries': 1,
    # Tente novamente após 30 segundos depois do erro
    'retry_delay': timedelta(seconds=30),
    # Execute uma vez a cada 1 dia
    'schedule_interval': '@daily'
}


with DAG(    
    dag_id='dag_carrinhos_abandonados',
    default_args=default_args,
    schedule_interval=None,
    tags=['exemplo'],
) as dag:    

    # Primeira tarefa
    t1 = BashOperator(bash_command="mv "+dir_input+"/"+file_input+" "+dir_work+"/"+file_input, task_id="move_arq_entrada") 

    # Vamos Definir a nossa Primeira Tarefa 
    t2 = PythonOperator(task_id="processa",python_callable=processa_arquivos)

    # Terceira tarefa
    t3= BashOperator(bash_command="mv "+dir_work+"/"+file_output+" "+dir_output+"/"+file_output, task_id="move_arq_saida")        

    # Quarta tarefa
    t4= BashOperator(bash_command="mv "+dir_work+"/"+file_input+" "+dir_done+"/"+file_input, task_id="move_arq_done")   

    # Configurar a tarefa T2 para ser dependente da tarefa T1
    t1 >> t2 >> t3 >> t4
