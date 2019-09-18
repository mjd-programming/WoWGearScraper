from urllib import request
from collections import namedtuple
import openpyxl
import time
import bs4
import re

gear_types = 'Plate Mail Cloth Leather Neck Finger Relic Shield Trinket hand Hand Ranged'.split()
class_types = 'Druid Hunter Mage Paladin Priest Rogue Shaman Warlock Warrior'.split()
letters = [chr(i + 65) for i in range(26)]

# setup of master url
page_id = '4.16'
url = 'https://classicdb.ch/?items=%s' % page_id
html = request.urlopen(url)
soup = bs4.BeautifulSoup(html, 'html.parser')

# find the list of gear pieces
script_list = soup.select('script[type="text/javascript"]')
gear_script = script_list[len(script_list) - 1].get_text()

# extract gear information from list
gear_regex = re.compile(r'data:\[({.*})')
gear_list = str(gear_regex.findall(gear_script)).split('},{')

# place id data into list
id_list = []
id_regex = re.compile(r'id:(\d+)')
for gear in gear_list:
    id_list.append(id_regex.search(gear).group(1))

def get_time_data(st, bt, et, times):
    overall_string = str(int(et - bt))
    individual_string = str(int(et*1000 - st*1000))
    est_string = '?'
    if len(times) > 0: est_string = int((sum(times)/len(times))*(total_items-current_id_index))
    print('Program has been running for %s seconds.\n'
          'Individual process took %s milliseconds to complete.\n'
          'Estimated time to complete: %s seconds.\n' % (overall_string, individual_string, est_string))
# TODO has the equip bonuses and the set bonuses within a single cell check
# https://stackoverflow.com/questions/15370432/writing-multi-line-strings-into-cells-using-openpyxl
# also sometimes the name appears in the set name area, I would try to fix it but after making the multi-cell thing work

