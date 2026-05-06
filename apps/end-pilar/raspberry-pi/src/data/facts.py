facts = [
    "Tijdens zijn wereldrecord op de 100 meter sprint van 9,58 seconden in 2009 bereikte Usain Bolt een topsnelheid van 44,72 km/u (27,78 mph).",
    "Het wereldrecord op de 100 meter van 10,49 seconden van Florence Griffith-Joyner, gevestigd in 1988, is nog steeds ongeslagen en sneller dan de winnende tijden bij de mannen in de eerste vijf moderne Olympische Spelen.",
    "Eliud Kipchoge is de eerste persoon in de geschiedenis die een marathon onder de twee uur liep (1:59:40) in een gecontroleerde omgeving, hoewel zijn officiële Olympische record 2:08:38 is.",
    "Wayde van Niekerk verbrak het wereldrecord op de 400 meter vanuit baan 8 in Rio 2016, een prestatie die zelden wordt geleverd omdat lopers hun concurrenten achter zich niet kunnen zien.",
    "In de 400 meter horden in Tokio 2020 verpulverde Karsten Warholm zijn eigen wereldrecord met 0,76 seconden door te finishen in 45,94 seconden — een tijd die competitief zou zijn geweest op de vlakke 400 meter.",
    "In 1968 was de verspringprestatie van Bob Beamon van 8,90 meter zo ver dat het optische meetinstrument niet lang genoeg was; officials moesten een handmatig meetlint gebruiken.",
    "Faith Kipyegon is de eerste vrouw die drie opeenvolgende Olympische gouden medailles won op de 1500 meter (Rio 2016, Tokio 2020, Parijs 2024).",
    "Tijdens de Olympische Spelen van 1912 won Jim Thorpe de tienkamp en de vijfkamp terwijl hij twee verschillende schoenen droeg die hij in een vuilnisbak vond nadat de zijne waren gestolen.",
    "Abebe Bikila won de Olympische marathon van 1960 in Rome terwijl hij volledig op blote voeten liep, waarmee hij destijds een nieuw wereldrecord vestigde.",
    "Onder immense druk in Sydney 2000 liep Cathy Freeman de 400 meter in een op maat gemaakt 'swift suit' om goud te winnen in een tijd van 49,11 seconden.",
    "Met 11 Olympische medailles is Allyson Felix de meest gedecoreerde Amerikaanse atleet in de geschiedenis van de baanatletiek, waarmee ze Carl Lewis voorbijstreeft.",
    "Tijdens zijn wereldrecordprestatie op de tienkamp was het puntentotaal van Ashton Eaton zo hoog dat dit vertaald kon worden naar topprestaties in tien verschillende disciplines over slechts twee dagen.",
    "Sydney McLaughlin-Levrone heeft het wereldrecord op de 400 meter horden zes keer verbroken, waarbij ze het onlangs tijdens de Spelen van Parijs 2024 verlaagde naar 50,37 seconden.",
    "Tijdens de Spelen van München in 1972 behaalde Valeriy Borzov de zeldzame 'sprint-dubbel' door goud te winnen op zowel de 100 meter als de 200 meter.",
    "Merlene Ottey, bekend als de 'Queen of the Track', nam deel aan zeven verschillende Olympische Spelen en heeft negen medailles op haar naam staan.",
    "Op de Olympische Spelen van 1924 in Parijs won Paavo Nurmi de gouden medailles op de 1500 meter en de 5000 meter met slechts 55 minuten tussentijd.",
    "In Parijs 2024 vestigde Armand 'Mondo' Duplantis een nieuw wereldrecord van 6,25 meter bij het polsstokhoogspringen, nadat hij het goud al had veiliggesteld bij eerdere sprongen.",
    "Het wereldrecord hoogspringen van Javier Sotomayor van 2,45 meter (gevestigd in 1993) betekent dat hij effectief over de hoogte van de lat van een standaard voetbaldoel sprong.",
    "Het wereldrecord op de 400 meter van Marita Koch van 47,60 seconden staat al sinds 1985; geen enkele Olympische atleet in de 21e eeuw heeft tot nu toe sneller gelopen.",
    "In de 100 meter finale van Parijs 2024 won Noah Lyles goud met een marge van slechts 0,005 seconden op Kishane Thompson."
]

class Facts:
    @staticmethod
    def get_random_fact():
        import random
        return random.choice(facts)