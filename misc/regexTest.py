import re


testStrings = [
    r"@CROMN'ICHEL@ #s. n.# Aliaj care conține 10-20\% crom, 60-70\% nichel, restul fier, folosit la construcția rezistențelor bobinate care lucrează la temperaturi înalte. - Din #germ.# @Chromnickel.@",
    r"@AZOTOBACT'ER@ #subst.# #v.# @azotobacterie.@▶azobacterie→azotobacterie◀",
    r"@ACĂT'ĂREA@ #adj.# #invar.# #v.# @acătării.@",
    r"@AL'EM@ #s. n.# Steag cu însemnele Imperiului Otoman▶otoman→Otoman◀ (primit de domnii români la învestitura lor). - Din #tc.# @alem.@",
    r"@ABIT'AȚIE@ #s. f.# (#Jur.#) Drept de folosință a unei case de locuit care este proprietatea altuia. - Din #fr.# [droit d\']@habitation.@",
    r"@ANGROS'IST, -Ă,@ $angrosiști, -ste,$ #s. m.# și #f.#, #adj.# (Persoană, întreprindere) care face comerț angro. - @Angro@ + #suf.# $-##ist.##$",
    r"@NESCAF'E^{®},@ (@2@) $nescafeuri,$ #s. n.# @1.@ Denumire comercială dată unui praf de cafea solubil, din care se prepară o băutură prin simpla dizolvare în apă; nes. @2.@ Sortiment sau porție de nescafe (@1@). - #Cuv.# #fr.#",
    r"@AC'EL^2, ACE'A@ #pron. dem.# #v.# @acela^1.@",
    r"@ALCH'ENĂ,@ $alchene,$ #s. f.# Nume dat unor hidrocarburi aciclice nesaturate. - Din #fr.# @alkène,@ #germ.# @Alkene.@{{E vorba de hidrocarburi care conțin o singură legătură nesaturată - de tipul -CH=CH- - și care au formula generală C_{n}H_{2n} cu n>1. (comentariu preluat din definiția cu sursa DEX \'98)/212}}",
    r"@ACIDIT'ATE@ #s. f.# Grad de concentrație de ioni de hidrogen sau cantitatea totală de acid dintr-o soluție. ** Proprietatea de a fi acid. * $Aciditate gastrică$ = gradul de aciditate a sucului gastric, conferit de prezența acidului clorhidric, clorului, pepsinei și acidului lactic. - Din #fr.# @acidité,@ #lat.# @aciditas, -atis.@",
    r"@TOM'ISM@ #s. n.# Doctrină filosofică și teologică a lui Toma d\'Aquino și a continuatorilor săi. - Din #fr.# @thomisme.@",
    r"@SFECL'I,@ $sfeclesc,$ #vb.# IV. #Tranz.# (în #expr.#) $A o sfecli$ = a ajunge într-o situație neplăcută, a o păți; a o băga pe mânecă. - #Cf.# %sfeclă.%",
    r"@SF'ECLĂ,@ $sfecle,$ #s. f.# Specie de plante erbacee cu frunze lucioase și cu rădăcina cărnoasă de culoare albă sau roșie, folosită ca aliment, ca plantă furajeră sau în industrie, pentru extragerea zahărului; nap $(Beta).$ * $Sfeclă de zahăr$ = plantă cu rădăcină cilindrică sau conică alungită și frunze mari, oval-alungite cu uri conținut de 14-22\% zahăr și utilizată în industria zahărului și a alcoolului $(Beta vulgaris-saccharifera). Sfeclă furajeră$ = plantă cu rădăcină voluminoasă ovală, cilindrică sau sferică, cu un conținut de 4-5\% zahăr, cultivată pentru hrana animalelor $(Beta vulgaris).$ - Din #sl.# @sveklŭ.@"
]

ReplacementsRegexDict = {
    r' - ': ' – ',  # U+2013
    r' \*\* ': ' ♦ ', # U+2666
    r' \* ': ' ◊ ',  # U+25CA
    r'\\\'': '’',   # U+2019
    r'<': '&lt;',
    r'>': '&gt;',
    r'▶(.*?)◀': '',
    r'(?<!\\)"([^"]*)"': '„\\1”',
    r'(?<!\\)##(.*?)(?<!\\)##': '<span class="abr">\\1</span>',
    r'(?<!\\)#(.*?)(?<!\\)#': '<span class="abr">\\1</span>',
    r'(?<!\\)\{{2}(.*?)(?<![+])\}{2}': ' [Notă: \\1]',
    r'(?<!\\)%(.*?)(?<!\\)%': '<span class="eti">\\1</span>',
    r'(?<!\\)@(.*?)(?<!\\)@': '<b>\\1</b>',
    r'(?<!\\)\$(.*?)(?<!\\)\$': '<i>\\1</i>',
    r'(?<!\\)\^(\d)': '<sup>\\1</sup>',
    r'(?<!\\)\^\{([^}]*)\}': '<sup>\\1</sup>',
    r'(?<!\\)_(\d)': '<sub>\\1</sub>',
    r'(?<!\\)_\{([^}]*)\}': '<sub>\\1</sub>',
    r'(?<!\\)\'([a-zA-ZáàäåăắâấÁÀÄÅĂẮÂẤçÇéèêÉÈÊíîî́ÍÎÎ́óöÓÖșȘțȚúüÚÜýÝ])': '<span class="und">\\1</span>',
    r'\\%': '%',
    r'\\$': '$',
}

def formatDefinition(definition):
    result = definition

    for key in ReplacementsRegexDict:
        result = re.sub(key, ReplacementsRegexDict[key], result)

    return result

for definition in testStrings:
    print(formatDefinition(definition))
    print("<hr>")
