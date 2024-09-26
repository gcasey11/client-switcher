import random
import time

from matplotlib import pyplot as plt
import pie_charts
import web_scraper

# This recommendation program is focused on selecting clients and dependencies that have a percentage share that is furthest below 33%.

#Should these be weighted based on how low the entropy currently is? Or based on how vulnerable they are?
LANGUAGE_WEIGHT = 1
DB_WEIGHT = 1
CRYPTO_WEIGHT = 1
TEAM_WEIGHT =1
CLIENT_WEIGHT = 1

INITIAL_TOTAL_NODES = 15000
initial_dist = web_scraper.get_execution_dist()

geth_nodes = initial_dist["Geth"] * INITIAL_TOTAL_NODES
nethermind_nodes = initial_dist["Nethermind"] * INITIAL_TOTAL_NODES
besu_nodes = initial_dist["Besu"] * INITIAL_TOTAL_NODES
erigon_nodes = initial_dist["Erigon"] * INITIAL_TOTAL_NODES

initial_consensus_dist = web_scraper.get_consensus_dist()
prysm_nodes = initial_consensus_dist["Prysm"] * INITIAL_TOTAL_NODES
lighthouse_nodes = initial_consensus_dist["Lighthouse"] * INITIAL_TOTAL_NODES
teku_nodes = initial_consensus_dist["Teku"] * INITIAL_TOTAL_NODES
nimbus_nodes = initial_consensus_dist["Nimbus"] * INITIAL_TOTAL_NODES
lodestar_nodes = initial_consensus_dist["Lodestar"] * INITIAL_TOTAL_NODES

geth = {'name': 'geth', 'distribution': geth_nodes, 'language': 'Go', 'db': 'LevelDB', 'crypto': 'Go-Default-Library', 'team': 'Go-Ethereum'}
nethermind = {'name': 'nethermind', 'distribution': nethermind_nodes, 'language': 'C#', 'db': 'RocksDB', 'crypto': 'BouncyCastle', 'team': 'Nethermind'}
besu = {'name': 'besu', 'distribution': besu_nodes, 'language': 'Java', 'db': 'RocksDB', 'crypto': 'BouncyCastle', 'team': 'Consensys'}
erigon = {'name': 'erigon', 'distribution': erigon_nodes, 'language': 'Go', 'db': 'SQLite', 'crypto': 'Go-Default-Library', 'team': 'Erigon'}

prysm = {'name': 'prysm', 'distribution': prysm_nodes, 'language': 'Go', 'db': 'BoltDB', 'crypto': 'Go-Default-Library', 'team': 'Prysmatic-Labs'}
lighthouse = {'name': 'lighthouse', 'distribution': lighthouse_nodes, 'language': 'Rust', 'db': 'LevelDB', 'crypto': 'Rust-Default-Library', 'team': 'SigmaPrime'}
teku = {'name': 'teku', 'distribution': teku_nodes, 'language': 'Java', 'db': 'LevelDB', 'crypto': 'BouncyCastle', 'team': 'Consensys'}
nimbus = {'name': 'nimbus', 'distribution': nimbus_nodes, 'language': 'Nim', 'db': 'SQLite', 'crypto': 'Nim-Default-Library', 'team': 'Status'}
lodestar = {'name': 'lodestar', 'distribution': lodestar_nodes, 'language': 'TypeScript', 'db': 'LevelDB', 'crypto': 'bcrypt', 'team': 'Chainsafe'}

execution_clients = {'geth': geth, 'nethermind': nethermind, 'besu': besu, 'erigon': erigon}
consensus_clients = {'prysm': prysm, 'lighthouse': lighthouse, 'teku': teku, 'nimbus': nimbus, 'lodestar': lodestar}

execution_consensus_pairs = [('geth', 'prysm'), ('geth', 'lighthouse'), ('geth', 'teku'), ('geth', 'nimbus'), ('geth', 'lodestar'), 
                             ('nethermind', 'prysm'), ('nethermind', 'lighthouse'), ('nethermind', 'teku'), ('nethermind', 'nimbus'), 
                             ('nethermind', 'lodestar'), ('besu', 'prysm'), ('besu', 'lighthouse'), 
                             ('erigon', 'prysm'), ('erigon', 'lighthouse')]

attack_surface_scores = {}

def get_distance(name, distribution):
    total_nodes = 0
    total_types = 0
    for type in distribution.keys():
        total_nodes+=distribution[type]
        total_types+=1

    fraction_of_dist = distribution[name]/total_nodes

    if total_types < 3:
        distance_score = (1/total_types) - fraction_of_dist
    else:
        distance_score = 1/3 - fraction_of_dist

    return distance_score

def get_attack_surface_score(execution_client, consensus_client):
    common_dependencies = 1
    for client_property in execution_client.keys():
        if client_property not in ["name", "distribution"]:
            if execution_client[client_property] == consensus_client[client_property]:
                common_dependencies+=1
        else:
            continue
    attack_surface = 1/common_dependencies * 0.1
    return attack_surface

