
# Function to parse the string and return structured data
def parse_vote_string(vote_string):
    extracted_data = vote_string.split('!')[1]
    data_list = [int(num) for num in extracted_data.split(',')]
    #print(data_list)
    return data_list

# Function to update the totals
def update_totals(data_list, totals):
    index = 0
    for i, candidate in enumerate(candidates):
        if candidate not in totals:
            totals[candidate] = 0
        for _ in parties[i]:
            totals[candidate] += data_list[index]
            index += 1

def update(qrstring, totals):
    data_list = parse_vote_string(qrstring)
    update_totals(data_list, totals)

# Candidate names and their respective parties
candidates = [
    "NICOLAS MADURO",
    "LUIS MARTINEZ",
    "JAVIER BERTUCCI",
    "JOSE BRITO",
    "ANTONIO ECARRI",
    "CLAUDIO FERMIN",
    "DANIEL CEBALLOS",
    "EDMUNDO GONZALEZ",
    "ENRIQUE MARQUEZ",
    "BENJAMIN RAUSSEO"
]

parties = [
    ["PSUV", "PCV", "TUPAMARO", "PPT", "MSV", "PODEMOS", "MEP", "APC", "ORA", "UPV", "EV", "PVV","PFV"],
    ["AD", "COPEI","MR","BR","DOP","UNE"],
    ["ELCAMBIO"],
    ["PV", "VU", "UVV", "MPJ"],
    ["AP","MOVEV","CMC","FV","ALANZA DEL LAPIZ","MIN UNIDAD"],
    ["SPV"],
    ["VPA","AREPA"],
    ["UNTC","MPV","MUD"],
    ["IND"],
    ["FUERZANUEVA"]
]

