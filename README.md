# transversal-project-sensors
Repository dédié au développement IOT du Projet Transversal

## Protocole de communication 

Pour communiquer via radio entre les deux cartes micro:bit de notre architecture, nous passons par une communication via un protocole fait maison composé comme suit :

Sachant que nous sommes limités à un envoie de 232 bits (29 caractères) par communication radio avec micro:bit (En utilisant un encodage UTF8 de radio.send()), nous avons mis en place un protocolede communication présenté comme suit :

**Source (id du *sensor*) :** 2 caractères
Id du sensor qui récupère les données depuis le Simulator Web Server et les envoie par radio.

**Destination (id de la *gateway*) :** 2 caractères
Id de la gateway qui récupère les données par radio et envoie les données par UART à Emergency Web Server.

**Communication ID :** 2 caractères 
Id de la communication en cours. Permet ainsi à la gateway de recevoir plusieurs communications radio venant de différents sensors.
(Allant de 00 à 99)

**Packet ID :** 2 caractères
Id du paquet de la communication. Cela permet ainsi de reconstruire le message.

**Flag (état de la communication) :** 3 caractères

Label de l'état de la communication indiqué dans le paquet.

SYN -> Synchronisation : Demande de connexion
ACK -> Acknowledge : Accusé de réception
FIN -> Final : fin de la communication
PSH -> Push : Envoie de données
RST -> Reset : Réinitialisation de la connexion

Il nous reste donc 18 caractères pour les données (data).

Le protocole d'envoi des données est défini comme tel :
- Un premier caractère 'X' définissant le type d'incident suivi d'un caractère de séparation '/'.
- Les coordonnées 'x' et 'y' ainsi que 'i' l'intensité de l'incident (de 0 à 9).
- Un caractère de séparation '/' entre les propriétés de l'incident.
- Un caractère de séparation '&' entre les liste d'incidents.

> Exemple de data : `F/1,1,1&I/4,4,4/6,6,6`

Ainsi ici nous avons les données de 2 listes d'incidents :
F pour les feux : 1 feu à la case 1x1 d'une intensité de 1.
I pour les innodations : 1 innondation à la case 4x4 d'une intensité de 4, 1 innondation à la case 6x6 d'une intensité 6

> Exemple de message : `01980101PSHF/1,1,1&I/4,4,4/6,6,6`

**Récapitulatif :**

| Field    | Source | Destination | Communication ID  | Packet ID  | Flag | Data |
|:---------|-------:|------------:|------------------:|-----------:|-----:|-----:|
| Nb bytes |      2 |           2 |                 2 |          2 |    3 |   18 |

