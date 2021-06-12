import os
import shutil
import vagrant
import netmiko

# Optiemenu
print("############################################################")
print("1. Server registreren")
print("2. Vagrant box beheer")
print("3. Remote execution van commando's/scripts op server")
print("4. Monitoring van remote hosts")
print("5. Predefined architecture opzetten in Vagrant")
print("6. Exit")
print("############################################################")
# keuze registreren
option = input("Kies optie 1/2/3/4/5/6: ")
print("############################################################")


# controleren of er al reeds een serversconfig.txt bestand bestaat
def checkfile():
    check = open('serversconfig.txt', 'a')
    check.close()
    check = open('vagrantboxesconfig.txt', 'a')
    check.close()


# Registreerd een server dat opgegeven wordt door de user in een bestand genaamd serversconfig.txt
# leest het bestand in, controleerd als de naam of het ip adres in het bestand staan
# indien de naam of het ip adres niet in het bestand staat, komt er een nieuwe entry in het bestand in formaat "naam,ip"
# indien de naam of het ip adres wel in het bestand staat, komt er een foutmelding en wordt het programma afgesloten
def serv_reg():
    print("U heeft de optie 'Server registreren' gekozen")
    naam = input("Geef de naam op van de te registreren server: ")
    ip = input("Geef het ip adres op van de te registreren server: ")
    lezen = open('serversconfig.txt')
    allservers = lezen.read()
    lezen.close()
    if ip in allservers or naam in allservers:
        print("De server of het ip adres zit al in het config bestand")
        print("############################################################")
        exit()
    else:
        a = open('serversconfig.txt', 'a')
        a.write(naam + "," + ip + ",")
        a.close()
        print("De server: "+naam+" is geregistreerd in het config bestand")
        print("############################################################")
        exit()


