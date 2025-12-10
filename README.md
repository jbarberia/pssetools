Este conjunto de funcionalidades permiten hacer un estudio eléctrico.
Ver la carpeta example para ver un ejemplo de uso.

Los datos minimos son:

- sav (casos del psse)
- sub (para resolver casos estaticos)
- mon (para resolver casos estaticos)
- con (para resolver casos estaticos)
- dyr, lib y dll (para simulaciones dinamicas)
- py  (para controlar la simulacion dinamica)

El flujo de trabajo sería el siguiente, para preparar los casos:

1.  Se arman los casos bases *.sav
1.  Se definen los sub, mon y con para las simulaciones estaticas
1.  Se crea el snapshot y se compila los modelos
1.  Se cargan los canales sobre el snapshot creado (este paso es manual - pero se puede guardar un idv)
1.  Se realizan las simulaciones necesarias

