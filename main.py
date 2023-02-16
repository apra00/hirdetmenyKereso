import requests
import streamlit as st
import urllib
import base64
import pandas as pd




site = 'https://hirdetmenyek.magyarorszag.hu'


def displayPDF(file):
    # Opening file from file path. this is used to open the file from a website rather than local
    with urllib.request.urlopen(file) as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def extractIds(url):
    ids = []
    first = False
    page = lines(url)
    for sor in page:
        if "talalatilista" in sor:
            first = True
        if first:
            if "hirdetmeny" in sor:
                ids.append(site+"/hirdetmeny?id="+(sor.split('"')[1]).split('=')[1])
    #print(ids)
    return ids


def lines(url):
    page = requests.get(url)
    page = page.text.split("\n")
    return page



def findId(link):
    id = link.split("?id=")[1]
    return id


def findKozzetetel(sorok):
    next = False
    for sor in sorok:
        if next:
            kozzetetel = sor.split("</p>")[0].strip("\t")
            return kozzetetel
        if "portálon való közzététel" in sor:
            next = True


def findHatarido(sorok):
    next = False
    for sor in sorok:
        if next:
            hatarido = sor.split("</p>")[0].strip("\t")
            return hatarido
        if "határidő utolsó napja" in sor:
            next = True


def findHrsz(sorok):
    for sor in sorok:
        if "<strong>Helyrajzi szám:</strong>" in sor:
            hrsz = sor.split("<strong>Helyrajzi szám:</strong>")[1].split("</p>")[0]
            return hrsz


def findAr(sorok):
    for sor in sorok:
        if "<strong>Vételár:</strong>" in sor:
            ar = sor.split("<strong>Vételár:</strong>")[1].split("</p>")[0]
            return ar


def findTerulet(sorok):
    for sor in sorok:
        if "<strong>Terület:</strong>" in sor:
            terulet = sor.split("<strong>Terület:</strong>")[1].split("</p>")[0]
            return terulet


def findKat(sorok):
    for sor in sorok:
        if "Művelési ág:" in sor:
            kat = sor.split("<strong>Művelési ág:</strong>")[1].split("</p>")[0]
            return kat


def findHanyad(sorok):
    for sor in sorok:
        if "<strong>Tulajdoni hányad:</strong>" in sor:
            hanyad = sor.split("<strong>Tulajdoni hányad:</strong>")[1].split("</p>")[0]
            return hanyad


def findCsat(sorok):
    next = False
    for sor in sorok:
        if next:
            link = sor.split('<p><a href="')[1].split('">')[0]
            link = link.split("csatolmany/")[1]
            return link
        if "<h3>Csatolmányok:</h3>" in sor:
            next = True



data = [["teszt1","teszt2","teszt3","teszt4","teszt5","teszt6","teszt7","teszt8","teszt9",]]
df = pd.DataFrame(data,columns=["hirdetesId","kozzetetel","hatarido","hrsz","ar","terulet","kat","hanyad","csat"])

st.set_page_config(layout='wide')
st.title("Magyarország hirdetménykereső")
st.markdown("---")
st.subheader("Kereső")
inputForrasInt = st.text_input("Forrás Intézmény",placeholder='Gyöngyöstarjáni Közös Önkormányzati Hivatal',value='Gyöngyöstarjáni Közös Önkormányzati Hivatal')
weblink = "https://hirdetmenyek.magyarorszag.hu/?FORRASINTEZMENYNEVE="+inputForrasInt+'&IDOSZAK=1&KATEGORIA=&SZO=&OLDALANKENTITALALAT=100&RENDEZES=0&x=14&y=9'
links = extractIds(weblink)
progressbar = st.progress(0)
counter = 0
for link in links:
    counter += 1
    sorok = lines(link)

    hirdetesId = f'<a target="_blank" href="' + site + "/hirdetmeny?id=" + findId(link) + '">Megnyitás</a>'
    kozzetetel = findKozzetetel(sorok)
    hatarido = findHatarido(sorok)
    hrsz = findHrsz(sorok)
    ar = findAr(sorok)
    terulet = findTerulet(sorok)
    kat = findKat(sorok)
    hanyad = findHanyad(sorok)
    csat = f'<a target="_blank" href="' + site + "/csatolmany/" + findCsat(sorok) + '">Csatolmány</a>'

    #print(hirdetesId,kozzetetel,hatarido,hrsz,ar,terulet,kat,hanyad,csat)

    #df = df.append(dict(zip(df.columns,[hirdetesId,kozzetetel,hatarido,hrsz,ar,terulet,kat,hanyad,csat])), ignore_index = True)
    #df = pd.concat([df,pd.Series([hirdetesId,kozzetetel,hatarido,hrsz,ar,terulet,kat,hanyad,csat])])
    df.loc[len(df)] = [hirdetesId,kozzetetel,hatarido,hrsz,ar,terulet,kat,hanyad,csat]
    progressbar.progress(1/len(links)*counter)
df = df.iloc[1:]
progressbar.empty()
eredmenyTabla = st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
