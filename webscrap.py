from bs4 import BeautifulSoup
import requests as re
import pandas as pd

def make_soup():
    html = re.get(url).text
    global soup 
    soup = BeautifulSoup(html, 'html.parser')

def pagination():
    global url
    url = next_page
    make_soup()

def n_pages():
    global pages
    pages = int(soup.find('li', class_='andes-pagination__page-count').text.replace('de', '').strip()) 
     
#Get the url from portlainmoboliario.com 
url = 'https://www.portalinmobiliario.com/venta/casa/vitacura-metropolitana'

make_soup()
n_pages()

#Creating DataFrame
output = pd.DataFrame(columns=['Precio', 'M2_utiles', 'Dormitorios', 'Direccion', 'Link'])

for i in range(0, pages):
    estate = soup.find_all('li', class_='ui-search-layout__item shops__layout-item')
    try:
        next_page = soup.find('a', {'title' : 'Siguiente'}).attrs['href']
    except:
        break
    
    for soup in estate:
        property = []
        try:
            if soup.find('label', class_='ui-search-styled-label ui-search-item__highlight-label__text').text == 'PROYECTO':
                continue
        except:
            pass
        property.append(soup.find('span', class_='price-tag-text-sr-only').text) #Price
        try:
            property.append(soup.find_all('li', class_='ui-search-card-attributes__attribute')[0].text) #Square meters
        except:
            property.append(0) #No info   
        try:
            property.append(soup.find_all('li', class_='ui-search-card-attributes__attribute')[1].text) #Bedrooms
        except:
            property.append(0) #No info about bedroom
        property.append(soup.find('p', class_='ui-search-item__group__element ui-search-item__location shops__items-group-details').text) #Adress
        property.append(soup.find('a', class_='ui-search-result__content-wrapper ui-search-link').attrs['href']) #Url
        output.loc[len(output)] = property #Insert data to DataFrame

    pagination()    

#Cleaning Data
output['Precio'] = output['Precio'].replace('undefined', 'UF', regex=True).replace(' con ', '.', regex=True).replace('centavos', '', regex=True).replace('pesos', 'clp', regex=True)
output['M2_utiles'] = output['M2_utiles'].replace('útiles', '', regex=True)
output['Dormitorios'] = output['Dormitorios'].replace('dormitorios', '', regex=True).replace('dormitorio', '', regex=True)
output['Dormitorios'] = pd.to_numeric(output['Dormitorios'])

price_fix = pd.DataFrame(columns=['amount', 'type'])

for price in output['Precio']:
    fix = []
    if 'UF' in price:
        fix.append(price.replace(' UF', ''))
        fix.append('UF')
    elif 'clp' in price:
        fix.append(price.replace(' clp', ''))
        fix.append('CLP')
    try:
        price_fix.loc[len(price_fix)] = fix
    except:
        continue

output['Precio'] = pd.to_numeric(price_fix['amount'])
output.insert(loc=1, column='Formato', value=price_fix['type'])
        
#Convert to excel 
output.to_excel('Lista de inmuebles.xlsx')