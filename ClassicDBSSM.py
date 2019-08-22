from urllib import request
import time
import bs4
import re

gear_types = 'Plate Mail Cloth Leather Neck Finger Relic Shield Trinket hand Hand Ranged'.split()
class_types = 'Druid Hunter Mage Paladin Priest Rogue Shaman Warlock Warrior'.split()

# setup of master url
url = 'https://classicdb.ch/?items=4.3.5'
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

def add_gear_to_spreadsheet(html):
    gear_soup = bs4.BeautifulSoup(html, 'html.parser')
    master_text = gear_soup.select('.tooltip table tr td table tr td')
    for content in master_text[0].contents:
        if len(content) > 0:
            if len(content) > 1:
                # binds, stats, req level
                if 'Binds' in content:
                    # gives the binding of the item, may have to change to just bind or include the word
                    # bounds so account bound items will be able to be read as well
                    print(content)
                elif 'Requires' in content:
                    # this is the required level, TODO change to just include the number
                    print(content)
                elif 'Durability' in content:
                    # gives the durability, we do not want the durability
                    pass
                elif 'Class' in content:
                    # the word class may appear but we don't want it
                    pass
                else:
                    # stats are here TODO have a way to more accurately read the stats
                    print(content)
            else:
                # name and slot/type
                gear_type_found = False
                for item in gear_types:
                    if item in content.text:
                        try:
                            # slot
                            # type
                            # the slot will be on the top and the type will be on the bottom
                            # TODO may be faster for the program to save the str(content.text) variable and then
                            # TODO finish the processes by using the variable
                            if str(content.text).split(item)[1] == '':
                                print(str(content.text).split(item)[0])
                                print(str(content.text).split(str(content.text).split(item)[0])[1])
                            else:
                                print(str(content.text).split(item)[1])
                                print(str(content.text).split(str(content.text).split(item)[1])[0])
                            gear_type_found = True
                            break
                        except:
                            # if it's alone in the row then just get the row, most likely the slot
                            print(content.text)
                            gear_type_found = True
                if not gear_type_found:
                    class_found = False
                    for classes in class_types:
                        if classes in content.text:
                            # required class
                            print(content.text)
                            class_found = True
                            break
                    if not class_found:
                        # name
                        print(content.text)
    # if the item that we are looking at is a weapon then we need to change the index
    # that we are looking for the equip stats and the set bonuses
    if master_text[2].contents[0][::-1][0] == 'e':
        equip_index = 3
    else:
        equip_index = 2
    for content in master_text[equip_index].contents:
        if len(content) > 0:
            if type(content) is bs4.element.Tag:
                if content.text[:5] == 'Equip' or content.text[:3] == 'Use' or content.text[:3] == 'Cha':
                    # equips and uses and chance on hits
                    print(content.text)
                else:
                    if content.text[len(content.text)-1] == ')':
                        # set name
                        print(content.text[:len(content.text)-6])
                    else:
                        if content.text[0] == '(':
                            for bonus in content.text.split(': '):
                                if bonus[0] != '(':
                                    if bonus[len(bonus)-1] != '.':
                                        # set bonuses
                                        print(bonus[:len(bonus)-7])
                                    else:
                                        # set bonuses also, happens to be the last bonus
                                        print(bonus)
    print()

times = []
beginning_time = time.time()
total_items = len(id_list)
current_id_index = 0
base_url = 'https://classicdb.ch/?item='
for id in id_list:
    starting_time = time.time()
    html = request.urlopen('%s%s' % (base_url, str(id)))
    add_gear_to_spreadsheet(html)
    ending_time = time.time()
    # get_time_data(starting_time, beginning_time, ending_time, times)
    times.append((ending_time-starting_time))
    current_id_index += 1