def create_distributions(clients):
    client_dist = {}
    language_dist = {}
    db_dist = {}
    crypto_dist = {}
    team_dist = {}
    for client in clients.values():
        if client['name'] in client_dist.keys():
            client_dist[client['name']] += client['distribution']
        else:
            client_dist[client['name']] = client['distribution']
    
        if client['language'] in language_dist.keys():
            language_dist[client['language']] += client['distribution']
        else:
            language_dist[client['language']] = client['distribution']

        if client['db'] in db_dist.keys():
            db_dist[client['db']] += client['distribution']
        else:
            db_dist[client['db']] = client['distribution']

        if client['crypto'] in crypto_dist.keys():
            crypto_dist[client['crypto']] += client['distribution']
        else:
            crypto_dist[client['crypto']] = client['distribution']
        
        if client['team'] in team_dist.keys():
            team_dist[client['team']] += client['distribution']
        else:
            team_dist[client['team']] = client['distribution']
    
    return client_dist, language_dist, db_dist, crypto_dist, team_dist

def evaluate(name_of_client, clients):

    client_dist, language_dist, db_dist, crypto_dist, team_dist = create_distributions(clients)

    total_distance = get_distance(clients[name_of_client]["name"], client_dist) + get_distance(clients[name_of_client]["language"], language_dist) + get_distance(clients[name_of_client]["db"], db_dist) + get_distance(clients[name_of_client]["crypto"], crypto_dist) + get_distance(clients[name_of_client]["team"], team_dist)

    return total_distance


def recommendation():
    distances = {}
    for execution_client in execution_clients.keys():
        for consensus_client in consensus_clients.keys():
            distances[execution_client, consensus_client] = evaluate(execution_client, execution_clients) + evaluate(consensus_client, consensus_clients) 

    sorted_distances = dict(sorted(distances.items(), key=lambda item: item[1], reverse=True))

    # If the difference in improvement between the first and second option is equal, decide based on attack surface instead
    i = 1
    equal_clients = {list(sorted_distances.keys())[0] : get_attack_surface_score(execution_clients[list(sorted_distances.keys())[0][0]], consensus_clients[list(sorted_distances.keys())[0][1]])}
    while i < len(list(sorted_distances.keys())):
        if sorted_distances[list(sorted_distances.keys())[i]] == sorted_distances[list(sorted_distances.keys())[i-1]]:
            equal_clients[list(sorted_distances.keys())[i]] = get_attack_surface_score(execution_clients[list(sorted_distances.keys())[i][0]], consensus_clients[list(sorted_distances.keys())[i][1]])
        else:
            break
        i+=1

    if len(equal_clients.keys()) > 1:
        with open("diff.txt", "a") as file:
            file.write("Attack Surface" + "\n")
        return min(equal_clients, key=equal_clients.get)
    
    with open("diff.txt", "a") as file:
        file.write("Distribution" + "\n")
    
    return max(distances, key=distances.get)

# start = time.time()

# i = 0
# while i <= 7500:
#     if i == 0:
#         total = 0
#         for client in execution_clients:
#             total += execution_clients[client]['distribution']

#         print("Total is", total)

#     random_choice = random.choices(execution_consensus_pairs)[0]

#     value = random.randint(0,100)
#     if value > 1:
#         execution_clients[random_choice[0]]['distribution'] -= 1
#         consensus_clients[random_choice[1]]['distribution'] -= 1


#     recommended = recommendation()
#     execution_clients[recommended[0]]['distribution'] += 1
#     consensus_clients[recommended[1]]['distribution'] += 1

#     if i == 7500:
#         client_dist, language_dist, db_dist, crypto_dist, team_dist = create_distributions(execution_clients)
#         consensus_client_dist, consensus_language_dist, consensus_db_dist, consensus_crypto_dist, consensus_team_dist = create_distributions(consensus_clients)
        
#         plt.figure(0)
#         plt.subplot(211)
#         pie_charts.create_pie(list(client_dist.values()), list(client_dist.keys()))
#         plt.subplot(212)
#         pie_charts.create_pie(list(consensus_client_dist.values()), list(consensus_client_dist.keys()))

#         plt.figure(1)
#         plt.subplot(211)
#         pie_charts.create_pie(list(language_dist.values()), list(language_dist.keys()))
#         plt.subplot(212)
#         pie_charts.create_pie(list(consensus_language_dist.values()), list(consensus_language_dist.keys()))

#         plt.figure(2)
#         plt.subplot(211)
#         pie_charts.create_pie(list(db_dist.values()), list(db_dist.keys()))
#         plt.subplot(212)
#         pie_charts.create_pie(list(consensus_db_dist.values()), list(consensus_db_dist.keys()))

#         plt.figure(3)
#         plt.subplot(211)
#         pie_charts.create_pie(list(crypto_dist.values()), list(crypto_dist.keys()))
#         plt.subplot(212)
#         pie_charts.create_pie(list(consensus_crypto_dist.values()), list(consensus_crypto_dist.keys()))

#         plt.figure(4)
#         plt.subplot(211)
#         pie_charts.create_pie(list(team_dist.values()), list(team_dist.keys()))
#         plt.subplot(212)
#         pie_charts.create_pie(list(consensus_team_dist.values()), list(consensus_team_dist.keys()))

#         plt.show()

#         total = 0
#         for client in execution_clients:
#             total += execution_clients[client]['distribution']

#         print("Total is", total)

#     i+=1

# end = time.time()

# print("Time", str(end-start))