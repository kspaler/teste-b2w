# teste-b2w
Desenvolver um job para encontrar carrinhos abandonados pelos clientes de um e-commerce. 

# Cenário proposto

Desenvolver um job para encontrar carrinhos abandonados pelos clientes de um e-commerce. Embora o assunto seja rico, no teste a definição de abandono de carrinho será simplificada.

# Regra de abandono de carrinho

A regra de abandono de carrinho é simples.

* Definimos como sessão, uma janela de 10 minutos onde o cliente interage (visualiza páginas) no nosso site
* O tempo de sessão é renovado a cada nova interação
* O fluxo de páginas padrão de um pedido é: product -> basket -> checkout
* Um abandono pode ser identificado por um fluxo interrompido na página basket: product -> basket dentro de uma sessão

Por exemplo:

* Um cliente visualiza a página de produto (product) às 12:00
* O mesmo cliente visualiza a página de carrinho (basket) às 12:02
* O mesmo cliente visualizar a página de pagamento (checkout) às 12:04
* Nào temos uma abandono 

Outro exemplo:

* Outro cliente visualiza a página de produto (product) às 13:00
* O mesmo cliente visualiza a página de carrinho (basket) às 13:01
* O cliente fica 15 minutos sem visualizar nenhuma página (pode ter ido tomar um café). Como sua última interação foi às 13:01, sua sessão terminou às 13:11
* Aqui temos um abandono 

Mais um exemplo:

* Um terceiro cliente visualiza a página de produto (product) às 14:00
* O mesmo cliente visualiza a página de carrinho (basket) às 14:05
* O mesmo cliente visualizar outra página de produto (product) às 14:10
* O mesmo cliente visualiza ainda outra página de produto (product) às 14:16
* O mesmo cliente visualiza a página de carrinho (basket) novamente às 14:20
* O mesmo cliente visualiza a página de pagamento (checkout) às 14:21
* Não temos um abandono 

# Testes

Executar o job, lendo o arquivo input/page-views.json e escrevendo no arquivo output/abandoned-carts.json.

O arquivo input/page-views.json deve conter algumas visualizações de páginas:


  { "timestamp": "2019-01-01 12:00:00", "customer": "customer-1", "page": "product", "product": "product-1" }
  { "timestamp": "2019-01-01 12:02:00", "customer": "customer-1", "page": "basket", "product": "product-1" }
  { "timestamp": "2019-01-01 12:04:00", "customer": "customer-1", "page": "checkout" }
  { "timestamp": "2019-01-01 13:00:00", "customer": "customer-2", "page": "product", "product": "product-2" }
  { "timestamp": "2019-01-01 13:02:00", "customer": "customer-2", "page": "basket", "product": "product-2" }
  { "timestamp": "2019-01-01 14:00:00", "customer": "customer-3", "page": "product", "product": "product-3" }
  { "timestamp": "2019-01-01 14:05:00", "customer": "customer-3", "page": "basket", "product": "product-3" }
  { "timestamp": "2019-01-01 14:10:00", "customer": "customer-3", "page": "product", "product": "product-4" }
  { "timestamp": "2019-01-01 14:16:00", "customer": "customer-3", "page": "product", "product": "product-5" }
  { "timestamp": "2019-01-01 14:20:00", "customer": "customer-3", "page": "basket", "product": "product-4" }
  { "timestamp": "2019-01-01 14:21:00", "customer": "customer-3", "page": "checkout" }

O arquivo output/abandoned-carts.json deve conter apenas 1 abandono de carrinho:

  { "timestamp": "2019-01-01 13:02:00", "customer": "customer-2", "product": "product-2" }

# Premissas

1. Assumi que após 10 minutos a cesta é limpa
2. Assumi também que não é possível continuar a compra e ir para a página de checkout direto nem a página de cesta

# Pré requisitos

1. Python
2. Apache Airflow
3. o DAG foi desenvolvido urilizando o Apache Airflow com o banco PostgreSQL, mas deve funcionar sem problemas se utilizado com o SQLite, já que não utiliza paralelismo 

# instalação:
1. O arquivo dag_car_abandon.py deve ser movido para o diretório de DAGs do airflow, esse diretório é apontado pela variável dags_folder do arquivo airflow.cfg que fica no diretório de instalação do airflow, normalmente, ~/airflow
2. Devem ser criados os diretórios:
    - ~Documents/teste-b2w
    - ~Documents/teste-b2w/input
    - ~Documents/teste-b2w/work
    - ~Documents/teste-b2w/output
    - ~Documents/teste-b2w/done

# Funcionamento
- O arquivo page-views.json deverá ser colocado no diretório ~Documents/teste-b2w/input
- durante o processamento será movido para ~Documents/teste-b2w/work e após para ~Documents/teste-b2w/done
- o arquivo abandoned-carts.json será gerado no diretório ~Documents/teste-b2w/output com os carrinhos abandonados
- no airflow habilitar a dag_carrinhos_abandonados