# Keuze tussen vagrantbox aanmaken/beheren of exit
def vagr_box():
    # optiemenu
    print("U heeft de optie 'Vragrant box beheer' gekozen")
    print("--------------------------")
    print("1. Vagrantbox aanmaken")
    print("2. Vagrantbox beheren")
    print("3. Exit")
    print("--------------------------")
    optie = input("Kies optie 1/2/3: ")
    print("--------------------------")

    def vagr_box_create():
        print("U heeft de optie 'Vagrantbox aanmaken' gekozen")
        # locatie kiezen
        loc = input("Waar wilt u de vagrantbox opslaan: ")
        ip = input("Geef het gewenste ip adres op: ")
        username = input("Geef uw gewenste username op: ")
        password = input("Geef uw gewenste wachtwoord op: ")
        # controle naam en ip in vagrantboxes.txt
        lezen = open('vagrantboxesconfig.txt')
        allservers = lezen.read()
        lezen.close()
        if ip in allservers or loc in allservers:
            print("Er bestaat al een vagrantfile met deze directory of met dit ip-adres")
            print("############################################################")
            exit()
        else:
            sch = open('vagrantboxesconfig.txt', 'a')
            sch.write(loc+","+ip+","+username+","+password+",")
            sch.close()
        # huidige directory ophalen, hieraan "/" toevoegen, hierdoor moet de gebruiker dit niet meer doen
        parent_dir = os.getcwd() + "/"
        path = os.path.join(parent_dir, loc)
        # directory wordt aangemaakt
        os.mkdir(path)
        # Creëren vagrantfile in opgegeven directory
        vf = open(path + "/VagrantFile", "a")
        vf.write('Vagrant.configure("2") do |config|\n')
        vf.write('\tconfig.vm.box = "hashicorp/bionic64"\n')
        vf.write('\tconfig.vm.provider "virtualbox" do |vb|\n')
        # type netwerk en ip opvragen aan gebruiker, instellingen toepassen in vagrantfile
        tnet = input("Wilt u een 'private' of 'public' netwerk: ")
        # ip adres toevoegen aan vagrantfile
        vf.write('\tconfig.vm.network "' + tnet + '_network", ip: "' + ip + '"\n')
        # username toevoegen ssh
        vf.write('\tconfig.ssh.username = "'+username+'"\n')
        # password toevoegen ssh
        vf.write('\tconfig.ssh.password = "'+password+'"\n')
        # hostname opvragen aan gebruiker, instelling toepassen in vagrantfile
        hostname = input("Geef de gewenste hostname op: ")
        vf.write('\tconfig.vm.hostname = "' + hostname + '"\n')
        # cpu cores opvragen en hoeveelheid ram opvragen, instellingen toepassen in vagrantfile
        atlcpu = input("Geef het gewenste aantal CPUs op: ")
        vf.write('\tvb.cpus = ' + atlcpu + '\n')
        atlram = input("Geef de gewenste hoeveelheid ram op in MB: ")
        vf.write('\tvb.memory = ' + atlram + '\n')
        # Kijken of er aan portwarding gedaan wilt worden
        pfcheck = input("Wilt u aan portforwarding doen Y/N: ")

        while pfcheck == "Y" or pfcheck == "y":
            pfg = input("Geef de te portforwarden poort op: ")
            pfh = input("Geef de poort naar waar te portforwarden op: ")
            vf.write('\tconfig.vm.network :forwarded_port, guest: ' + pfg + ', host: ' + pfh + '\n')
            pfcheck = input("Wilt u nog een port forwarden Y/N: ")

        # Kijken of er provisions moeten geinstalleerd moeten worden
        provcheck = input("Wilt u aan provisioning doen Y/N: ")
        while provcheck == "Y" or provcheck == "y":
            # path van shell script opvragen, shell script kopiëren en in vagrantfile steken
            provscript = input("Geef de locatie op van het shell script: ")
            shutil.copyfile(provscript, path)
            # naam van het script uit het opgegeven pad halen
            scriptname = os.path.basename(os.path.normpath(provscript))
            vf.write('\tconfig.vm.provision :shell, path: "' + scriptname + '"\n')
            provcheck = input("Wilt u nog aan provisioning doen Y/N: ")

        # 2 end statements onderaan schrijven en het bestand sluiten
        vf.write("end\nend")
        vf.close()

        print("############################################################")

    def vagr_box_manage():
        print("U heeft de optie 'Vagrantbox beheren' gekozen")
        print("--------------------------")
        print("U heeft de volgende vagrantboxes:")
        # toont alle boxes met hun ip in vagrantboxesconfig.txt
        boxes = open("vagrantboxesconfig.txt", 'r').read().split(",")
        i = 0
        while i < len(boxes):
            print(boxes[i])
            i = i+4

        # optiemenu
        print("--------------------------")
        print("1. Start box: ")
        print("2. Halt box: ")
        print("3. Suspend box: ")
        print("4. Destroy box: ")
        print("5. Exit")
        print("--------------------------")
        # keuze optiemenu
        optie = input("Kies optie 1/2/3/4/5: ")
        print("--------------------------")

        # starten van vagrant box
        def start_box():
            print("U heeft de optie 'Start box' gekozen")
            print("--------------------------")
            # check
            check = "y"
            while check == "y" or check == "Y":
                # box vragen om op te starten
                box = input("Geef de te op te starten box op: ")
                # naar directory van box gaan die opgestart moet worden
                os.chdir(box)
                # met python-vagrant de box opstarten
                v = vagrant.Vagrant()
                v.halt()
                # aantonen dat de box is opgestart
                print("De volgende Vagrant box is nu opgestart: " + box)
                # terug naar de algemene directory gaan, belangrijk indien er nog een box opgestart moet worden
                os.chdir("..")
                # vragen of er nog een box opgestart moet worden, indien y of Y herhalen while cyclus
                check = input("Wilt u nog een box opstarten Y/N: ")

        # halten van vagrant box
        def halt_box():
            print("U heeft de optie 'Halt box' gekozen")
            print("--------------------------")
            check = "y"
            while check == "y" or check == "Y":
                box = input("Geef de te halten box op: ")
                os.chdir(box)
                v = vagrant.Vagrant()
                v.halt()
                print("De volgende Vagrant box is nu gehalt: " + box)
                os.chdir("..")
                check = input("Wilt u nog een box halten Y/N: ")

        # suspenden van vagrant box
        def suspend_box():
            print("U heeft de optie 'Suspend box' gekozen")
            print("--------------------------")
            check = "y"
            while check == "y" or check == "Y":
                box = input("Geef de te suspenden box op: ")
                os.chdir(box)
                v = vagrant.Vagrant()
                v.suspend()
                print("De volgende Vagrant box is nu suspended: " + box)
                os.chdir("..")
                check = input("Wilt u nog een box suspenden Y/N: ")

        # destroyen van vagrant box
        def destroy_box():
            print("U heeft de optie 'Destroy box' gekozen")
            print("--------------------------")
            check = "y"
            # check variabele om meerde boxen in 1 sessie te kunnen destroyen
            while check == "y" or check == "Y":
                # te destroyen box opvragen
                box = input("Geef de te destroyen box op: ")
                # veranderen naar dir van box
                os.chdir(box)
                # box destroyen
                v = vagrant.Vagrant()
                v.destroy()
                print("De volgende Vagrant box is nu destroyed: " + box)
                # terug naar main directory gaan
                os.chdir("..")
                # box verwijderen uit config bestand
                b = open('vagrantboxesconfig.txt')
                # alles inlezen
                vagbox = b.read()
                b.close()
                # separeren en in array
                vagbox = vagbox.split(",")
                x = 0
                # while lus om elementen uit box te verwijderen die te maken hebben met de opgegeven box
                while x < len(vagbox):
                    if box == vagbox[x]:
                        vagbox.pop(x+3)
                        vagbox.pop(x+2)
                        vagbox.pop(x+1)
                        vagbox.pop(x)
                        # 1 element blijft altijd over zonder waarde, met deze command dit element verwijderen
                        vagbox.remove("")
                        # config bestand overschrijven
                        save = open("vagrantboxesconfig.txt", "w")
                        # met for lus alle elementen in vagbox array terug in config bestand schrijven
                        # en separeren door ","
                        for conf in vagbox:
                            save.write(conf+",")
                        save.close()
                    x = x + 1
                    # directory van verwijderde box verwijderen
                shutil.rmtree(box, ignore_errors=True)
                # vragen of er nog een box verwijderd moet worden
                check = input("Wilt u nog een box destroyen Y/N: ")

        # keuze optiemenu met corresponderende commando, bij foute input melding en exit
        if optie == "1":
            start_box()
        elif optie == "2":
            halt_box()
        elif optie == "3":
            suspend_box()
        elif optie == "4":
            destroy_box()
        elif optie == "5":
            print("Het programma zal nu verlaten worden")
            exit()
        else:
            print("Foutieve input")
            exit()

        print("############################################################")

    # keuze optie uit optiemenu met call naar functie of exit
    if optie == "1":
        vagr_box_create()
    elif optie == "2":
        vagr_box_manage()
    elif optie == "3":
        print("Het programma zal nu verlaten worden")
        exit()
    else:
        print("Foutieve input")
        exit()