def add_gear_to_spreadsheet(html, sheet, current_piece):
    gear_soup = bs4.BeautifulSoup(html, 'html.parser')
    master_text = gear_soup.select('.tooltip table tr td table tr td')
    name = ''
    gear_type = ''
    gear_slot = ''
    required_level = 0
    required_class = ''
    armor = 0
    dps = 0
    agi = 0
    strength = 0
    sta = 0
    intellect = 0
    fire = 0
    frost = 0
    nature = 0
    arcane = 0
    shadow = 0
    equips = []
    set_name = ''
    set_bonuses = []
    for content in master_text[0].contents:
        if len(content) > 0:
            if len(content) > 1:
                # binds, stats, req level
                if 'Binds' in content:
                    # gives the binding of the item, may have to change to just bind or include the word
                    # bounds so account bound items will be able to be read as well
                    pass
                elif 'Requires' in content:
                    required_level = int(re.compile(r'Requires Level (\d+)').search(content).group(1))
                elif 'Durability' in content:
                    # gives the durability, we do not want the durability
                    pass
                elif 'Class' in content:
                    pass
                else:
                    # just content to access the values
                    if ' Armor' in content:
                        armor = int(content.split(' Armor')[0])
                    elif ' damage per second' in content:
                        try: # TODO fix this section, it seems to mess up the placement of the name and stuff
                            dps = float(content.split(' damage per second')[0])
                        except:
                            pass
                    elif ' Agility' in content:
                        agi = int(content.split(' Agility')[0])
                    elif ' Strength' in content:
                        strength = int(content.split(' Strength')[0])
                    elif ' Stamina' in content:
                        sta = int(content.split(' Stamina')[0])
                    elif ' Intellect' in content:
                        intellect = int(content.split(' Intellect')[0])
                    elif ' Fire Resistance' in content:
                        fire = int(content.split(' Fire Resistance')[0])
                    elif ' Frost Resistance' in content:
                        frost = int(content.split(' Frost Resistance')[0])
                    elif ' Nature Resistance' in content:
                        nature = int(content.split(' Nature Resistance')[0])
                    elif ' Arcane Resistance' in content:
                        arcane = int(content.split(' Arcane Resistance')[0])
                    elif ' Shadow Resistance' in content:
                        shadow = int(content.split(' Shadow Resistance')[0])
            else:
                # name and slot/type
                gear_type_found = False
                for item in gear_types:
                    if item in content.text:
                        try:
                            # slot
                            # type
                            # the slot will be on the top and the type will be on the bottom
                            if str(content.text).split(item)[1] == '':
                                gear_slot = str(content.text).split(item)[0]
                                gear_type = str(content.text).split(str(content.text).split(item)[0])[1]
                            else:
                                gear_slot = str(content.text).split(item)[1]
                                gear_type = str(content.text).split(str(content.text).split(item)[1])[0]
                            gear_type_found = True
                            break
                        except:
                            # if it's alone in the row then just get the row, most likely the slot
                            gear_slot = content.text
                            gear_type_found = True
                if not gear_type_found:
                    class_found = False
                    for classes in class_types:
                        if classes in content.text:
                            # required class
                            required_class = content.text
                            class_found = True
                            break
                    if not class_found:
                        # name
                        name = content.text
    # if the item that we are looking at is a weapon then we need to change the index
    # that we are looking for the equip stats and the set bonuses
    equip_index = 2
    try:
        if master_text[2].contents[0][::-1][0] == 'e':
            equip_index = 3
    except:
        equip_index = 2
    for content in master_text[equip_index].contents:
        if len(content) > 0:
            if type(content) is bs4.element.Tag:
                if content.text[:5] == 'Equip' or content.text[:3] == 'Use' or content.text[:3] == 'Cha':
                    # equips and uses and chance on hits
                    equips.append(content.text)
                else:
                    if content.text[len(content.text)-1] == ')':
                        # set name
                        set_name = content.text[:len(content.text)-6]
                    else:
                        if content.text[0] == '(':
                            for bonus in content.text.split(': '):
                                if bonus[0] != '(':
                                    if bonus[len(bonus)-1] != '.':
                                        set_bonuses.append(bonus[:len(bonus)-7])
                                    else:
                                        # set bonuses also, happens to be the last bonus
                                        set_bonuses.append(bonus)
        # begin excel
        # name type slot level class stats equips set
        add_to_sheet(sheet, 0, current_piece, name)
        add_to_sheet(sheet, 1, current_piece, gear_type)
        add_to_sheet(sheet, 2, current_piece, gear_slot)
        add_to_sheet(sheet, 3, current_piece, required_level)
        add_to_sheet(sheet, 4, current_piece, required_class)
        add_to_sheet(sheet, 5, current_piece, armor)
        add_to_sheet(sheet, 6, current_piece, dps)
        add_to_sheet(sheet, 7, current_piece, agi)
        add_to_sheet(sheet, 8, current_piece, strength)
        add_to_sheet(sheet, 9, current_piece, sta)
        add_to_sheet(sheet, 10, current_piece, intellect)
        add_to_sheet(sheet, 11, current_piece, fire)
        add_to_sheet(sheet, 12, current_piece, frost)
        add_to_sheet(sheet, 13, current_piece, nature)
        add_to_sheet(sheet, 14, current_piece, arcane)
        add_to_sheet(sheet, 15, current_piece, shadow)
        for eq_index in range(len(equips)):
            add_to_sheet(sheet, 16, current_piece, str(equips[eq_index] + '\n'))
        add_to_sheet(sheet, 17, current_piece, set_name)
        for sb_index in range(len(set_bonuses)):
            add_to_sheet(sheet, 18, current_piece, str(set_bonuses[sb_index] + '\n'))

def add_to_sheet(sheet, index, cp, item):
    sheet.cell(row=cp+1, column=index+1).value = str(item)

times = []
beginning_time = time.time()
total_items = len(id_list)
current_id_index = 0
base_url = 'https://classicdb.ch/?item='
workbook = openpyxl.Workbook()
current_sheet = workbook.active
current_sheet.title = '%s' % id
current_piece = 1
for id_index in range(len(id_list)):
    starting_time = time.time()
    html = request.urlopen('%s%s' % (base_url, str(id_list[id_index])))
    add_gear_to_spreadsheet(html, current_sheet, current_piece)
    current_piece += 1
    ending_time = time.time()
    get_time_data(starting_time, beginning_time, time.time(), times)
    times.append((ending_time-starting_time))
    if ending_time-starting_time > 2:
        workbook.save('gear_list_%s.xlsx' % page_id)
        workbook.close()
        # check to see if this works, if it does then have the workbook grab the sheet again after it saves
    current_id_index += 1
workbook.save('gear_list_%s.xlsx' % page_id)
workbook.close()
print('Program Complete!')