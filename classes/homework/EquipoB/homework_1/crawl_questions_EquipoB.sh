#!/bin/bash
curl https://worldbuilding.stackexchange.com/ | grep -oE '\"s-link\"[^\"]+' > archivo_temp 

echo "Número de preguntas: "
read n_pages
echo $n_pages 

for page in $(seq $n_pages)
do
   sed -n ${page}'p' archivo_temp
   #p=print, siempre se usa con -n
done
