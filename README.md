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

**Parity Bit :** 1 caractères

Nous utilisons un bit de parité afin de vérifier la validité de nos données. En effet, cet algorithme de checksum est le plus simple à mettre en place et est suffisant pour notre envoi de données sur les micro:bit.

Pour le calculer, on détermine le XOR de notre block data et ainsi, si l'un des bit est erroné, la gateway enverra alors un paquet *Reset*.

**Data :** 17 caractères

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

> Exemple de message : `01980101PSH0F/1,1,1&I/4,4,4/6,6,6`

**Récapitulatif :**

| Field    | Source | Destination | Communication ID  | Packet ID  | Flag | Parity Bit | Data | Total |
|:---------|-------:|------------:|------------------:|-----------:|-----:|-----------:|-----:|------:|
| Nb bytes |      2 |           2 |                 2 |          2 |    3 |          1 |   17 |    29 |
| Example  |     01 |          98 |                01 |         01 |  PSH |          0 |  ... |   ... |

## Sécurité

### Encryption

Les données sont encryptées avant d'être envoyé par radio avec un chiffrement césar. La gateway et le sensor partage la même clé privée (chiffrement symétrique) qui est hardcodé dans les deux fichiers. Il serait mieux de procéder par un échange via clé privée - clé publique pour l'envoi et le partage de la clé privé utilisé pour le chiffrement de César.

Ainsi, les données initialement lues sous forme de string sont encodés en bytes puis envoyées sous forme de bytes en représentation héxadécimale par le sensor. Elles sont alors récupérées par la gateway qui va décoder le message avec la même clé que pour l'encodage.

### Canal de communication

Les cartes micro:bit ne peuvent communiquer par messages radio que s'ils elles ont la même configuration d'adresse. Ainsi, lorsque la gateway reçoit un paquet de demande de synchronisation de la part du sensor (flag SYN) elle envoie en réponse (flag ACK) dans la partie donnée de son paquet l'adresse encryptée de communication sur laquelle la gateway et le sensor doivent se configurer pour envoyer des paquets sur un canal sécurisée.

Ainsi, si l'un utilisateur malveillant cherchait à vouloir récupérer les données envoyées par le sensor il ne pourrait pas car s'il n'a pas la clé du chiffrement césar il ne sait pas sur quelle adresse vont être envoyés les paquets.

> Les adresses envoyées par la gateay au sensor sont générés pseudo-aléatoirement à partir d'une plage d'adresses disponibles. 
