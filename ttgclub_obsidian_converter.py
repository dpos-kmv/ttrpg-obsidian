import requests
import jinja2
import bs4
from re import sub
from pathlib import Path

url='https://ttg.club'
jinjaTemplateDir = '/Users/kmv/workdir/kmv/DND_TTG/obsidian_ttg_converter/'

bad_chars = [';', ':', '!', "*", "/"]

def kebab(s):
  return '-'.join(
    sub(r"(\s|_|-)+"," ",
    sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
    lambda mo: ' ' + mo.group(0).lower(), s)).split())


def diceFormulaChange(description: str):
    diceFormulaReplace = { 'к': 'd', '×': '*' }
    BS = bs4.BeautifulSoup(description)
    diceFormulaOld = BS.find_all('dice-roller')
    for dice in diceFormulaOld:
        diceFormula = str(dice.get_text())
        for i, j in diceFormulaReplace.items():
          diceFormula = diceFormula.replace(i, j)
        diceFormulaNew = '`dice: '+ diceFormula + '|render`'
        description = str(description).replace(str(diceFormulaOld[0]), str(diceFormulaNew))
        htmlTagsDescription = bs4.BeautifulSoup(description)
        description = htmlTagsDescription.get_text()
        return description


def convertMagicItems(): 
    api_magicItems='/api/v1/items/magic'
    magicItemsList=requests.post(url+api_magicItems, json={ "page": 0 })
    jsonData = magicItemsList.json()
    magicItemsUrls = []
    
    for item in jsonData: (
            magicItemsUrls.append("/api/v1" + item['url'])
            )
    
    Path("").mkdir(parents=True, exist_ok=True)
    
    for magicItemurl in magicItemsUrls:
        magicItemInfo = requests.post(url+magicItemurl).json()
        #print(magicItemInfo)
    
        magicItem = magicItemInfo['name']['rus']
        source = magicItemInfo['source']['shortName']
        magicItemType = magicItemInfo['type']['name']
        magicItemRarity = magicItemInfo['rarity']['name']
        #magicItemCost = magicItemInfo['cost']['dmg']
        magicItemDescription = magicItemInfo['description']
        #magicItemDescription =  diceFormulaChange(magicItemInfo['description'])
   
        

        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(jinjaTemplateDir))
        template = environment.get_template("magic_items_template.j2")
    
        filename = f"MagicItems/{str(magicItem).replace('/', ' ')}.md" 
        content = template.render(
                magicItem = magicItem,
                magicItemType = magicItemType,
                magicItemRarity = magicItemRarity,
                #magicItemCost = magicItemCost,
                magicItemDescription = magicItemDescription
                )
    
        with open(filename, mode="w", encoding="utf-8") as message:
                message.write(content)
                print(f"... wrote {filename}")
    


def convertSpells():
    api_spell='/api/v1/spells'
    #print(url+api_spell)
    spellList=requests.post(url+api_spell, json={ "page": 0 })
    jsonData = spellList.json()
    spellUrls = []
    for item in jsonData: (
            spellUrls.append("/api/v1" + item['url'])
            )
    #print(spellUrls[0])
    
    componentMapping = {
            "s": "[[Spellcasting#СОМАТИЧЕСКИЙ (С)|С]]", 
            "m": "[[Spellcasting#МАТЕРИАЛЬНЫЙ (М)|М]]", 
            "v": "[[Spellcasting#ВЕРБАЛЬНЫЙ (В)|В]]"
            }
    
    
    for spellUrl in spellUrls:
        spellComponents = []
        spellClasses = []
        spellInfo = requests.post(url+spellUrl).json()
        for component in spellInfo['components']:
            spellComponents.append(componentMapping[component])
        try:
            spellMaterialComponents = spellInfo['components']['m']
        except:
            spellMaterialComponents = ''
        spell = spellInfo['name']['rus']
        spellEng = spellInfo['name']['eng']
        spellEngKebab = kebab(spellEng)
        spellLevel = spellInfo['level']
        spellSchool = spellInfo['school']
        spellCastingTime = spellInfo['time']
        spellRange = spellInfo['range']
        spellDuration = spellInfo['duration']
        for personClass in spellInfo['classes']:
            spellClasses.append(personClass['name'])
        source = spellInfo['source']['shortName']
        spellDescription = diceFormulaChange(spellInfo['description'])
    
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(jinjaTemplateDir))
        template = environment.get_template("spells_template.j2")

        filename = f"Spells/{str(spell).replace('/', ' ')}.md"
    
        content = template.render(
                spell=spell,
                spellEng=spellEng,
                spellEngKebab=spellEngKebab,
                spellLevel=spellLevel,
                spellSchool=spellSchool,
                spellCastingTime=spellCastingTime,
                spellRange=spellRange,
                spellComponents=spellComponents,
                spellMaterialComponents=spellMaterialComponents,
                spellDuration=spellDuration,
                spellClasses=spellClasses,
                source=source,
                spellDescription=spellDescription
                )
        
        with open(filename, mode="w", encoding="utf-8") as message:
                message.write(content)
                print(f"... wrote {filename}")



convertMagicItems()
convertSpells()