def rem_exec():
    # optie menu
    print("U heeft de optie 'Remote exececution van commando's/scripts op server' gekozen")
    print("--------------------------")
    print("1. Interactieve connectie")
    print("2. Script uitvoeren")
    print("3. Exit")
    print("--------------------------")
    optie = input("Kies optie 1/2/3: ")
    print("--------------------------")

    # opzetten interactieve connectie
    def inter_connec():
        print("U heeft de optie 'Interactieve connectie' gekozen")
        # naam server of vagrantbox opgeven
        naam = input("Geef de naam van de vagrantbox of server op: ")
        # alle vagrantbox namen ophalen
        a = open('vagrantboxesconfig.txt')
        vagname_ip = a.read()
        a.close()
        vagname_ip = vagname_ip.split(",")
        # alle server namen ophalen
        b = open('serversconfig.txt')
        srvname_ip = b.read()
        b.close()
        srvname_ip = srvname_ip.split(",")
        # 2 variabelen defineren om zometeen te itereren
        i = 0
        j = 0
        # hier komt ip adres terecht voor ssh connectie
        ipadres = ""
        # bepalen type, vagrant box of normale server
        type = ""
        password = ""
        username = ""
        # itereren over alle vagrant boxes, indien variabele naam gelijk is aan een vagrantbox, wordt het ip adres van
        # de vagrantbox opgeslagen in ip en wordt het type op vagrant gezet
        while i < len(vagname_ip):
            if naam == vagname_ip[i]:
                ipadres = vagname_ip[i+1]
                type = "vagrant"
                username = vagname_ip[i+2]
                password = vagname_ip[i + 3]
                break
            i = i+1
        # itereren over alle servers, indien variabele naam gelijk is aan een server, wordt het ip adres van de server
        # opgeslagen in ip en wordt het type op normal gezet
        while j < len(srvname_ip):
            if naam == srvname_ip[j]:
                ipadres = srvname_ip[j+1]
                type = "normal"
                break
            j = j+1
        # indien type vagrant is wordt de verbinding opgesteld met credentials van vagrantboxoesconfig.txt
        if type == "vagrant":
            os = input("Geef het operating system op: ")
            os = os.lower()
            connection = netmiko.ConnectHandler(ip=ipadres, device_type=os, username=username, password=password,
                                                secret="vagrant", port=22)
            check = "y"
            # while gebruiken om te kunnen blijven commando's sturen tot de user wilt stoppen
            while check == "y" or check == "Y":
                cmd = input("Geef een commando op: ")
                print(connection.send_command(cmd))
                check = input("Wilt u nog een commando invoeren Y/N: ")
            connection.disconnect()
            print("De verbinding met de server is nu afgesloten")
        # indien type normal is wordt de verbinding opgesteld en wordt de username en wachtwoord gevraagd
        # aan de gebruiker
        elif type == "normal":
            naam = input("Geef de SSH naam op: ")
            wachtwoord = input("Geef het wachtwoord op: ")
            os = input("Geef het operating system op: ")
            os = os.lower()
            connection = netmiko.ConnectHandler(ip=ipadres, device_type=os, username=naam,
                                                password=wachtwoord, port=22)
            check = "y"
            while check == "y" or check == "Y":
                cmd = input("Geef een commando op: ")
                print(connection.send_command(cmd))
                check = input("Wilt u nog een commando invoeren Y/N: ")
            connection.disconnect()
            print("De verbinding met de server is nu afgesloten")
        # indien de opgegeven naam niet gevonden werd in de vagrantboxes en normale server komt er een foutmelding
        else:
            print("Server: "+naam+" niet gevonden\nHet programma wordt nu verlaten")
            exit()

    def script_exe():
        print("U heeft de optie 'Script uitvoeren' gekozen")

    if optie == "1":
        inter_connec()
    elif optie == "2":
        script_exe()
    elif optie == "3":
        print("Het programma wordt nu verlaten")
        exit()
    else:
        print("Foutieve input")
        exit()

    print("############################################################")
def monitoring():
    print("U heeft de optie 'Monitoring van remote hosts' gekozen")


def setup_arch():
    print("U heeft de optie 'Predefined architecture opzetten in Vagrant' gekozen")


# optiemenu met hierin verwijzing naar commando
def optiemenu(opt):
    if option == "1":
        serv_reg()
    elif option == "2":
        vagr_box()
    elif option == "3":
        rem_exec()
    elif option == "4":
        monitoring()
    elif option == "5":
        setup_arch()
    elif option == "6":
        print("Het programma zal nu verlaten worden")
        exit()
    else:
        print("Foutieve input")
        exit()


# utivoeren controle config bestanden
checkfile()
# uitvoeren keuze optiemenu
optiemenu(option)
