import pandas as pd

def databaseExists(dbName, crs):
    dbName = dbName.lower()
    crs.execute("SHOW DATABASES;")
    for x in crs:
        if x[0] == dbName:
            return True
    return False

def create_table(path, tb_name, htypes, pkeys, fkeys, crs, db_name):

    file = pd.read_csv(path, encoding="windows-1251")
    headers = [header for header in file]
    if len(htypes) != len(headers):
        return print("num of headers is not the same as num of header types") # I know it's weird but it works

    # Craft command to create table
    crt_tbl = ""
    for i in range(len(headers)):
        crt_tbl += headers[i] + " " + htypes[i] + ", "
    crt_tbl = crt_tbl[:len(crt_tbl) - 2]    # Slice to remove last comma
    if len(pkeys) > 0:
        pkeys = ", ".join(pkeys)
        pkeys = f"PRIMARY KEY ({pkeys})"
        crt_tbl += ", " + pkeys
    if len(fkeys) > 0:
        fkeyquery = ""
        for fkey in fkeys:
            fkeyquery += f"FOREIGN KEY {fkey[0]} REFERENCES {fkey[1]}, "
        crt_tbl += ", " + fkeyquery[:len(fkeyquery) - 2]
    crt_tbl = f"({crt_tbl})"

    crs.execute("CREATE TABLE " + db_name + "." + tb_name + " " + crt_tbl)

    # Insert data into table
    tbl = db_name + "." + tb_name
    for i in range(len(file)):  # Rows
        values = ""
        for header in headers:   # Columns
            value = file[header][i]

            hindex = headers.index(header)
            if "int" not in htypes[hindex]:  # Will check if column stores int
                values += f'"{value}", '
            else:
                values += f'{value}, '
        values = f'({values[:len(values) - 2]})' # Slice out the comma for the last value and put values in brackets
        crs.execute("INSERT INTO " + tbl + " VALUES " + values)

def create_database(crs, db_name):
    crs.execute("CREATE DATABASE " + db_name)

    # Data needed to create tables
    paths = ['valorant_db_data/' + fname for fname in ['agents.csv', 'maps.csv', 'roles.csv', 'comps.csv', 'fits.csv', 'utilities.csv']]
    tb_names = ["agents", "maps", "roles", "comps", "fits", "utilities"]
    htypes = [
        ["varchar(20)", "varchar(20)"],
        ["varchar(20)", "varchar(20)"],
        ["varchar(20)", "varchar(1000)"],
        ["varchar(20)", "varchar(20)"],
        ["varchar(20)", "varchar(20)"],
        ["varchar(20)", "varchar(20)"],
    ]
    pkeys = [
        ["agent_name"],
        ["map_name"],
        ["role_name"],
        ["agent_name", "map_name"],
        ["agent_name", "role_name"],
        ["utility_name", "agent_name"]
    ]
    fkeys = [  # These are in lists so the code is more readable
        [],
        [],
        [],
        [
            ["(agent_name)", "agents(agent_name)"],
            ["(map_name)", "maps(map_name)"]
        ],
        [
            ["(agent_name)", "agents(agent_name)"],
            ["(role_name)", "roles(role_name)"]
        ],
        [
            ["(agent_name)", "agents(agent_name)"]
        ]
    ]

    for i in range(6):
        create_table(paths[i], tb_names[i], htypes[i], pkeys[i], fkeys[i], crs, db_name)

    # Create views
    crs.execute("USE Valorant")

    crs.execute("CREATE VIEW AgentRCMap AS SELECT comps.agent_name, comps.map_name, agents.type, maps.gimic FROM Valorant.comps, " +
                "Valorant.agents, Valorant.maps WHERE comps.agent_name = agents.agent_name AND comps.map_name = maps.map_name;")

    crs.execute("CREATE VIEW AgentRFit AS SELECT agents.agent_name, agents.type, roles.role_name, roles.description FROM " +
                "Valorant.agents, Valorant.roles, Valorant.fits where agents.agent_name = fits.agent_name AND roles.role_name = fits.role_name;")

    crs.execute("CREATE VIEW AgentUCount AS SELECT agent_name, COUNT(utility_name) as util_count FROM Valorant.utilities GROUP BY agent_name;")

    print("Database Created\n\n\n\n\n\n\n")