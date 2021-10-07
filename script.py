from siibra_explorer_toolsuite import run
import siibra

atlas=siibra.atlases['human']
space=siibra.spaces['mni 152']
short=siibra.parcellations['short bundle']
long=siibra.parcellations['long bundle']

def main():
    arr=[]
    for parc in [short, long]:
        for region in parc.regiontree:
            if len(region.labels) > 0:
                arr.append({
                    'name': region.name,
                    'url': run(atlas, space, parc, region)
                })
    with open('./output.json', 'w') as fp:
        import json
        json.dump(arr, fp)
    with open('./output.txt', 'w') as fp:
        for item in arr:
            fp.write(item['name'])
            fp.write('\n')
            fp.write(item['url'])
            fp.write('\n')
            fp.write('\n')
        

if __name__ == "__main__":
    main()