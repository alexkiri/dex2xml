import re


testStrings = [
    "@CROMNÍCHEL@ #s. n.# Aliaj care conține 10-20\% crom, 60-70\% nichel, restul fier, folosit la construcția rezistențelor bobinate care lucrează la temperaturi înalte. - Din #germ.# @Chromnickel.@", 
    "@AZOTOBACTÉR@ #subst.# #v.# @azotobacterie.@▶azobacterie→azotobacterie◀", 
    "@ACĂT'ĂREA@ #adj.# #invar.# #v.# @acătării.@", 
    "@ALÉM@ #s. n.# Steag cu însemnele Imperiului Otoman▶otoman→Otoman◀ (primit de domnii români la învestitura lor). - Din #tc.# @alem.@", 
    "@ABITÁȚIE@ #s. f.# (#Jur.#) Drept de folosință a unei case de locuit care este proprietatea altuia. - Din #fr.# [droit d\']@habitation.@", 
    "@ANGROSÍST, -Ă,@ $angrosiști, -ste,$ #s. m.# și #f.#, #adj.# (Persoană, întreprindere) care face comerț angro. - @Angro@ + #suf.# $-##ist.##$", 
    "@NESCAFÉ^{®},@ (@2@) $nescafeuri,$ #s. n.# @1.@ Denumire comercială dată unui praf de cafea solubil, din care se prepară o băutură prin simpla dizolvare în apă; nes. @2.@ Sortiment sau porție de nescafe (@1@). - #Cuv.# #fr.#, <b>NESCAFÉ<sup>®</sup>,</b> (<b>2</b>) <i>nescafeuri,</i> s. n. <b>1.</b> Denumire comercială dată unui praf de cafea solubil, din care se prepară o băutură prin simpla dizolvare în apă; nes. <b>2.</b> Sortiment sau porție de nescafe (<b>1</b>). – Cuv. fr.", 
    "@ACÉL^2, ACEÁ@ #pron. dem.# #v.# @acela^1.@	<b>ACÉL<sup>2</sup>, ACEÁ</b> pron. dem. v. <b>acela<sup>1</sup>.</b>", 
    "@GUANÍNĂ,@ $guaníne,$ s. f. Purină ($C_5H_5N_5O$) care codează informația genetică în lanțul de polinucleotide al acidului dezoxiribonucleic sau al acidului ribonucleic. Cf. $adenină, citozină, timină$ și $uracil.$ (terminolog. științif., din $guano$ (unde se întâlnește cu precădere) + suf. $-ină$ (cf. $citozină$); cf. engl., fr. $guanine$) [$MW, TLF$]", 
    "@ACIDITÁTE@ #s. f.# Grad de concentrație de ioni de hidrogen sau cantitatea totală de acid dintr-o soluție. ** Proprietatea de a fi acid. * $Aciditate gastrică$ = gradul de aciditate a sucului gastric, conferit de prezența acidului clorhidric, clorului, pepsinei și acidului lactic. - Din #fr.# @acidité,@ #lat.# @aciditas, -atis.@	<b>ACIDITÁTE</b> s. f. Grad de concentrație de ioni de hidrogen sau cantitatea totală de acid dintr-o soluție. ♦ Proprietatea de a fi acid. ◊ <i>Aciditate gastrică</i> = gradul de aciditate a sucului gastric, conferit de prezența acidului clorhidric, clorului, pepsinei și acidului lactic. – Din fr. <b>acidité,</b> lat. <b>aciditas, -atis.</b>", 
    "@TOMÍSM@ #s. n.# Doctrină filosofică și teologică a lui Toma d\'Aquino și a continuatorilor săi. - Din #fr.# @thomisme.@", 
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
