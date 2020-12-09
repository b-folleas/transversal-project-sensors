# transversal-project-sensors
Repository dédié au développement IOT du Projet Transversal

## Protocole de communication 

Pour communiquer via radio entre les deux cartes micro:bit de notre architecture, nous passons par une communication via un protocole fait maison composé comme suit :

Sachant que nous sommes limités à un envoie de 232 bits (29 caractères) par communication radio avec micro:bit (En utilisant un encodage UTF8 de radio.send()), nous avons mis en place un protocolede communication présenté comme suit :

Source (id du *sensor*) : 2 caractères

Id du packet : 2 caractères

Flag (état de la communication) : 3 caractères

SYN -> Synchronisation : Demande de connexion
ACK -> Acknowledge : Accusé de réception
FIN -> Final : fin de la communication
PSH -> Push : Envoie de données
RST -> Reset : Réinitialisation de la connexion

Il nous reste donc 22 caractères pour les données.

| Field    | Source | Destination | Communication ID | Packet ID | Flag | Data |
|:---------|-------:|------------:|-----------------:|----------:|-----:|-----:|
| Nb bytes |      2 |           2 |                2 |         2 |    3 |   18 |
