Infra:
    - Accessrättigheter
        - Manager <-> slave, spärra portar på ip
        - Registry endast access från vissa ip (slave, manager, lokalt)
        - Admin bara access från vitlistade ip
        - Flytta ssh port på båda servrar
    - Root
        - Kör docker som egen användare
        - Tillåt inte root inlogg
    - Backup
        - Kolla hur man kan ta backup av db, conf etc varje dag
    - Övervakning
        - Internt med grafana etc?
        - Externt så jag får varningar om den är nere
    - Omstart?
        - Hur funkar det? Hur hanterar man det? Testa!
    - Hur vet man att de sprider ut sig mellan noder?


Testa reboota och se om allt finns kvar

https://webbkoll.dataskydd.net
https://www.nginx.com/blog/http-strict-transport-security-hsts-and-nginx/
https://matomo.org/

