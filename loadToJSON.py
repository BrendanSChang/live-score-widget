import requests
import pprint
import xml.etree.ElementTree as ET

BASE_URL="http://api.core.optasports.com/volleyball/"
USER="frmedia"
AUTH="8277e0910d750195b448797616e091ad"

def loadXML(url, payload):
    resp = requests.get(url, params=payload)
    return ET.fromstring(resp.content)


def getMatches(sid):
    payload = {"username": USER, "authkey": AUTH}
    payload["type"] = "season"
    payload["id"] = sid
    url = BASE_URL + "get_matches"
    root = loadXML(url, payload)
    data = []
    for comp in root:
        if (comp.tag == 'competition'):
            for season in comp:
                for match in season.iter():
                    # TODO: Currently only works for completed matches.
                    if (match.tag == 'match' and
                        match.attrib.get("status") == 'Played'):

                        a = match.get("team_A_name")
                        b = match.get("team_B_name")

                        winner = match.get("winner")
                        sets_played = \
                            int(match.get("fs_A")) + int(match.get("fs_B"))
                        a_scores = []
                        b_scores = []
                        for i in range(1, sets_played + 1):
                            prefix = "p%ds" % i
                            a_scores.append(match.get(prefix + "_A"))
                            b_scores.append(match.get(prefix + "_B"))
                        
                        data.append({
                            "team_A": a,
                            "team_B": b,
                            "winner": winner,
                            "team_A_scores": a_scores,
                            "team_B_scores": b_scores
                        })

    return data


def getSeasons(authorized=True):
    payload = {"username": USER, "authkey": AUTH}
    if (authorized):
        payload["authorized"] = "yes"
    url = BASE_URL + "get_seasons"
    comps = loadXML(url, payload)
    data = {}
    for comp in comps:
        if (comp.tag == 'competition'):
            c = comp.attrib
            data[c.get("name")] = {}
            for season in comp:
                s = season.attrib
                matches = getMatches(s.get("season_id"))
                data[c.get("name")][s.get("name")] = matches

    return data


def writeToJSON(
        data,
        path="C:\\Users\\Brendan\\Documents\\School\\2015-2016\\Volleyverse\\"):
    f = open(path + "output_minimal.json", "w+")
    f.write(str(data))
    f.close()

    f = open(path + "output_pretty.json", "w+")
    pp = pprint.PrettyPrinter(indent=3, stream=f)
    pp.pprint(data)
    f.close()


if __name__ == '__main__':
    writeToJSON(getSeasons())