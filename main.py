import database_creator as db_bld  # Check this file to adjust database connection
import mysql.connector

# Functions
# Trivial
def cap_first(word):  # Capitalizes first letter of a word and makes rest lower
    return str(word[:1]).capitalize() + str(word[1:].lower())

def no_result():
    input("No results, Press Enter to return to main menu.")
    main_menu()

# Menus
# Main Menu
def main_menu():
    print("\n Main Menu\n___________\n")
    user = input("a for Agents \nm for Maps \nr for Roles \nu for Utilities\nChoice: ")
    if user in ['a', 'm', 'r', 'u']:
        if user == 'a':
            # Agent names
            crs.execute("SELECT agent_name FROM Valorant.agents")
            agent_list = [row[0] for row in crs.fetchall()]

            # Agent count
            crs.execute("SELECT COUNT(agent_name) FROM Valorant.agents")
            for row in crs.fetchall():
                count = row[0]

            agents_menu(agent_list, count)
        elif user == 'm':
            crs.execute("SELECT * FROM Valorant.maps")
            map_list = [[row[0], row[1]] for row in crs.fetchall()]
            maps_menu(map_list)
        elif user == 'r':
            crs.execute("SELECT role_name, COUNT(agent_name), description FROM Valorant.agentrfit " +
                        f"GROUP BY role_name;")
            role_list = [[cap_first(row[0]), row[1], row[2]] for row in crs.fetchall()]
            roles_menu(role_list)
        else:
            crs.execute(f"SELECT utility_name FROM Valorant.utilities GROUP BY utility_name;")
            utility_list = [cap_first(row[0]) for row in crs.fetchall()]
            utilities_menu(utility_list)

    else:
        print("\n\n\n\n")
        main_menu()

# Agents
def agents_menu(agent_list, count):
    print(f"\n\n Agents (count = {count})\n_____________________")
    # Clean up agent names
    agent_list = [cap_first(agent) for agent in agent_list]
    for agent in agent_list:
        print(agent)
    agent = -99  # Just so the while loop works first time
    while agent not in agent_list:
        agent = cap_first(input("Choose an agent: "))

    # Fetch agent type
    crs.execute(f"SELECT type FROM Valorant.agents WHERE agent_name = '{agent}'")
    for row in crs.fetchall():
        type = cap_first(row[0])
    user = -99
    while user not in ["b", "f", "u"]:
        print(f"\nAgent: {agent}, Type: {type}")
        user = input("b for Best played on \nf for Fits role \nu for Utilities\nChoice: ")

    if user == "b":
        crs.execute(f"SELECT map_name, gimic FROM Valorant.agentrcmap WHERE agent_name = '{agent}'")
        map_list = [[row[0], row[1]] for row in crs.fetchall()]
        if map_list == []:  # Empty results
            no_result()
        else:
            maps_menu(map_list)
    elif user == "f":
        crs.execute("SELECT role_name, COUNT(agent_name), description FROM Valorant.agentrfit" +
                   f" WHERE agent_name = '{agent}' GROUP BY role_name;")
        role_list = [[cap_first(row[0]), row[1], row[2]] for row in crs.fetchall()]
        if role_list == []:
            no_result()
        else:
            roles_menu(role_list)
    else:
        crs.execute(f"SELECT utility_name FROM Valorant.utilities WHERE agent_name = '{agent}'")
        utility_list = [cap_first(row[0]) for row in crs.fetchall()]
        if utility_list == []:
            no_result()
        else:
            utilities_menu(utility_list)

# Maps
def maps_menu(map_list):  # Map_list = name and gimic
    print(f"\n\n Maps\n______")
    # Clean up map names
    map_list = [[cap_first(map[0]), cap_first(map[1])] for map in map_list]
    for map in map_list:
        print(f"Map: {map[0]}, Gimic: {map[1]}")
    map = -99
    while map not in [map[0] for map in map_list]:
        map = cap_first(input("Choose a map to see current meta comp: "))

    # Fetch suitable comp for map
    crs.execute(f"SELECT agent_name FROM Valorant.agentrcmap WHERE map_name = '{map}'")
    agent_list = [row[0] for row in crs.fetchall()]
    agents_menu(agent_list, 5)

