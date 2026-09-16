# 16/09/2026

## Processamento do dataset CORD

Foi realizado o primeiro processamento do protótipo utilizando o **dataset CORD**, com execução do pipeline de OCR e extração dos campos definidos para o projeto.

### Resultado

A taxa média de acerto na extração de valores monetários foi de **0,0%**. Esse resultado já era esperado, principalmente devido às diferenças nos padrões de escrita e formatação de valores monetários presentes nos documentos do dataset. Essas variações dificultam a correspondência direta entre os valores identificados pelo OCR e os valores de referência utilizados no cálculo da métrica.

Apesar da taxa de acerto registrada pela métrica, o processamento demonstrou que o OCR foi capaz de identificar valores monetários em diversas imagens. Entre os valores extraídos estão **“52,81”, “25,15”, “580,96”, “92,00”, “334,00”, “350,00”, “59,00”, “190,00”, “302,01” e “250,10”**, entre outros.

Também foram observados diferentes comportamentos durante o processamento. Em alguns documentos, o OCR não identificou nenhum bloco de texto ou o parser não encontrou valores para extração. Em outros, foram identificados diversos blocos de texto e valores monetários.

No pré-processamento das imagens, também houve variações na detecção da perspectiva dos documentos. Em alguns casos, foi identificado um contorno com quatro vértices e aplicada a transformação de perspectiva. Em outros, não foi possível localizar o contorno do documento, fazendo com que o processamento prosseguisse utilizando a imagem original.

Dessa forma, o resultado de **0,0% não significa necessariamente que o OCR não tenha reconhecido valores monetários**. A métrica utilizada depende da correspondência entre os valores extraídos e os valores esperados. Como os documentos apresentam diferentes padrões de representação monetária, é possível que o sistema identifique corretamente um valor, mas que sua representação não corresponda exatamente ao formato utilizado como referência na avaliação.

## Testes locais

Enquanto o processamento do dataset era executado no notebook, também foram realizados **testes locais da aplicação** para verificar o funcionamento dos métodos implementados.

A partir dos resultados observados nesses testes, serão realizados alguns ajustes em determinados métodos, com o objetivo de melhorar a execução e o comportamento geral dos testes.

Após a realização desses ajustes, será executado **um novo processamento utilizando o dataset CORD**, permitindo comparar os resultados e verificar se as alterações produziram melhorias na extração e na avaliação dos dados.
