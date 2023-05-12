from urllib.request import urlopen
import streamlit as st
import datetime
import urllib.parse
import json
import ssl
import pandas as pd


def make_clickable(url, name):
    return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(url,name)


ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(layout='wide')
st.title("Magyarország hirdetménykereső")
st.markdown("---")
st.subheader("Kereső")
inputForrasInt = st.text_input("Forrás Intézmény (vesszővel elválasztva több is megadható)",placeholder='Gyöngyöstarján, Gyöngyöspata',value='Gyöngyöstarján, Gyöngyöspata').replace(", ", ",").split(',')
print(inputForrasInt)
forrasintezmenyek = inputForrasInt
host = "https://hirdetmenyek.gov.hu/api/hirdetmenyek/reszletezo/"
uiHost = "https://hirdetmenyek.gov.hu/reszletezo/"
csatolmanyHost = "https://hirdetmenyek.gov.hu/api/csatolmany/"

hirdetmenyek = []
ids = []

progressbarIntezmeny = st.progress(0)
progressbarHirdetes = st.progress(0)

for indexIntezmeny, forrasintezmeny in enumerate(forrasintezmenyek):
    link = "https://hirdetmenyek.gov.hu/api/hirdetmenyek?order=desc&targy=&kategoria=&forrasIntezmenyNeve="+urllib.parse.quote_plus(forrasintezmeny)+"&ugyiratSzamIktatasiSzam=&telepules=&nev=&idoszak=&adottNap=&szo=&pageIndex=0&pageSize=50&sort=kifuggesztesNapja"
    jsonData = json.loads(urlopen(link).read())
    progressbarIntezmeny.progress(1/len(forrasintezmenyek)*indexIntezmeny)

    for indexHirdetes, row in enumerate(jsonData["rows"]):
        hirdetmenyek.append(json.loads(urlopen(host+str(row["id"])).read()))
        ids.append(str(row["id"]))
        progressbarHirdetes.progress(1/len(jsonData["rows"])*indexHirdetes)
    


df = pd.DataFrame(columns=["id", "idUrl", "telepules", "kifuggesztve", "lejarat", "hrsz", "ar", "terulet", "kat", "hanyad", "csat", "csatNev"])
for index, hirdetmeny in enumerate(hirdetmenyek):
    id = None
    idUrl = None
    telepules = None
    kifuggesztve = None
    lejarat = None
    hrsz = None
    ar = None
    terulet = None
    kat = None
    hanyad = None
    csat = None
    csatNev = None
    try:
        attribs = hirdetmeny["attributumok"]

        id = str(ids[index])
        idUrl = uiHost+str(ids[index])
        telepules = attribs["telepules1"]
        kifuggesztve = datetime.datetime.strptime(hirdetmeny["hirdetmenyDTO"]["kifuggesztesNapja"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d")
        lejarat = datetime.datetime.strptime(hirdetmeny["hirdetmenyDTO"]["lejaratNapja"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d")
        hrsz = attribs["helyrajzi_szam1"]
        ar = attribs["vetelar1"]
        if ar is None:
            ar = attribs["haszonber1"]
        terulet = attribs["terulet1"]
        kat = attribs["muvelesi_ag1"]
        hanyad = attribs["tulhanyad1"]
        csat = csatolmanyHost+str(hirdetmeny["csatolmanyok"][0]["id"])
        csatNev = hirdetmeny["csatolmanyok"][0]["fajlNev"]
    except KeyError as e:
        e = e
    
    newRow = pd.DataFrame({'id':id, 'idUrl':idUrl, 'telepules':telepules, 'kifuggesztve':kifuggesztve, 'lejarat':lejarat, 'hrsz':hrsz, 'ar':ar, 'terulet':terulet, 'kat':kat, 'hanyad':hanyad, 'csat':csat, "csatNev":csatNev}, index=[0])
    df = pd.concat([newRow,df.loc[:]]).reset_index(drop=True)

df['csat'] = df.apply(lambda x: make_clickable(x['csat'], x['csatNev']), axis=1)
df['id'] = df.apply(lambda x: make_clickable(x['idUrl'], x['id']), axis=1)

df.pop("idUrl")
df.pop("csatNev")

progressbarIntezmeny.empty()
progressbarHirdetes.empty()

html = st.write(df.to_html(render_links=True, escape=False), unsafe_allow_html=True)
