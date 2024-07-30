Script para extraer informacion de las imagenes de actas a traves de su codigo QR.

Para correr, si tienes go:
```
go run main.go
```

Sino:
```
# instala devbox
curl -fsSL https://get.jetify.com/devbox | bash

devbox shell
go run main.go
```

Corriendo el script en mi laptop, el script extrajo informacion de 2mil actas, de un total de ~6mil, y
tomó 16 minutos.

Creo que si se corre con las imagenes no comprimidas de las actas, debe poder extraer mas informacion.
O sino, podemos intentar con alguna otra libreria de codigos QR.