# Roles
def roles_menu(role_list):  # role_list = [[role_name, count], ...]
    print(f"\n\n Roles\n_______")
    for row in role_list:
        crs.execute(f"SELECT COUNT(agent_name) FROM Valorant.agentrfit WHERE role_name = '{row[0]}' GROUP BY role_name;")
        agent_count = [row[0] for row in crs.fetchall()][0]
        print(f"Role: {row[0]}, Agent count: {agent_count}")
    role = -99
    while role not in [role[0] for role in role_list]:
        role = cap_first(input("Choose a role: "))
    crs.execute(f"SELECT agent_name, description FROM Valorant.agentrfit WHERE role_name = '{role}'")
    results = crs.fetchall()
    agent_list = [cap_first(row[0]) for row in results]
    for row in results:
        desc = row[1]
        break

    # Print description
    print(f"\nDescription:")
    l_count = 0
    for letter in desc:   # To print neatly
        if letter != " ":
            print(letter, end="")
            l_count += 1
        else:
            if l_count >= 60:
                print()
                l_count = 0
            else:
                print(letter, end="")
                l_count += 1

    crs.execute(f"SELECT COUNT(agent_name) FROM Valorant.fits WHERE role_name = '{role}'")
    for row in crs.fetchall():
        count = row[0]
    # Go to agents menu
    agents_menu(agent_list, count)


# Utilities
def utilities_menu(utility_list):
    print(f"\n\n Utilities\n___________")
    utility_list = [cap_first(utility) for utility in utility_list]
    for utility in utility_list:
        print(utility)
    user = -99
    while user not in ["c", "l"]:
        user = input("\nc to choose a utility\nl to learn general utility facts\nChoice: ")
    if user == "c":
        utility = -99
        while utility not in utility_list:
            utility = cap_first(input("Choose utility: "))
        # Get agents
        crs.execute(f"SELECT agent_name FROM Valorant.utilities WHERE utility_name = '{utility}'")
        agent_list = [row[0] for row in crs.fetchall()]

        # Get agent count
        crs.execute(f"SELECT COUNT(agent_name) FROM Valorant.utilities WHERE utility_name = '{utility}'")
        for row in crs.fetchall():
            count = row[0]

        agents_menu(agent_list, count)
    else:
        crs.execute("SELECT AVG(util_count) FROM Valorant.agentucount;")
        for row in crs.fetchall():
            avg_util = round(float(row[0]))

        crs.execute("SELECT MAX(util_count) FROM valorant.agentucount;")
        for row in crs.fetchall(): max = row[0]
        crs.execute("SELECT MIN(util_count) FROM valorant.agentucount;")
        for row in crs.fetchall(): min = row[0]

        crs.execute(f"SELECT agent_name FROM Valorant.agentucount WHERE util_count = {max};")
        max_list = [cap_first(row[0]) for row in crs.fetchall()]
        crs.execute(f"SELECT agent_name FROM Valorant.agentucount WHERE util_count = {min};")
        min_list = [cap_first(row[0]) for row in crs.fetchall()]

        print(f"Agent(s) with least utilities ({min}): {', '.join(min_list)}",
              f"Agent(s) with most utilities ({max}): {', '.join(max_list)}",
              f"Average agent utility count: {avg_util}\n", sep="\n")
        input("Press Enter to return to main menu.")
        main_menu()

# Connection to database
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root'
)
crs = mydb.cursor(buffered=True)

# Create database if it doesn't exist
if not db_bld.databaseExists("Valorant", crs):
    db_bld.create_database(crs, "Valorant")
    mydb.commit()

# Start interface
main_menu()